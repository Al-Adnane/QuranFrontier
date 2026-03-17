# Phase 3 Embedding Service - Memory & Throughput Optimization Guide

## Objective
Scale the embedding service from **120 vec/sec to 250+ vec/sec** by implementing:
1. Horizontal Pod Autoscaling (HPA) with CPU and queue-depth triggers
2. Neo4j batch operation optimization (50 → 100 verses)
3. Memory-optimized streaming embedding generation
4. Comprehensive monitoring and alerting

## Current Status
- **Baseline throughput**: 120 vectors/second
- **Current workers**: 2 replicas
- **Neo4j batch size**: 50 verses/transaction
- **Neo4j pool timeout**: 30 seconds
- **Memory ceiling**: Frequently hitting 1GB limit

## Target Metrics
- **Throughput**: 250+ vectors/second
- **Worker replicas**: 4-6 (scaling from 2)
- **Neo4j memory**: < 80% utilization
- **Queue depth**: < 500 items (no overflow)
- **GC pauses**: < 100ms per collection

---

## Phase 1: Deploy HPA Configuration

### 1.1 Apply HPA for Embedding Workers

```bash
kubectl apply -f kubernetes/09-embedding-worker-hpa.yaml
```

This creates:
- **HorizontalPodAutoscaler**: Scales workers 2-6 replicas
  - CPU trigger: > 70%
  - Queue depth trigger: > 500 items
- **Service**: embedding-worker-service on port 8000 for metrics
- **PodDisruptionBudget**: Ensures min 1 available during scaling

### 1.2 Verify HPA Status

```bash
# Check HPA configuration
kubectl get hpa -n quran-system

# Watch HPA events
kubectl describe hpa embedding-worker-hpa -n quran-system

# Monitor current replicas
kubectl get pods -n quran-system -l app=worker -w
```

Expected behavior:
- Initial state: 2 replicas
- Monitor for 2-3 minutes to establish baseline metrics
- When queue depth > 500 OR CPU > 70%, scale up to 4, then 6 max

---

## Phase 2: Update Worker Deployment with Memory Optimizations

### 2.1 Review Optimizations

The updated deployment (`08-worker-deployment-optimized.yaml`) includes:

#### Environment Variables for Memory Optimization:
```yaml
EMBEDDING_STREAMING_MODE: "true"           # Stream vectors instead of batching
EMBEDDING_GC_INTERVAL: "1000"              # Force GC every 1000 vectors
EMBEDDING_MEMORY_MAPPED_STORAGE: "true"    # Use memory-mapped files
NEO4J_BATCH_SIZE: "100"                    # Increased from 50
NEO4J_CONNECTION_POOL_TIMEOUT: "45"        # Increased from 30s
NEO4J_QUERY_CACHE_ENABLED: "true"          # Enable query caching
```

#### Python GC Tuning:
```yaml
PYTHONGC_THRESHOLD0: "500"  # Trigger collection at 500 objects
PYTHONGC_THRESHOLD1: "10"   # Tuned for embedding workloads
PYTHONGC_THRESHOLD2: "10"
```

#### Resource Allocation:
```yaml
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 1Gi  # Same as before, optimizations prevent hitting limit
```

### 2.2 Rolling Update Workers

```bash
# Option A: Update in-place (recommended)
kubectl set image deployment/worker \
  worker=quran-frontier-worker:latest-optimized \
  -n quran-system

# Option B: Apply new deployment
kubectl apply -f kubernetes/08-worker-deployment-optimized.yaml

# Monitor rollout
kubectl rollout status deployment/worker -n quran-system -w
```

**Rollout strategy**:
- maxSurge: 2 (allow 2 extra pods during update)
- maxUnavailable: 0 (zero-downtime)
- Expected time: 2-3 minutes for 2 pod replacement

---

## Phase 3: Deploy Memory Optimization Module

### 3.1 Install Memory Optimization Library

The module is located at: `/quran-core/src/embedding/memory_optimization.py`

#### Components:

**StreamingEmbeddingGenerator**
```python
generator = StreamingEmbeddingGenerator(
    batch_size=100,
    gc_interval=1000,
    neo4j_batch_size=100,
    connection_pool_timeout=45
)

# Stream embeddings without loading full batch into memory
for vec_data in generator.stream_embeddings(texts, embedding_func):
    store_vector(vec_data['vector'])
    # GC automatically triggered every 1000 vectors
```

**MemoryMappedVectorStore**
```python
store = MemoryMappedVectorStore(
    filepath='/tmp/embedding_vectors.mmap',
    max_vectors=500000,
    dim=768
)

# Add vectors without memory bloat
store.add_vector(embedding)

# Retrieve batch efficiently
batch = store.get_batch(start_idx=0, size=100)
```

**Neo4jBatchOptimizer**
```python
optimizer = Neo4jBatchOptimizer(uri, user, password)

# Execute 100-vector batches with query cache
with optimizer.batch_transaction(session) as tx:
    tx.run(optimizer.create_batch_insert_query(vectors, metadata))
```

### 3.2 Integration into Worker

Add to your worker task code:

```python
from embedding.memory_optimization import (
    StreamingEmbeddingGenerator,
    MemoryMappedVectorStore,
    Neo4jBatchOptimizer,
    optimize_embedding_worker
)

@app.task
def process_embeddings(text_batch):
    """Task that uses memory-optimized streaming."""

    generator = StreamingEmbeddingGenerator(
        batch_size=100,
        gc_interval=1000
    )

    for vec_data in generator.stream_embeddings(text_batch, embedding_func):
        # Process and store immediately, don't accumulate
        store_to_neo4j(vec_data)

    # Report throughput
    return {
        'processed': generator.vectors_processed,
        'throughput_vec_sec': generator.get_throughput()
    }
```

---

## Phase 4: Neo4j Configuration Updates

### 4.1 Update Neo4j Settings

Connect to Neo4j and run:

```cypher
# Enable query cache
CALL apoc.config.set('query.max_cached_plans', 10000);

# Increase memory if available (optional, depends on Neo4j pod limits)
# Current: 256m initial, 512m max
```

### 4.2 Verify Neo4j Health

```bash
# Port-forward to Neo4j
kubectl port-forward neo4j-0 7687:7687 -n quran-system

# Query memory usage
curl -u neo4j:$PASSWORD -X POST http://localhost:7474/db/neo4j/tx \
  -H "Content-Type: application/json" \
  -d '{
    "statements": [{
      "statement": "CALL dbms.queryJmx(\"java.lang:type=Memory\") YIELD attributes RETURN attributes"
    }]
  }'
```

Expected baseline memory (before optimization):
- Used: ~200-300MB
- Committed: 512MB
- Usage: 40-60%

Expected post-optimization:
- Used: ~250-350MB (slightly higher throughput, but still < 85%)
- Committed: 512MB
- Usage: < 80% (room to scale further)

---

## Phase 5: Deploy Monitoring

### 5.1 Configure Grafana Dashboard

Import the dashboard configuration:

```bash
# Dashboard JSON is at: kubernetes/monitoring/embedding-monitoring-dashboard.json
# Import into Grafana via:
# 1. Grafana UI → Dashboards → Import
# 2. Paste JSON from embedding-monitoring-dashboard.json
# 3. Select Prometheus as datasource
```

### 5.2 Deploy Monitoring Script

```bash
# Install dependencies
pip install redis neo4j prometheus-client psutil kubernetes

# Run continuous monitoring (for testing)
python kubernetes/monitoring/embedding_monitoring.py \
  --interval 10 \
  --duration 3600 \
  --redis-host redis-0.redis-service.quran-system.svc.cluster.local \
  --neo4j-uri bolt://neo4j-0.neo4j-service.quran-system.svc.cluster.local:7687 \
  --prometheus-url http://prometheus-service.quran-system.svc.cluster.local:9090
```

### 5.3 Deploy as Kubernetes CronJob (Optional)

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: embedding-monitoring
  namespace: quran-system
spec:
  schedule: "*/5 * * * *"  # Every 5 minutes
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: embedding-monitor
          containers:
          - name: monitor
            image: quran-frontier-monitor:latest
            command:
            - python
            - /scripts/embedding_monitoring.py
            - --interval
            - "5"
            - --duration
            - "300"
          restartPolicy: OnFailure
```

---

## Phase 6: Verify & Monitor Improvements

### 6.1 Baseline Collection (First 5 minutes)

Before optimization is fully active, observe baseline metrics:

```bash
# Monitor in separate terminal
kubectl logs -f deployment/worker -n quran-system | grep -i "throughput\|memory\|queue"
```

Expected baseline:
- Throughput: 100-120 vec/sec
- Queue depth: accumulating (increasing)
- Memory: 400-800MB per pod
- GC events: frequent (every 30-60 seconds)

### 6.2 Post-Optimization Validation (After 5-15 minutes)

Expected improvements:

1. **Throughput Increase**
   ```
   ✓ Current: 120 vec/sec → Target: 250+ vec/sec
   Timeline: Should reach 180-200 vec/sec after first scale-up (4 pods)
   Timeline: Should reach 250+ vec/sec after second scale-up (6 pods)
   ```

2. **Memory Stabilization**
   ```
   ✓ Neo4j memory < 80% (was frequently > 85%)
   ✓ Worker pods stable at 600-800MB (not creeping to 1GB limit)
   ✓ Streaming generator releasing memory after each 1000-vector batch
   ```

3. **Queue Normalization**
   ```
   ✓ Queue depth trending down (was accumulating)
   ✓ Final depth: < 100 items (vs. > 500 during baseline)
   ```

4. **Scaling Activity**
   ```
   ✓ HPA scales from 2 → 4 replicas (when queue > 500)
   ✓ HPA scales from 4 → 6 replicas (if queue still > 500)
   ✓ Stabilizes at 4-6 replicas to maintain 250+ vec/sec
   ```

### 6.3 Sample Dashboard Output

After optimization, Grafana should show:

| Metric | Baseline | Target | Achieved |
|--------|----------|--------|----------|
| Throughput (vec/sec) | 120 | 250+ | 280 |
| Worker Replicas | 2 | 4-6 | 5 |
| Neo4j Memory % | 85% | < 80% | 72% |
| Queue Depth | 800+ | < 500 | 120 |
| GC Collections/5m | 15 | 8-10 | 9 |

---

## Troubleshooting

### Issue: Throughput Still Below 250 vec/sec

**Diagnosis:**
```bash
# Check worker logs
kubectl logs deployment/worker -n quran-system --tail=50 | grep -i error

# Check Neo4j query performance
kubectl exec neo4j-0 -n quran-system -- cypher-shell \
  'CALL dbms.queryJmx("java.lang:type=Threading") YIELD attributes RETURN attributes;'

# Check Redis queue
kubectl exec redis-0 -n quran-system -- redis-cli LLEN embedding:queue
```

**Solutions:**
1. Increase max replicas from 6 to 8: Edit HPA maxReplicas
2. Reduce Neo4j batch size from 100 to 75 if pool exhausted
3. Check if embedding model itself is bottleneck (not memory)

### Issue: Neo4j Memory Exceeds 85%

**Quick Fix:**
```bash
# Reduce batch size temporarily
kubectl set env deployment/worker \
  NEO4J_BATCH_SIZE=75 \
  -n quran-system

# Clear Neo4j cache
kubectl exec neo4j-0 -n quran-system -- cypher-shell \
  'CALL dbms.queryJmx("java.lang:type=Memory") YIELD attributes RETURN attributes;'
```

### Issue: Pods Crashing (OOM)

**Investigation:**
```bash
# Check events
kubectl describe pod <pod-name> -n quran-system | tail -20

# Check memory requests vs actual
kubectl top pods -n quran-system -l app=worker
```

**Solutions:**
1. Increase memory limit from 1Gi to 1.5Gi (if cluster allows)
2. Disable memory-mapped storage (less efficient but more stable)
3. Reduce gc_interval from 1000 to 500 (more frequent collections)

---

## Performance Validation Test

Run this script to validate improvements:

```bash
#!/bin/bash
# test_embedding_optimization.sh

echo "Phase 3 Embedding Optimization Test"
echo "======================================"

# Get baseline metrics
echo "Collecting baseline (30s)..."
sleep 30

THROUGHPUT=$(kubectl exec redis-0 -n quran-system -- redis-cli \
  HGET embedding:stats throughput_vec_sec | tail -1)

QUEUE_DEPTH=$(kubectl exec redis-0 -n quran-system -- redis-cli \
  LLEN embedding:queue)

NEO4J_MEM=$(kubectl exec neo4j-0 -n quran-system -- cypher-shell \
  'CALL dbms.queryJmx("java.lang:type=Memory") YIELD attributes RETURN attributes;' \
  | grep -i "heapmemory" | tail -1)

echo "Baseline Metrics:"
echo "  Throughput: $THROUGHPUT vec/sec"
echo "  Queue Depth: $QUEUE_DEPTH items"
echo "  Neo4j Memory: $NEO4J_MEM"

# Validate targets
if (( $(echo "$THROUGHPUT > 250" | bc -l) )); then
  echo "✓ PASS: Throughput target achieved ($THROUGHPUT > 250)"
else
  echo "✗ FAIL: Throughput below target ($THROUGHPUT < 250)"
fi

if (( QUEUE_DEPTH < 500 )); then
  echo "✓ PASS: Queue depth normalized ($QUEUE_DEPTH < 500)"
else
  echo "✗ FAIL: Queue still accumulating ($QUEUE_DEPTH > 500)"
fi

echo "======================================"
```

---

## Rollback Plan

If optimization causes issues:

```bash
# Quick rollback to baseline deployment
kubectl rollout undo deployment/worker -n quran-system

# Remove HPA (revert to static 2 replicas)
kubectl delete hpa embedding-worker-hpa -n quran-system

# Reset Neo4j config
kubectl exec neo4j-0 -n quran-system -- cypher-shell \
  'CALL apoc.config.set("query.max_cached_plans", 1000);'
```

Expected rollback time: < 2 minutes

---

## Success Criteria Checklist

- [ ] HPA deployed and scaling workers 2 → 4 → 6 pods
- [ ] Worker deployment updated with memory optimization env vars
- [ ] Memory optimization module integrated into tasks
- [ ] Grafana dashboard showing 250+ vec/sec throughput
- [ ] Neo4j memory consistently < 80%
- [ ] Queue depth trending down (< 100 items at equilibrium)
- [ ] GC pauses < 100ms per collection
- [ ] No worker OOM restarts in 10-minute stability window
- [ ] All 5 dashboard alerts configured and functioning

---

## References

- HPA Config: `kubernetes/09-embedding-worker-hpa.yaml`
- Worker Deployment: `kubernetes/08-worker-deployment-optimized.yaml`
- Memory Optimization Module: `quran-core/src/embedding/memory_optimization.py`
- Monitoring Dashboard: `kubernetes/monitoring/embedding-monitoring-dashboard.json`
- Monitoring Script: `kubernetes/monitoring/embedding_monitoring.py`

---

## Support & Monitoring

For ongoing monitoring post-deployment:

```bash
# Watch all components
watch -n 5 'kubectl get pods,hpa -n quran-system'

# Tail worker logs
kubectl logs -f deployment/worker -n quran-system --all-containers=true

# Monitor Prometheus metrics
kubectl port-forward svc/prometheus 9090:9090 -n quran-system
# Then visit http://localhost:9090/graph
```

**Key metrics to track:**
- `embedding_vectors_processed_total` (rate, should be > 250/sec)
- `neo4j_memory_heap_used_bytes` (should be < 85% of max)
- `redis_queue_depth` (should be < 500 items)
- `kube_hpa_status_desired_replicas` (should scale to 4-6)

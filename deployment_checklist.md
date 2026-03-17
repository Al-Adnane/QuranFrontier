# Phase 5 Deployment Checklist

**Phase**: Phase 5 (Production Deployment)
**Date**: 2026-03-14
**Target Activation Time**: 5 minutes (from pre-warm)
**Estimated Activation Time**: 3-5 minutes

---

## PRE-FLIGHT CHECKS (T-60 minutes)

### Infrastructure Readiness
- [ ] **Kubernetes Cluster Accessible**
  - Command: `kubectl cluster-info`
  - Expected: Cluster is running and accessible
  - Contact: DevOps Lead if inaccessible

- [ ] **Namespace Ready**
  - Command: `kubectl get namespace quran-system`
  - Expected: Namespace exists and is Active
  - Action: Create if needed: `kubectl create namespace quran-system`

- [ ] **Storage Classes Available**
  - Command: `kubectl get storageclass`
  - Expected: At least one storage class available (e.g., standard, fast, ssd)
  - Contact: Infrastructure team if none available

- [ ] **Docker Registry Accessible**
  - Command: `docker login <registry-url>`
  - Expected: Successfully authenticated
  - Contact: DevOps if login fails

- [ ] **Network Connectivity**
  - Ping external DNS servers
  - Test egress connectivity from worker nodes
  - Verify no network policies blocking required ports (5432, 6379, 7687, 19530)

### Secrets & Configuration
- [ ] **Secrets Created in Kubernetes**
  ```bash
  kubectl get secrets -n quran-system | grep quran-secrets
  ```
  Required secrets:
  - [ ] DB_PASSWORD
  - [ ] NEO4J_USER
  - [ ] NEO4J_PASSWORD
  - [ ] API_SECRET_KEY
  - [ ] JWT_SECRET
  - [ ] REDIS_PASSWORD
  - [ ] MILVUS_TOKEN (if applicable)

- [ ] **ConfigMap Created**
  ```bash
  kubectl get configmap -n quran-system | grep quran-config
  ```
  Must contain:
  - [ ] DB_HOST
  - [ ] DB_PORT
  - [ ] DB_NAME
  - [ ] MILVUS_HOST
  - [ ] MILVUS_PORT
  - [ ] API_LOG_LEVEL
  - [ ] PYTHONUNBUFFERED=1
  - [ ] PYTHONDONTWRITEBYTECODE=1

- [ ] **TLS Certificate Ready**
  - Check cert-manager installation
  - Verify certificate issued for ingress domains
  - Command: `kubectl get certificate -n quran-system`

### Data Migration
- [ ] **Database Backups Verified**
  - Latest backup timestamp recorded
  - Backup file tested for restore capability
  - Backup location documented

- [ ] **Corpus Data Integrity Validated**
  - Command: `python verify_data_integrity.sh`
  - Expected: All corpus records verified
  - Expected: Checksums match production baseline

- [ ] **Neo4j Graph Backups Created**
  - Command: `neo4j-admin backup --backup-dir=/backups`
  - Expected: Full backup completed
  - Backup size recorded

- [ ] **Redis Persistence Enabled**
  - Command: `redis-cli CONFIG GET save`
  - Expected: RDB snapshots configured
  - AOF enabled: Yes

- [ ] **Embedding Vectors Backed Up**
  - Milvus collection backed up
  - Backup location: `/backups/milvus/<timestamp>`
  - Backup verified: Yes

---

## SERVICE INITIALIZATION ORDER (T-30 minutes)

### Phase 1: Persistent Data Layer
**Deployment Sequence** (wait for each to be Ready before next)

1. **PostgreSQL StatefulSet**
   ```bash
   kubectl apply -f kubernetes/01-postgres-statefulset.yaml
   kubectl wait --for=condition=ready pod -l app=postgres -n quran-system --timeout=600s
   ```
   - [ ] All 3 PostgreSQL pods Running
   - [ ] PVC bound and mounted
   - [ ] Health check passing
   - Timeout: 10 minutes

2. **Neo4j StatefulSet**
   ```bash
   kubectl apply -f kubernetes/02-neo4j-statefulset.yaml
   kubectl wait --for=condition=ready pod -l app=neo4j -n quran-system --timeout=600s
   ```
   - [ ] All 3 Neo4j pods Running
   - [ ] Cluster elected leader
   - [ ] Bolt port accessible
   - Timeout: 10 minutes

3. **Redis StatefulSet**
   ```bash
   kubectl apply -f kubernetes/03-redis-statefulset.yaml
   kubectl wait --for=condition=ready pod -l app=redis -n quran-system --timeout=300s
   ```
   - [ ] All 3 Redis pods Running
   - [ ] Cluster formation verified
   - [ ] Sentinel active
   - Timeout: 5 minutes

4. **Milvus StatefulSet**
   ```bash
   kubectl apply -f kubernetes/04-milvus-statefulset.yaml
   kubectl wait --for=condition=ready pod -l app=milvus -n quran-system --timeout=300s
   ```
   - [ ] All 3 Milvus pods Running
   - [ ] Segment stores ready
   - [ ] Collections accessible
   - Timeout: 5 minutes

### Phase 2: Service Dependencies
5. **Config & Secrets**
   ```bash
   kubectl apply -f kubernetes/config/secrets.yaml
   kubectl apply -f kubernetes/config/configmap.yaml
   ```
   - [ ] Secrets applied without error
   - [ ] ConfigMap applied without error

### Phase 3: Application Services
6. **API Deployment**
   ```bash
   kubectl apply -f kubernetes/05-api-deployment.yaml
   kubectl wait --for=condition=ready deployment/api -n quran-system --timeout=300s
   ```
   - [ ] All 3 API replicas Ready
   - [ ] Service endpoint available
   - [ ] Health check: /health returning 200
   - Timeout: 5 minutes

7. **Frontend Deployment**
   ```bash
   kubectl apply -f kubernetes/06-frontend-deployment.yaml
   kubectl wait --for=condition=ready deployment/frontend -n quran-system --timeout=300s
   ```
   - [ ] All 3 Frontend replicas Ready
   - [ ] Static assets served
   - [ ] Connected to API backend
   - Timeout: 5 minutes

8. **Worker Deployment**
   ```bash
   kubectl apply -f kubernetes/08-worker-deployment.yaml
   kubectl wait --for=condition=ready deployment/worker -n quran-system --timeout=300s
   ```
   - [ ] All worker replicas Ready
   - [ ] Connected to message queue (Redis)
   - [ ] Processing jobs successfully
   - Timeout: 5 minutes

### Phase 4: Jobs & Utilities
9. **ETL CronJob**
   ```bash
   kubectl apply -f kubernetes/07-etl-job.yaml
   kubectl get cronjob corpus-etl -n quran-system
   ```
   - [ ] CronJob created
   - [ ] Schedule verified (0 2 * * *)
   - [ ] Timezone correct

10. **HPA & PDB**
    ```bash
    kubectl apply -f kubernetes/09-embedding-worker-hpa.yaml
    kubectl apply -f kubernetes/00-namespace.yaml (includes PDB)
    ```
    - [ ] HPA created
    - [ ] PDB created
    - [ ] Policy verified

11. **Ingress & Networking**
    ```bash
    kubectl apply -f kubernetes/networking/ingress.yaml
    ```
    - [ ] Ingress created
    - [ ] IP address assigned
    - [ ] TLS certificate active
    - [ ] DNS propagation verified (dig/nslookup)

---

## SMOKE TESTS (T-10 minutes)

### API Health Checks
```bash
bash health_check.sh
```

- [ ] **API Service Endpoint**
  - URL: `http://api-service.quran-system.svc.cluster.local:8000/health`
  - Expected: HTTP 200
  - Response contains: `{"status": "healthy"}`

- [ ] **Frontend Health**
  - URL: `http://frontend-service.quran-system.svc.cluster.local:80/`
  - Expected: HTTP 200
  - Response: HTML page loads

- [ ] **Worker Service Health**
  - Command: `kubectl exec -it deployment/worker -n quran-system -- celery -A tasks.worker inspect active`
  - Expected: Active worker nodes listed

### Database Connectivity Tests
```bash
bash verify_data_integrity.sh
```

- [ ] **PostgreSQL Connectivity**
  ```bash
  kubectl exec -it postgres-0 -n quran-system -- psql -U quran_user -d quran_db -c "SELECT COUNT(*) FROM quran_verses;"
  ```
  - Expected: Row count > 0

- [ ] **Neo4j Connectivity**
  ```bash
  kubectl exec -it neo4j-0 -n quran-system -- cypher-shell -u neo4j "MATCH (v:Verse) RETURN COUNT(v);"
  ```
  - Expected: Node count > 0

- [ ] **Redis Connectivity**
  ```bash
  kubectl exec -it redis-0 -n quran-system -- redis-cli PING
  ```
  - Expected: PONG

- [ ] **Milvus Connectivity**
  ```bash
  kubectl exec -it milvus-0 -n quran-system -- milvus_cli --version
  ```
  - Expected: Version info returned

### API Endpoint Tests
- [ ] **Search Endpoint**
  ```bash
  curl -X GET "http://api.quran-frontier.io/api/v1/search?q=basmala" -H "Authorization: Bearer <token>"
  ```
  - Expected: HTTP 200 with results

- [ ] **Corpus Endpoint**
  ```bash
  curl -X GET "http://api.quran-frontier.io/api/v1/corpus/info"
  ```
  - Expected: HTTP 200 with corpus statistics

- [ ] **Analytics Endpoint**
  ```bash
  curl -X GET "http://api.quran-frontier.io/api/v1/analytics/usage"
  ```
  - Expected: HTTP 200 with usage metrics

- [ ] **Metrics Endpoint**
  ```bash
  curl -X GET "http://api-service.quran-system.svc.cluster.local:8001/metrics" | grep quran
  ```
  - Expected: Prometheus metrics returned

---

## MONITORING SYSTEM ACTIVATION (T-5 minutes)

### Prometheus Setup
- [ ] **Prometheus ConfigMap Applied**
  ```bash
  kubectl apply -f kubernetes/monitoring/prometheus-config.yaml
  ```

- [ ] **Prometheus Service Scraping**
  ```bash
  kubectl logs -n quran-system deployment/prometheus | grep "started server"
  ```
  - Expected: Prometheus startup successful

- [ ] **Metrics Collection Verified**
  - Prometheus UI: http://prometheus.quran-frontier.io
  - Query: `up{namespace="quran-system"}`
  - Expected: 1.0 for all targets

### Grafana Dashboard Activation
- [ ] **Grafana Dashboards Imported**
  ```bash
  kubectl apply -f kubernetes/monitoring/grafana-dashboards.yaml
  ```

- [ ] **Data Sources Configured**
  - Prometheus source pointing to: http://prometheus:9090
  - Neo4j source configured
  - PostgreSQL plugin active

- [ ] **Dashboards Verified**
  - [ ] Quran Frontier Overview dashboard
  - [ ] API Performance dashboard
  - [ ] Database Health dashboard
  - [ ] Worker Status dashboard

### Alert Rules Configuration
- [ ] **Alert Rules Deployed**
  ```bash
  kubectl apply -f kubernetes/monitoring/alert-rules.yaml
  ```

- [ ] **Alert Manager Configured**
  ```bash
  kubectl logs -n quran-system statefulset/alertmanager | head -20
  ```

- [ ] **Test Alert Triggered**
  - Command: Trigger test alert
  - Expected: Alert received in configured channels (Slack/Email/PagerDuty)

---

## ROLLBACK PROCEDURE DOCUMENTATION

### Rollback Triggers
Automatic rollback initiated if any of the following occur within 5 minutes of deployment:

1. **API Health Check Failures**
   - More than 1 replica in CrashLoopBackOff state
   - More than 2 consecutive failed health checks
   - Response time > 30 seconds

2. **Database Connectivity Issues**
   - PostgreSQL replicas not reaching quorum (< 2 of 3)
   - Neo4j cluster split-brain detected
   - Data corruption detected in integrity check

3. **Service Mesh Issues**
   - Ingress routing failures
   - Certificate validation failures
   - Network policy blocking traffic

### Manual Rollback Procedure
```bash
# Step 1: Scale down new deployment
bash rollback.sh

# Step 2: Monitor rollback progress
watch kubectl get pods -n quran-system

# Step 3: Run health checks
bash health_check.sh

# Step 4: Verify previous version
curl http://api.quran-frontier.io/api/v1/version
```

**Rollback Time Estimate**: 2-3 minutes

---

## GO/NO-GO DECISION CHECKLIST

### Go Criteria (All must be YES)
- [ ] All pre-flight checks passed
- [ ] Security scan: 0 critical/high CVEs (conditionally approved status acceptable)
- [ ] Kubernetes manifest validation: PASSED
- [ ] All databases initialized and healthy
- [ ] All services healthy and ready
- [ ] All smoke tests passed
- [ ] Monitoring and alerting active
- [ ] On-call team ready
- [ ] Communication channels open

### No-Go Criteria (Any failure = NO-GO)
- [ ] Critical CVEs detected in any image
- [ ] Kubernetes manifest validation FAILED
- [ ] Any database failed to initialize
- [ ] Health check failures > 20% threshold
- [ ] Smoke tests failure rate > 10%
- [ ] Network connectivity issues unresolved
- [ ] TLS certificate issues unresolved
- [ ] On-call team unavailable

### Decision
- **GO Decision Authorized By**: DevOps Lead
- **Authorization Time**: [To be filled]
- **Deployment Window**: [To be filled]
- **Rollback Authority**: Engineering Lead

---

## DEPLOYMENT EXECUTION LOG

| Time | Component | Status | Notes |
|------|-----------|--------|-------|
| T-60  | Pre-flight checks | [ ] | |
| T-30  | PostgreSQL StatefulSet | [ ] | |
| T-25  | Neo4j StatefulSet | [ ] | |
| T-20  | Redis StatefulSet | [ ] | |
| T-15  | Milvus StatefulSet | [ ] | |
| T-10  | API Deployment | [ ] | |
| T-5   | Frontend Deployment | [ ] | |
| T-0   | Worker Deployment | [ ] | |
| T+2   | Smoke tests | [ ] | |
| T+3   | Monitoring activation | [ ] | |
| T+5   | DEPLOYMENT COMPLETE | [ ] | |

---

## POST-DEPLOYMENT VALIDATION (T+10 minutes)

- [ ] All pods in Ready state: `kubectl get pods -n quran-system`
- [ ] Services have endpoints: `kubectl get svc -n quran-system`
- [ ] PVC all bound: `kubectl get pvc -n quran-system`
- [ ] No crashloops: `kubectl get pods -n quran-system | grep -i crash`
- [ ] No pending pods: `kubectl get pods -n quran-system | grep -i pending`
- [ ] Logs show successful startup: `kubectl logs -n quran-system --all-containers=true --timestamps=true -l app=api | tail -50`
- [ ] Prometheus metrics flowing
- [ ] Grafana dashboards populated
- [ ] Alerts active in AlertManager

---

## STAKEHOLDER NOTIFICATION

- [ ] DevOps Team notified of deployment start
- [ ] On-call Engineer on standby
- [ ] Product team notified of go-ahead
- [ ] Documentation team notified
- [ ] Support team updated on endpoints/health checks
- [ ] Slack channel #phase-5-deployment updated with live status

---

## DOCUMENTS REFERENCE

- Security Scan Report: `trivy_scan_report.json`
- Manifest Validation: `manifest_validation_report.json`
- Deployment Scripts: `deploy.sh`, `rollback.sh`
- Health Checks: `health_check.sh`
- Data Integrity: `verify_data_integrity.sh`
- Monitoring Config: `monitoring_config.yaml`

# FrontierQu Deployment Runbook

**Version:** 1.0.0
**Last Updated:** March 14, 2026
**Environment:** Production (Kubernetes)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Step-by-Step Deployment](#step-by-step-deployment)
4. [Post-Deployment Verification](#post-deployment-verification)
5. [Troubleshooting](#troubleshooting)
6. [Rollback Procedures](#rollback-procedures)

---

## Prerequisites

### System Requirements

- **Kubernetes Cluster:** v1.24+
- **kubectl:** v1.24+
- **Docker:** 20.10+ (for image building)
- **Helm:** 3.10+ (for package management)
- **Disk Space:** 500 GB minimum
- **Memory:** 64 GB minimum across cluster
- **CPU:** 16 cores minimum

### Network Requirements

- **Ports Open:**
  - 8000 (API service)
  - 5432 (PostgreSQL)
  - 7687 (Neo4j)
  - 6379 (Redis)
  - 443 (HTTPS)
  - 80 (HTTP redirect)
- **DNS:** Configured domain for frontierqu.ai
- **TLS Certificates:** Valid SSL/TLS certificates (via Let's Encrypt or corporate CA)

### Prerequisites Checklist

- [ ] Kubernetes cluster operational and accessible
- [ ] kubectl configured and authenticated
- [ ] Helm 3.10+ installed
- [ ] Docker registry credentials configured
- [ ] PersistentVolume provisioner available
- [ ] Ingress controller deployed
- [ ] TLS certificates prepared
- [ ] Backup storage configured
- [ ] Monitoring stack available (Prometheus, Grafana)

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                     │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Ingress Layer (HTTPS/TLS)                          │  │
│  │ ├─ frontend.frontierqu.ai → Frontend Service      │  │
│  │ └─ api.frontierqu.ai → API Service                │  │
│  └────────────────────────────────────────────────────┘  │
│                          ↓                                │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Application Layer                                   │  │
│  │ ├─ API Service (FastAPI, 3 replicas)             │  │
│  │ ├─ Frontend Service (React, 3 replicas)          │  │
│  │ ├─ ETL Service (Batch processing)                │  │
│  │ └─ Worker Service (Async tasks, Ray cluster)     │  │
│  └────────────────────────────────────────────────────┘  │
│                          ↓                                │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Data Layer                                          │  │
│  │ ├─ PostgreSQL (RDS or self-hosted, 100 GB)       │  │
│  │ ├─ Neo4j (GraphDB, 50 GB)                         │  │
│  │ ├─ Redis (Cache, 10 GB)                           │  │
│  │ └─ Weaviate (Vector DB, 200 GB)                   │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Storage Layer                                       │  │
│  │ ├─ PersistentVolume (Corpus data)                 │  │
│  │ ├─ Backup Storage (S3, GCS, or on-prem)          │  │
│  │ └─ Logs & Metrics (EFK or similar)                │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Deployment

### Step 1: Prepare Kubernetes Cluster

Create namespace and configure RBAC:

```bash
# Create namespace
kubectl create namespace frontierqu

# Label namespace
kubectl label namespace frontierqu environment=production

# Create service account for deployments
kubectl create serviceaccount frontierqu-deployer -n frontierqu

# Grant necessary permissions
kubectl create clusterrolebinding frontierqu-deployer \
  --clusterrole=cluster-admin \
  --serviceaccount=frontierqu:frontierqu-deployer
```

### Step 2: Deploy PostgreSQL

Create PostgreSQL persistent volume and deployment:

```bash
# Create PersistentVolume for PostgreSQL
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: postgres-pv
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: standard
  hostPath:
    path: /data/postgres
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: frontierqu
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 100Gi
EOF

# Deploy PostgreSQL using Helm
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install postgres bitnami/postgresql \
  -n frontierqu \
  --set auth.postgresPassword=change_me \
  --set auth.database=frontierqu \
  --set persistence.enabled=true \
  --set persistence.existingClaim=postgres-pvc \
  --set resources.requests.memory=8Gi \
  --set resources.requests.cpu=2

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/name=postgresql \
  -n frontierqu --timeout=300s
```

### Step 3: Deploy Neo4j Graph Database

```bash
# Create PersistentVolume for Neo4j
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: neo4j-pv
spec:
  capacity:
    storage: 50Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: standard
  hostPath:
    path: /data/neo4j
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: neo4j-pvc
  namespace: frontierqu
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 50Gi
EOF

# Deploy Neo4j
helm repo add neo4j https://helm.neo4j.com/neo4j
helm repo update

helm install neo4j neo4j/neo4j \
  -n frontierqu \
  --set neo4j.password=change_me \
  --set persistence.enabled=true \
  --set persistence.existingClaim=neo4j-pvc \
  --set resources.requests.memory=16Gi \
  --set resources.requests.cpu=4

# Wait for Neo4j to be ready
kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/name=neo4j \
  -n frontierqu --timeout=300s
```

### Step 4: Deploy Redis Cache

```bash
# Deploy Redis
helm install redis bitnami/redis \
  -n frontierqu \
  --set auth.password=change_me \
  --set master.persistence.enabled=true \
  --set master.persistence.size=10Gi \
  --set resources.requests.memory=4Gi \
  --set resources.requests.cpu=1

# Wait for Redis to be ready
kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/name=redis \
  -n frontierqu --timeout=300s
```

### Step 5: Deploy Weaviate Vector Database

```bash
# Create PersistentVolume for Weaviate
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: weaviate-pv
spec:
  capacity:
    storage: 200Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: standard
  hostPath:
    path: /data/weaviate
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: weaviate-pvc
  namespace: frontierqu
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 200Gi
EOF

# Deploy Weaviate
helm repo add weaviate https://weaviate.github.io/weaviate-helm
helm repo update

helm install weaviate weaviate/weaviate \
  -n frontierqu \
  --set persistence.enabled=true \
  --set persistence.existingClaim=weaviate-pvc \
  --set resources.requests.memory=8Gi \
  --set resources.requests.cpu=2
```

### Step 6: Create Database Schemas

Initialize PostgreSQL schema:

```bash
# Connect to PostgreSQL pod
POSTGRES_POD=$(kubectl get pod -l app.kubernetes.io/name=postgresql \
  -n frontierqu -o jsonpath='{.items[0].metadata.name}')

# Apply schema
kubectl exec -it $POSTGRES_POD -n frontierqu -- \
  psql -U postgres -d frontierqu < database/schema.sql
```

### Step 7: Deploy API Service

Create API deployment configuration:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontierqu-api
  namespace: frontierqu
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontierqu-api
  template:
    metadata:
      labels:
        app: frontierqu-api
    spec:
      containers:
      - name: api
        image: frontierqu/api:1.0.0
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: connection-string
        - name: NEO4J_URL
          valueFrom:
            secretKeyRef:
              name: neo4j-credentials
              key: connection-string
        - name: REDIS_URL
          value: "redis://redis-master:6379"
        - name: WEAVIATE_URL
          value: "http://weaviate:8080"
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: frontierqu
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
  selector:
    app: frontierqu-api
EOF

# Wait for deployment to be ready
kubectl rollout status deployment/frontierqu-api -n frontierqu
```

### Step 8: Deploy Frontend Service

```bash
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontierqu-frontend
  namespace: frontierqu
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontierqu-frontend
  template:
    metadata:
      labels:
        app: frontierqu-frontend
    spec:
      containers:
      - name: frontend
        image: frontierqu/frontend:1.0.0
        imagePullPolicy: Always
        ports:
        - containerPort: 3000
        env:
        - name: REACT_APP_API_URL
          value: "https://api.frontierqu.ai/v1"
        - name: REACT_APP_ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "1Gi"
            cpu: "1"
          limits:
            memory: "2Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: frontierqu
spec:
  type: ClusterIP
  ports:
  - port: 3000
    targetPort: 3000
  selector:
    app: frontierqu-frontend
EOF
```

### Step 9: Configure Ingress with TLS

```bash
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: frontierqu-cert
  namespace: frontierqu
spec:
  secretName: frontierqu-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - frontierqu.ai
  - api.frontierqu.ai
  - frontend.frontierqu.ai
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontierqu-ingress
  namespace: frontierqu
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - frontierqu.ai
    - api.frontierqu.ai
    - frontend.frontierqu.ai
    secretName: frontierqu-tls
  rules:
  - host: api.frontierqu.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8000
  - host: frontend.frontierqu.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 3000
EOF
```

---

## Post-Deployment Verification

### Verification Checklist

Run the following checks to verify successful deployment:

```bash
#!/bin/bash

echo "=== FrontierQu Deployment Verification ==="

# Check namespace
echo "[1/10] Checking namespace..."
kubectl get namespace frontierqu

# Check pods
echo "[2/10] Checking pods..."
kubectl get pods -n frontierqu

# Check services
echo "[3/10] Checking services..."
kubectl get svc -n frontierqu

# Check API health
echo "[4/10] Checking API health..."
API_POD=$(kubectl get pod -l app=frontierqu-api -n frontierqu \
  -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $API_POD -n frontierqu -- \
  curl -s http://localhost:8000/health | jq .

# Check database connectivity
echo "[5/10] Checking PostgreSQL..."
POSTGRES_POD=$(kubectl get pod -l app.kubernetes.io/name=postgresql \
  -n frontierqu -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POSTGRES_POD -n frontierqu -- \
  psql -U postgres -d frontierqu -c "SELECT version();"

# Check Neo4j
echo "[6/10] Checking Neo4j..."
NEO4J_POD=$(kubectl get pod -l app.kubernetes.io/name=neo4j \
  -n frontierqu -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $NEO4J_POD -n frontierqu -- \
  cypher-shell -u neo4j -p change_me "RETURN 1"

# Check Redis
echo "[7/10] Checking Redis..."
REDIS_POD=$(kubectl get pod -l app.kubernetes.io/name=redis \
  -n frontierqu -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $REDIS_POD -n frontierqu -- \
  redis-cli PING

# Check Weaviate
echo "[8/10] Checking Weaviate..."
kubectl port-forward svc/weaviate 8080:8080 -n frontierqu &
sleep 2
curl -s http://localhost:8080/v1/meta | jq .
kill %1

# Check Ingress
echo "[9/10] Checking Ingress..."
kubectl get ingress -n frontierqu

# Check certificates
echo "[10/10] Checking TLS certificates..."
kubectl get certificate -n frontierqu

echo "=== Verification Complete ==="
```

### Manual Testing

Test API endpoints:

```bash
# Test API health
curl -k https://api.frontierqu.ai/v1/health

# Test model listing
curl -k https://api.frontierqu.ai/v1/models

# Test knowledge graph search
curl -k "https://api.frontierqu.ai/v1/graph/search?q=fasting"

# Test authentication (should fail without token)
curl -k https://api.frontierqu.ai/v1/audit-logs
# Expected: 401 Unauthorized
```

---

## Troubleshooting

### Issue: Pods Not Starting

**Symptoms:** Pods in CrashLoopBackOff or Pending state

**Solution:**

```bash
# Check pod logs
kubectl logs <pod-name> -n frontierqu

# Check pod events
kubectl describe pod <pod-name> -n frontierqu

# Check node resources
kubectl top nodes

# Check disk space
kubectl exec -it <pod-name> -n frontierqu -- df -h
```

### Issue: Database Connection Errors

**Symptoms:** API pods crash with database connection errors

**Solution:**

```bash
# Check PostgreSQL service
kubectl get svc -n frontierqu postgres-postgresql

# Test connection
POSTGRES_POD=$(kubectl get pod -l app.kubernetes.io/name=postgresql \
  -n frontierqu -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POSTGRES_POD -n frontierqu -- \
  psql -U postgres -c "SELECT 1"

# Check credentials
kubectl get secret postgres-credentials -n frontierqu -o yaml
```

### Issue: Ingress Not Routing Traffic

**Symptoms:** Cannot access services through domain names

**Solution:**

```bash
# Check ingress configuration
kubectl describe ingress frontierqu-ingress -n frontierqu

# Check certificate status
kubectl describe certificate frontierqu-cert -n frontierqu

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# Test DNS resolution
nslookup api.frontierqu.ai
```

### Issue: High Memory Usage

**Symptoms:** Pods consuming excessive memory, out-of-memory kills

**Solution:**

```bash
# Check resource usage
kubectl top pods -n frontierqu

# Increase resource limits in deployment
kubectl set resources deployment frontierqu-api \
  -n frontierqu \
  --limits=memory=16Gi,cpu=8 \
  --requests=memory=8Gi,cpu=4

# Add node autoscaling if on cloud provider
```

---

## Rollback Procedures

### Rollback to Previous Version

```bash
# Check deployment history
kubectl rollout history deployment/frontierqu-api -n frontierqu

# Rollback to previous revision
kubectl rollout undo deployment/frontierqu-api -n frontierqu

# Rollback to specific revision
kubectl rollout undo deployment/frontierqu-api -n frontierqu --to-revision=2

# Monitor rollout
kubectl rollout status deployment/frontierqu-api -n frontierqu
```

### Database Rollback

See UPGRADE_GUIDE.md for database rollback procedures.

---

## Post-Deployment Configuration

1. **Update database credentials** in Kubernetes secrets
2. **Configure external monitoring** (Prometheus, Grafana)
3. **Set up logging** (EFK stack or similar)
4. **Configure backups** (schedule automated dumps)
5. **Set up security policies** (network policies, pod security policies)
6. **Initialize audit logging** in PostgreSQL

---

## Deployment Timeline

- **Prerequisites:** 30 minutes
- **Database setup:** 15 minutes
- **API deployment:** 10 minutes
- **Frontend deployment:** 5 minutes
- **Ingress/TLS:** 10 minutes (includes DNS propagation)
- **Verification:** 15 minutes

**Total estimated time:** 85 minutes

---

**Last Updated:** March 14, 2026
**Next Review:** June 14, 2026
**Deployment Status:** Ready for Production

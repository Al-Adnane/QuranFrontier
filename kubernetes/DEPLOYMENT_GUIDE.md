# Quran Frontier - Kubernetes Deployment Guide

This guide provides step-by-step instructions for deploying the complete Quran Frontier infrastructure using Docker and Kubernetes.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Local Development Setup](#local-development-setup)
4. [Building Docker Images](#building-docker-images)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Monitoring & Logging](#monitoring--logging)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)
9. [Security Hardening](#security-hardening)

---

## Prerequisites

### Required Tools

- **Docker**: v20.10+ (for building images)
- **Kubernetes**: v1.24+ cluster (local or cloud)
- **kubectl**: v1.24+ (Kubernetes CLI)
- **Docker Registry**: DockerHub or private registry
- **Git**: For version control

### Kubernetes Cluster Setup

#### Option 1: Local Development (Minikube)

```bash
# Install Minikube
brew install minikube

# Start cluster with sufficient resources
minikube start --cpus=8 --memory=16384 --disk-size=100g

# Enable required add-ons
minikube addons enable ingress
minikube addons enable metrics-server

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)
echo "$MINIKUBE_IP api.quran.local" >> /etc/hosts
echo "$MINIKUBE_IP app.quran.local" >> /etc/hosts
```

#### Option 2: Cloud Kubernetes (EKS/GKE/AKS)

```bash
# Example for AWS EKS
aws eks create-cluster --name quran-system --region us-east-1 --nodegroup-name quran-nodes

# Configure kubectl
aws eks update-kubeconfig --name quran-system --region us-east-1

# Verify connection
kubectl cluster-info
```

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Ingress (NGINX)                          │   │
│  │  - api.quran.local → API Service                     │   │
│  │  - app.quran.local → Frontend Service                │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                    │
│        ┌─────────────────┼─────────────────┐                │
│        │                 │                 │                │
│   ┌────▼────┐     ┌─────▼──────┐   ┌─────▼──────┐          │
│   │   API   │     │  Frontend   │   │  Worker    │          │
│   │  Pods   │     │   Pods      │   │  Pods      │          │
│   │  (3x)   │     │   (2x)      │   │  (2x)      │          │
│   └────┬────┘     └─────┬──────┘   └─────┬──────┘          │
│        │                │                │                  │
│        └────────────────┼────────────────┘                  │
│                         │                                    │
│        ┌────────────────┼────────────────┐                  │
│        │                │                │                  │
│   ┌────▼────┐     ┌─────▼──────┐  ┌────▼────┐             │
│   │ Postgres │     │   Neo4j    │  │  Redis   │ Milvus     │
│   │  StatefulSet   │  StatefulSet  │ StatefulSet           │
│   └──────────┘     └────────────┘  └──────────┘             │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Monitoring Stack                            │   │
│  │  - Prometheus (Metrics Collection)                    │   │
│  │  - Grafana (Visualization)                            │   │
│  │  - AlertManager (Alerting)                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Resource Allocation

| Component  | CPU Request | Memory Request | CPU Limit | Memory Limit |
|-----------|-------------|-----------------|-----------|--------------|
| API Pod   | 500m        | 512Mi           | 1         | 1Gi          |
| Frontend  | 250m        | 256Mi           | 500m      | 512Mi        |
| Worker    | 500m        | 512Mi           | 1         | 1Gi          |
| Postgres  | 500m        | 512Mi           | 2         | 2Gi          |
| Neo4j     | 500m        | 512Mi           | 2         | 1Gi          |
| Redis     | 200m        | 256Mi           | 1         | 512Mi        |
| Milvus    | 1           | 1Gi             | 4         | 4Gi          |

---

## Local Development Setup

### Docker Compose for Local Development

```bash
# Navigate to project root
cd /Users/mac/Desktop/QuranFrontier

# Create .env file from example
cp docker-compose.yml.env.example docker-compose.yml.env

# Edit secrets
nano docker-compose.yml.env

# Start services
docker-compose up -d

# Verify services
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f frontend
```

### Services Available Locally

- **API**: http://localhost:8000
  - Health: http://localhost:8000/health
  - Docs: http://localhost:8000/docs

- **Frontend**: http://localhost:3000

- **PostgreSQL**: localhost:5432
  - User: `quran_user`
  - Database: `quran_db`

- **Neo4j**: http://localhost:7474
  - User: `neo4j`

- **Redis**: localhost:6379

- **Milvus**: localhost:19530

- **Prometheus**: http://localhost:9090

- **Grafana**: http://localhost:3001
  - User: `admin`

---

## Building Docker Images

### Prerequisites

Ensure you have Docker installed and logged into a registry:

```bash
docker login docker.io
```

### Build Images

```bash
cd /Users/mac/Desktop/QuranFrontier

# Build API image
docker build -f Dockerfile.api -t quran-frontier-api:latest .
docker tag quran-frontier-api:latest docker.io/yourrepo/quran-frontier-api:latest
docker push docker.io/yourrepo/quran-frontier-api:latest

# Build Frontend image
docker build -f Dockerfile.frontend -t quran-frontier-frontend:latest .
docker tag quran-frontier-frontend:latest docker.io/yourrepo/quran-frontier-frontend:latest
docker push docker.io/yourrepo/quran-frontier-frontend:latest

# Build ETL image
docker build -f Dockerfile.etl -t quran-frontier-etl:latest .
docker tag quran-frontier-etl:latest docker.io/yourrepo/quran-frontier-etl:latest
docker push docker.io/yourrepo/quran-frontier-etl:latest

# Build Worker image
docker build -f Dockerfile.worker -t quran-frontier-worker:latest .
docker tag quran-frontier-worker:latest docker.io/yourrepo/quran-frontier-worker:latest
docker push docker.io/yourrepo/quran-frontier-worker:latest
```

### Image Sizes

Expected image sizes after multi-stage builds:

- API: ~400-500MB
- Frontend: ~300-400MB
- ETL: ~400-500MB
- Worker: ~400-500MB

---

## Kubernetes Deployment

### Step 1: Prepare Configuration

```bash
cd kubernetes

# Copy and customize secrets
cp config/secrets.yaml config/secrets.yaml.local

# Edit secrets with production values
nano config/secrets.yaml.local

# Apply changes
kubectl apply -f config/secrets.yaml.local -n quran-system
```

### Step 2: Run Deployment Script

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh

# Or deploy manually:
kubectl apply -f 00-namespace.yaml
kubectl apply -f config/configmap.yaml
kubectl apply -f config/secrets.yaml
kubectl apply -f storage/pvc.yaml
kubectl apply -f 01-postgres-statefulset.yaml
kubectl apply -f 02-neo4j-statefulset.yaml
kubectl apply -f 03-redis-statefulset.yaml
kubectl apply -f 04-milvus-statefulset.yaml
kubectl apply -f 05-api-deployment.yaml
kubectl apply -f 06-frontend-deployment.yaml
kubectl apply -f 07-etl-job.yaml
kubectl apply -f 08-worker-deployment.yaml
kubectl apply -f monitoring/
kubectl apply -f networking/
```

### Step 3: Verify Deployment

```bash
# Check namespace
kubectl get namespace quran-system

# Check pods
kubectl get pods -n quran-system -o wide

# Check services
kubectl get svc -n quran-system

# Check statefulsets
kubectl get statefulsets -n quran-system

# Check deployments
kubectl get deployments -n quran-system

# Check ingress
kubectl get ingress -n quran-system

# View pod logs
kubectl logs -n quran-system -l app=api -f
kubectl logs -n quran-system -l app=frontend -f
```

### Step 4: Access Services

```bash
# Port forward to API
kubectl port-forward -n quran-system svc/api-service 8000:8000

# Port forward to Frontend
kubectl port-forward -n quran-system svc/frontend-service 3000:3000

# Port forward to Prometheus
kubectl port-forward -n quran-system svc/prometheus 9090:9090

# Port forward to Grafana
kubectl port-forward -n quran-system svc/grafana 3001:3001
```

---

## Monitoring & Logging

### Prometheus Metrics

Access Prometheus at `http://localhost:9090/`

Key metrics:
- `api_requests_total`: Total API requests
- `api_request_duration_seconds`: API request latency
- `api_errors_total`: Total API errors
- `container_memory_usage_bytes`: Container memory
- `container_cpu_usage_seconds_total`: Container CPU

### Grafana Dashboards

Access Grafana at `http://localhost:3001/`
- Default user: `admin`
- Password: See `kubernetes/config/secrets.yaml`

Pre-configured dashboards:
- Quran System Overview
- API Performance
- Database Metrics
- Pod Resources

### Log Aggregation

```bash
# Stream logs from all pods
kubectl logs -n quran-system -f --all-containers=true

# Stream logs from specific service
kubectl logs -n quran-system -l app=api -f --all-containers=true

# Get logs from previous pod instance
kubectl logs -n quran-system <pod-name> --previous
```

---

## Backup & Recovery

### Backup Strategy

#### Daily Full Backup Script

```bash
#!/bin/bash
# backup.sh

NAMESPACE="quran-system"
BACKUP_DIR="/backups/quran-$(date +%Y%m%d-%H%M%S)"

mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL
kubectl exec -n $NAMESPACE postgres-0 -- \
  pg_dump -U quran_user quran_db | \
  gzip > "$BACKUP_DIR/postgres.dump.gz"

# Backup Neo4j
kubectl exec -n $NAMESPACE neo4j-0 -- \
  tar czf /tmp/neo4j-backup.tar.gz /var/lib/neo4j/data

kubectl cp $NAMESPACE:neo4j-0:/tmp/neo4j-backup.tar.gz \
  "$BACKUP_DIR/neo4j-backup.tar.gz"

# Backup Redis
kubectl exec -n $NAMESPACE redis-0 -- \
  redis-cli bgsave

kubectl cp $NAMESPACE:redis-0:/data/dump.rdb \
  "$BACKUP_DIR/redis-dump.rdb"

# Archive and compress
tar czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

# Upload to S3
aws s3 cp "$BACKUP_DIR.tar.gz" s3://backup-bucket/quran/

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

### Recovery Procedure

```bash
# Extract backup
tar xzf quran-20240314-120000.tar.gz

# Restore PostgreSQL
kubectl exec -i -n quran-system postgres-0 -- \
  gunzip < backup-dir/postgres.dump.gz | \
  psql -U quran_user quran_db

# Restore Neo4j
kubectl cp backup-dir/neo4j-backup.tar.gz quran-system:neo4j-0:/tmp/
kubectl exec -n quran-system neo4j-0 -- \
  tar xzf /tmp/neo4j-backup.tar.gz -C /

# Restore Redis
kubectl cp backup-dir/redis-dump.rdb quran-system:redis-0:/data/
kubectl exec -n quran-system redis-0 -- redis-cli SHUTDOWN
```

### RTO/RPO Targets

- **RTO (Recovery Time Objective)**: 1 hour
- **RPO (Recovery Point Objective)**: 24 hours
- **Backup Retention**: 30 days
- **Test Restore**: Weekly

---

## Troubleshooting

### Common Issues

#### Pods Not Starting

```bash
# Check pod status
kubectl describe pod -n quran-system <pod-name>

# Check events
kubectl get events -n quran-system --sort-by='.lastTimestamp'

# Check logs
kubectl logs -n quran-system <pod-name> --previous
```

#### Database Connection Issues

```bash
# Test database connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -n quran-system -- \
  nc -zv postgres-0.postgres-service.quran-system.svc.cluster.local 5432

# Test with psql
kubectl run -it --rm psql --image=postgres:16-alpine --restart=Never -n quran-system -- \
  psql -h postgres-0.postgres-service.quran-system.svc.cluster.local -U quran_user -d quran_db
```

#### High Memory Usage

```bash
# Check memory usage
kubectl top pods -n quran-system

# Check container limits
kubectl describe pod -n quran-system <pod-name>

# Adjust limits in deployment
kubectl set resources deployment api -n quran-system --limits=memory=2Gi,cpu=2 --requests=memory=1Gi,cpu=1
```

#### Network Policy Issues

```bash
# Test connectivity between pods
kubectl exec -it -n quran-system <pod-name> -- /bin/sh
nc -zv api-service.quran-system.svc.cluster.local 8000

# Disable network policies temporarily
kubectl delete networkpolicy --all -n quran-system
```

---

## Security Hardening

### 1. Secret Management

```bash
# Use sealed secrets for better security
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Create sealed secrets
echo -n 'password123' | kubectl create secret generic test --dry-run=client --from-file=password=/dev/stdin -o yaml | \
  kubectl apply -f -
```

### 2. Pod Security Policies

```bash
# Apply pod security policies
kubectl apply -f - <<EOF
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
  - ALL
  volumes:
  - 'configMap'
  - 'emptyDir'
  - 'projected'
  - 'secret'
  - 'downwardAPI'
  - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'MustRunAs'
  fsGroup:
    rule: 'MustRunAs'
  readOnlyRootFilesystem: false
EOF
```

### 3. Network Policies

Network policies are already defined in `networking/ingress.yaml` to restrict inter-pod communication.

### 4. RBAC Configuration

```bash
# Create service account for deployment
kubectl create serviceaccount quran-deployer -n quran-system

# Bind to role
kubectl create rolebinding quran-deployer-binding \
  --clusterrole=edit \
  --serviceaccount=quran-system:quran-deployer \
  -n quran-system
```

### 5. Secret Rotation

```bash
# Rotate database password
kubectl patch secret quran-secrets -n quran-system \
  -p '{"data":{"DB_PASSWORD":"'$(echo -n 'new-password' | base64)'"}}'

# Restart pods to apply new secrets
kubectl rollout restart deployment api -n quran-system
```

---

## Performance Tuning

### Horizontal Pod Autoscaling

```bash
# Check HPA status
kubectl get hpa -n quran-system

# Monitor scaling events
kubectl get events -n quran-system --field-selector involvedObject.kind=HorizontalPodAutoscaler
```

### Resource Optimization

```bash
# Install VPA (Vertical Pod Autoscaler)
kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vertical-pod-autoscaler-0.14.0/vpa-v0.14.0.yaml

# Check recommendations
kubectl describe vpa api-vpa -n quran-system
```

---

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

---

**Last Updated**: 2024-03-14
**Version**: 1.0

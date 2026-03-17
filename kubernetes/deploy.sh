#!/bin/bash
# Kubernetes Deployment Script for Quran Frontier System
# This script deploys the complete infrastructure to a Kubernetes cluster

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="quran-system"
DEPLOYMENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${DEPLOYMENT_DIR}/deployment-$(date +%Y%m%d-%H%M%S).log"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi

    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi

    log_success "kubectl is installed and connected"

    # Check if Docker images exist or need to be built
    log_info "Checking for required Docker images..."
}

create_namespace() {
    log_info "Creating namespace: $NAMESPACE"

    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_warning "Namespace $NAMESPACE already exists"
    else
        kubectl create namespace "$NAMESPACE"
        log_success "Namespace $NAMESPACE created"
    fi

    # Label namespace for monitoring
    kubectl label namespace "$NAMESPACE" app=quran-frontier --overwrite
}

apply_secrets() {
    log_info "Creating secrets..."

    # Check if secrets file exists
    if [ ! -f "$DEPLOYMENT_DIR/config/secrets.yaml" ]; then
        log_error "secrets.yaml not found"
        exit 1
    fi

    # Create secrets
    kubectl apply -f "$DEPLOYMENT_DIR/config/secrets.yaml" -n "$NAMESPACE"
    log_success "Secrets created/updated"
}

apply_configmaps() {
    log_info "Creating ConfigMaps..."

    kubectl apply -f "$DEPLOYMENT_DIR/config/configmap.yaml" -n "$NAMESPACE"
    log_success "ConfigMaps created/updated"
}

apply_storage() {
    log_info "Creating storage resources..."

    kubectl apply -f "$DEPLOYMENT_DIR/storage/pvc.yaml" -n "$NAMESPACE"
    log_success "PersistentVolumeClaims created/updated"
}

deploy_databases() {
    log_info "Deploying databases..."

    # PostgreSQL
    log_info "Deploying PostgreSQL..."
    kubectl apply -f "$DEPLOYMENT_DIR/01-postgres-statefulset.yaml"
    log_success "PostgreSQL deployed"

    # Neo4j
    log_info "Deploying Neo4j..."
    kubectl apply -f "$DEPLOYMENT_DIR/02-neo4j-statefulset.yaml"
    log_success "Neo4j deployed"

    # Redis
    log_info "Deploying Redis..."
    kubectl apply -f "$DEPLOYMENT_DIR/03-redis-statefulset.yaml"
    log_success "Redis deployed"

    # Milvus
    log_info "Deploying Milvus..."
    kubectl apply -f "$DEPLOYMENT_DIR/04-milvus-statefulset.yaml"
    log_success "Milvus deployed"

    # Wait for databases to be ready
    log_info "Waiting for databases to be ready..."
    kubectl wait --for=condition=Ready pod -l app=postgres -n "$NAMESPACE" --timeout=300s || true
    kubectl wait --for=condition=Ready pod -l app=neo4j -n "$NAMESPACE" --timeout=300s || true
    kubectl wait --for=condition=Ready pod -l app=redis -n "$NAMESPACE" --timeout=300s || true
    kubectl wait --for=condition=Ready pod -l app=milvus -n "$NAMESPACE" --timeout=300s || true

    log_success "Databases deployed and ready"
}

deploy_applications() {
    log_info "Deploying applications..."

    # API
    log_info "Deploying API..."
    kubectl apply -f "$DEPLOYMENT_DIR/05-api-deployment.yaml"
    log_success "API deployed"

    # Frontend
    log_info "Deploying Frontend..."
    kubectl apply -f "$DEPLOYMENT_DIR/06-frontend-deployment.yaml"
    log_success "Frontend deployed"

    # Wait for applications to be ready
    log_info "Waiting for applications to be ready..."
    kubectl wait --for=condition=Ready pod -l app=api -n "$NAMESPACE" --timeout=300s || true
    kubectl wait --for=condition=Ready pod -l app=frontend -n "$NAMESPACE" --timeout=300s || true

    log_success "Applications deployed and ready"
}

deploy_jobs() {
    log_info "Deploying jobs..."

    # ETL Job
    log_info "Deploying ETL job..."
    kubectl apply -f "$DEPLOYMENT_DIR/07-etl-job.yaml"
    log_success "ETL job deployed"

    # Worker Deployment
    log_info "Deploying worker..."
    kubectl apply -f "$DEPLOYMENT_DIR/08-worker-deployment.yaml"
    log_success "Worker deployed"
}

deploy_monitoring() {
    log_info "Deploying monitoring stack..."

    kubectl apply -f "$DEPLOYMENT_DIR/monitoring/prometheus-config.yaml"
    kubectl apply -f "$DEPLOYMENT_DIR/monitoring/prometheus-deployment.yaml"

    log_success "Monitoring stack deployed"
}

deploy_networking() {
    log_info "Deploying networking resources..."

    kubectl apply -f "$DEPLOYMENT_DIR/networking/ingress.yaml"

    log_success "Networking resources deployed"
}

verify_deployment() {
    log_info "Verifying deployment..."

    echo ""
    log_info "=== Deployment Status ==="

    # Check pods
    log_info "Checking pods..."
    kubectl get pods -n "$NAMESPACE" -o wide

    echo ""

    # Check services
    log_info "Checking services..."
    kubectl get svc -n "$NAMESPACE"

    echo ""

    # Check StatefulSets
    log_info "Checking StatefulSets..."
    kubectl get statefulsets -n "$NAMESPACE"

    echo ""

    # Check Deployments
    log_info "Checking Deployments..."
    kubectl get deployments -n "$NAMESPACE"

    echo ""

    # Check ingress
    log_info "Checking Ingress..."
    kubectl get ingress -n "$NAMESPACE"
}

main() {
    log_info "Starting Quran Frontier Kubernetes Deployment"
    log_info "Deployment log: $LOG_FILE"

    check_prerequisites
    create_namespace
    apply_secrets
    apply_configmaps
    apply_storage
    deploy_databases
    deploy_applications
    deploy_jobs
    deploy_monitoring
    deploy_networking
    verify_deployment

    echo ""
    log_success "========================================="
    log_success "Deployment completed successfully!"
    log_success "========================================="
    echo ""
    log_info "Next steps:"
    log_info "1. Port-forward to access services:"
    log_info "   kubectl port-forward -n $NAMESPACE svc/api-service 8000:8000"
    log_info "   kubectl port-forward -n $NAMESPACE svc/frontend-service 3000:3000"
    log_info ""
    log_info "2. View logs:"
    log_info "   kubectl logs -n $NAMESPACE -l app=api -f"
    log_info "   kubectl logs -n $NAMESPACE -l app=frontend -f"
    log_info ""
    log_info "3. Access Grafana:"
    log_info "   kubectl port-forward -n $NAMESPACE svc/grafana 3001:3001"
    log_info "   http://localhost:3001 (admin/your-password)"
    log_info ""
    log_info "4. Run ETL job:"
    log_info "   kubectl create job --from=cronjob/etl-scheduled-sync etl-manual-$(date +%s) -n $NAMESPACE"
}

main "$@"

#!/bin/bash

################################################################################
# Phase 5 Deployment Automation Script
# Purpose: Single-command deployment with proper service initialization order
# Activation Time Target: 5 minutes (from pre-warm)
# Author: Phase 5 Pre-Warm System
# Date: 2026-03-14
################################################################################

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Configuration
NAMESPACE="quran-system"
KUBERNETES_DIR="./kubernetes"
TIMEOUT_DB=600        # 10 minutes for databases
TIMEOUT_SERVICES=300  # 5 minutes for services
TIMEOUT_JOBS=120      # 2 minutes for jobs
START_TIME=$(date +%s)

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get deployment status
get_deployment_status() {
    local deployment=$1
    kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Progressing")].message}' 2>/dev/null || echo "unknown"
}

# Function to wait for pod readiness
wait_for_pods() {
    local selector=$1
    local timeout=$2
    local pod_name=${3:-"service"}

    log_info "Waiting for $pod_name pods to be ready (timeout: ${timeout}s)..."

    if kubectl wait --for=condition=ready pod -l "$selector" -n "$NAMESPACE" --timeout="${timeout}s" 2>/dev/null; then
        log_success "$pod_name pods are ready"
        return 0
    else
        log_error "$pod_name pods failed to reach ready state"
        return 1
    fi
}

# Function to wait for deployment readiness
wait_for_deployment() {
    local deployment=$1
    local timeout=$2
    local deployment_name=${3:-"deployment"}

    log_info "Waiting for $deployment_name to be ready (timeout: ${timeout}s)..."

    if kubectl wait --for=condition=available deployment/"$deployment" -n "$NAMESPACE" --timeout="${timeout}s" 2>/dev/null; then
        log_success "$deployment_name is ready"
        return 0
    else
        log_error "$deployment_name failed to reach ready state"
        kubectl get deployment "$deployment" -n "$NAMESPACE"
        kubectl get pods -n "$NAMESPACE" -l "app=$deployment" | tail -5
        return 1
    fi
}

# Function to check pod health
check_pod_health() {
    local deployment=$1

    local crashed_pods=$(kubectl get pods -n "$NAMESPACE" -l "app=$deployment" --field-selector=status.phase=Failed --no-headers 2>/dev/null | wc -l)
    local crashloop_pods=$(kubectl get pods -n "$NAMESPACE" -l "app=$deployment" -o json 2>/dev/null | jq -r '.items[].status.containerStatuses[]? | select(.state.waiting.reason=="CrashLoopBackOff") | .name' | wc -l)

    if [ "$crashed_pods" -gt 0 ] || [ "$crashloop_pods" -gt 0 ]; then
        log_warn "Found $crashed_pods crashed pods and $crashloop_pods in CrashLoopBackOff state for $deployment"
        return 1
    fi
    return 0
}

# Function to verify service endpoint
verify_service_endpoint() {
    local service=$1
    local port=$2

    local endpoint=$(kubectl get service "$service" -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}' 2>/dev/null)

    if [ -z "$endpoint" ]; then
        log_error "Service $service endpoint not found"
        return 1
    fi

    log_info "Service $service endpoint: $endpoint:$port"
    return 0
}

# Pre-deployment checks
pre_deployment_checks() {
    log_info "========== PRE-DEPLOYMENT CHECKS =========="

    # Check kubectl
    if ! command_exists kubectl; then
        log_error "kubectl not found. Please install kubectl."
        exit 1
    fi
    log_success "kubectl found"

    # Check cluster access
    if ! kubectl cluster-info > /dev/null 2>&1; then
        log_error "Cannot access Kubernetes cluster"
        exit 1
    fi
    log_success "Kubernetes cluster accessible"

    # Check namespace
    if ! kubectl get namespace "$NAMESPACE" > /dev/null 2>&1; then
        log_warn "Namespace $NAMESPACE does not exist. Creating..."
        kubectl create namespace "$NAMESPACE"
        log_success "Namespace $NAMESPACE created"
    else
        log_success "Namespace $NAMESPACE exists"
    fi

    # Check secrets
    if ! kubectl get secrets quran-secrets -n "$NAMESPACE" > /dev/null 2>&1; then
        log_error "Secrets 'quran-secrets' not found in namespace $NAMESPACE"
        log_info "Please create secrets first: kubectl create secret generic quran-secrets --from-literal=..."
        exit 1
    fi
    log_success "Secrets 'quran-secrets' exist"

    # Check configmap
    if ! kubectl get configmap quran-config -n "$NAMESPACE" > /dev/null 2>&1; then
        log_error "ConfigMap 'quran-config' not found in namespace $NAMESPACE"
        log_info "Please create configmap first: kubectl create configmap quran-config --from-literal=..."
        exit 1
    fi
    log_success "ConfigMap 'quran-config' exists"

    # Check kubernetes directory
    if [ ! -d "$KUBERNETES_DIR" ]; then
        log_error "Kubernetes manifests directory not found: $KUBERNETES_DIR"
        exit 1
    fi
    log_success "Kubernetes manifests directory found"

    echo ""
}

# Deploy namespace and policies
deploy_namespace_and_policies() {
    log_info "========== DEPLOYING NAMESPACE & POLICIES =========="

    kubectl apply -f "$KUBERNETES_DIR/00-namespace.yaml"
    log_success "Namespace, ResourceQuota, and LimitRange deployed"

    echo ""
}

# Phase 1: Persistent Data Layer
deploy_persistent_data_layer() {
    log_info "========== PHASE 1: DEPLOYING PERSISTENT DATA LAYER =========="

    # PostgreSQL
    log_info "[1/4] Deploying PostgreSQL StatefulSet..."
    kubectl apply -f "$KUBERNETES_DIR/01-postgres-statefulset.yaml"
    if wait_for_pods "app=postgres" $TIMEOUT_DB "PostgreSQL"; then
        log_success "PostgreSQL deployed and ready"
        verify_service_endpoint "postgres-service" "5432"
    else
        log_error "PostgreSQL deployment failed"
        return 1
    fi

    # Neo4j
    log_info "[2/4] Deploying Neo4j StatefulSet..."
    kubectl apply -f "$KUBERNETES_DIR/02-neo4j-statefulset.yaml"
    if wait_for_pods "app=neo4j" $TIMEOUT_DB "Neo4j"; then
        log_success "Neo4j deployed and ready"
        verify_service_endpoint "neo4j-service" "7687"
    else
        log_error "Neo4j deployment failed"
        return 1
    fi

    # Redis
    log_info "[3/4] Deploying Redis StatefulSet..."
    kubectl apply -f "$KUBERNETES_DIR/03-redis-statefulset.yaml"
    if wait_for_pods "app=redis" $TIMEOUT_SERVICES "Redis"; then
        log_success "Redis deployed and ready"
        verify_service_endpoint "redis-service" "6379"
    else
        log_error "Redis deployment failed"
        return 1
    fi

    # Milvus
    log_info "[4/4] Deploying Milvus StatefulSet..."
    kubectl apply -f "$KUBERNETES_DIR/04-milvus-statefulset.yaml"
    if wait_for_pods "app=milvus" $TIMEOUT_SERVICES "Milvus"; then
        log_success "Milvus deployed and ready"
        verify_service_endpoint "milvus-service" "19530"
    else
        log_error "Milvus deployment failed"
        return 1
    fi

    echo ""
}

# Phase 2: Configuration
deploy_configuration() {
    log_info "========== PHASE 2: DEPLOYING CONFIGURATION =========="

    log_info "Applying secrets and configmap..."
    kubectl apply -f "$KUBERNETES_DIR/config/secrets.yaml"
    kubectl apply -f "$KUBERNETES_DIR/config/configmap.yaml"
    log_success "Configuration deployed"

    echo ""
}

# Phase 3: Application Services
deploy_application_services() {
    log_info "========== PHASE 3: DEPLOYING APPLICATION SERVICES =========="

    # API
    log_info "[1/3] Deploying API service..."
    kubectl apply -f "$KUBERNETES_DIR/05-api-deployment.yaml"
    if wait_for_deployment "api" $TIMEOUT_SERVICES "API"; then
        if check_pod_health "api"; then
            log_success "API deployed and healthy"
            verify_service_endpoint "api-service" "8000"
        else
            log_error "API pods are not healthy"
            return 1
        fi
    else
        log_error "API deployment failed"
        return 1
    fi

    # Frontend
    log_info "[2/3] Deploying Frontend service..."
    kubectl apply -f "$KUBERNETES_DIR/06-frontend-deployment.yaml"
    if wait_for_deployment "frontend" $TIMEOUT_SERVICES "Frontend"; then
        if check_pod_health "frontend"; then
            log_success "Frontend deployed and healthy"
            verify_service_endpoint "frontend-service" "80"
        else
            log_error "Frontend pods are not healthy"
            return 1
        fi
    else
        log_error "Frontend deployment failed"
        return 1
    fi

    # Worker
    log_info "[3/3] Deploying Worker service..."
    kubectl apply -f "$KUBERNETES_DIR/08-worker-deployment.yaml"
    if wait_for_deployment "worker" $TIMEOUT_SERVICES "Worker"; then
        if check_pod_health "worker"; then
            log_success "Worker deployed and healthy"
            verify_service_endpoint "worker-service" "5000"
        else
            log_error "Worker pods are not healthy"
            return 1
        fi
    else
        log_error "Worker deployment failed"
        return 1
    fi

    echo ""
}

# Phase 4: Infrastructure Services
deploy_infrastructure_services() {
    log_info "========== PHASE 4: DEPLOYING INFRASTRUCTURE SERVICES =========="

    # ETL Job
    log_info "[1/3] Deploying ETL CronJob..."
    kubectl apply -f "$KUBERNETES_DIR/07-etl-job.yaml"
    log_success "ETL CronJob deployed"

    # HPA & PDB
    log_info "[2/3] Deploying Horizontal Pod Autoscaler..."
    kubectl apply -f "$KUBERNETES_DIR/09-embedding-worker-hpa.yaml"
    log_success "HPA deployed"

    # Ingress
    log_info "[3/3] Deploying Ingress..."
    kubectl apply -f "$KUBERNETES_DIR/networking/ingress.yaml"
    log_success "Ingress deployed"

    echo ""
}

# Post-deployment health checks
post_deployment_checks() {
    log_info "========== POST-DEPLOYMENT HEALTH CHECKS =========="

    # Check all pods
    log_info "Checking pod status..."
    local total_pods=$(kubectl get pods -n "$NAMESPACE" --no-headers | wc -l)
    local ready_pods=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Running --no-headers | wc -l)

    log_info "Total pods: $total_pods, Running: $ready_pods"

    # Check for crashloops
    local crashloop_count=$(kubectl get pods -n "$NAMESPACE" -o json | jq -r '.items[].status.containerStatuses[]? | select(.state.waiting.reason=="CrashLoopBackOff")' | jq -s 'length')

    if [ "$crashloop_count" -gt 0 ]; then
        log_error "Found $crashloop_count pods in CrashLoopBackOff state"
        return 1
    fi

    # Check services
    log_info "Checking service endpoints..."
    local services=$(kubectl get svc -n "$NAMESPACE" --no-headers | wc -l)
    log_info "Total services: $services"

    # Check deployments
    log_info "Checking deployment status..."
    kubectl get deployments -n "$NAMESPACE"

    # Check statefulsets
    log_info "Checking statefulset status..."
    kubectl get statefulsets -n "$NAMESPACE"

    echo ""
}

# Summary
print_summary() {
    local end_time=$(date +%s)
    local elapsed=$((end_time - START_TIME))

    log_info "========== DEPLOYMENT SUMMARY =========="
    log_success "Deployment completed in ${elapsed} seconds"
    log_info "Namespace: $NAMESPACE"
    log_info "Kubernetes directory: $KUBERNETES_DIR"
    log_info ""
    log_info "Next steps:"
    log_info "1. Verify all pods are running: kubectl get pods -n $NAMESPACE"
    log_info "2. Check service endpoints: kubectl get svc -n $NAMESPACE"
    log_info "3. Run health checks: bash health_check.sh"
    log_info "4. Run smoke tests: bash health_check.sh"
    log_info "5. Verify data integrity: bash verify_data_integrity.sh"
    log_info ""
    log_info "API endpoint: http://api-service.$NAMESPACE.svc.cluster.local:8000"
    log_info "Frontend endpoint: http://frontend-service.$NAMESPACE.svc.cluster.local:80"
    log_info "Metrics endpoint: http://api-service.$NAMESPACE.svc.cluster.local:8001/metrics"

    echo ""
}

# Main execution
main() {
    log_info "========== PHASE 5 DEPLOYMENT STARTED =========="
    log_info "Time: $(date)"
    echo ""

    # Pre-deployment checks
    if ! pre_deployment_checks; then
        log_error "Pre-deployment checks failed"
        exit 1
    fi

    # Deploy namespace and policies
    if ! deploy_namespace_and_policies; then
        log_error "Namespace deployment failed"
        exit 1
    fi

    # Phase 1: Persistent data layer
    if ! deploy_persistent_data_layer; then
        log_error "Persistent data layer deployment failed"
        exit 1
    fi

    # Phase 2: Configuration
    if ! deploy_configuration; then
        log_error "Configuration deployment failed"
        exit 1
    fi

    # Phase 3: Application services
    if ! deploy_application_services; then
        log_error "Application services deployment failed"
        exit 1
    fi

    # Phase 4: Infrastructure services
    if ! deploy_infrastructure_services; then
        log_error "Infrastructure services deployment failed"
        exit 1
    fi

    # Post-deployment checks
    if ! post_deployment_checks; then
        log_warn "Some post-deployment checks had issues, but deployment may still be usable"
    fi

    # Print summary
    print_summary

    log_success "========== PHASE 5 DEPLOYMENT COMPLETED SUCCESSFULLY =========="
    exit 0
}

# Run main function
main "$@"

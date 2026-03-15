#!/bin/bash

################################################################################
# Phase 5 Health Check Script
# Purpose: Verify all services are running and healthy
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

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNED=0

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((CHECKS_PASSED++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((CHECKS_FAILED++))
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((CHECKS_WARNED++))
}

# Configuration
NAMESPACE="quran-system"
API_SERVICE="api-service.$NAMESPACE.svc.cluster.local"
FRONTEND_SERVICE="frontend-service.$NAMESPACE.svc.cluster.local"
WORKER_SERVICE="worker-service.$NAMESPACE.svc.cluster.local"
POSTGRES_SERVICE="postgres-0.postgres-service.$NAMESPACE.svc.cluster.local"
NEO4J_SERVICE="neo4j-0.neo4j-service.$NAMESPACE.svc.cluster.local"
REDIS_SERVICE="redis-0.redis-service.$NAMESPACE.svc.cluster.local"
MILVUS_SERVICE="milvus-0.milvus-service.$NAMESPACE.svc.cluster.local"

# Function to check pod status
check_pod_status() {
    local app=$1
    local expected_replicas=${2:-1}

    log_info "Checking pod status for $app..."

    local running=$(kubectl get pods -n "$NAMESPACE" -l "app=$app" --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
    local total=$(kubectl get pods -n "$NAMESPACE" -l "app=$app" --no-headers 2>/dev/null | wc -l)

    if [ "$running" -eq "$expected_replicas" ]; then
        log_pass "$app: $running/$total pods running"
    else
        log_fail "$app: $running/$total pods running (expected $expected_replicas)"
    fi
}

# Function to check deployment status
check_deployment_status() {
    local deployment=$1

    log_info "Checking deployment status for $deployment..."

    local available=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null)

    if [ "$available" = "True" ]; then
        log_pass "$deployment deployment is available"
    else
        log_fail "$deployment deployment is not available"
    fi
}

# Function to check statefulset status
check_statefulset_status() {
    local statefulset=$1
    local expected_replicas=${2:-3}

    log_info "Checking statefulset status for $statefulset..."

    local ready=$(kubectl get statefulset "$statefulset" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")

    if [ "$ready" -eq "$expected_replicas" ]; then
        log_pass "$statefulset: $ready/$expected_replicas replicas ready"
    else
        log_fail "$statefulset: $ready/$expected_replicas replicas ready"
    fi
}

# Function to check HTTP endpoint
check_http_endpoint() {
    local service=$1
    local port=$2
    local path=${3:-"/"}

    log_info "Checking HTTP endpoint: http://$service:$port$path"

    # Try to get response from the service
    local http_code=$(curl -s -w "%{http_code}" -o /dev/null "http://$service:$port$path" 2>/dev/null || echo "000")

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ] || [ "$http_code" = "204" ]; then
        log_pass "HTTP endpoint $service:$port$path returned $http_code"
    elif [ "$http_code" = "301" ] || [ "$http_code" = "302" ] || [ "$http_code" = "307" ] || [ "$http_code" = "308" ]; then
        log_warn "HTTP endpoint $service:$port$path returned redirect $http_code"
    else
        log_fail "HTTP endpoint $service:$port$path returned $http_code"
    fi
}

# Function to check TCP port
check_tcp_port() {
    local host=$1
    local port=$2
    local service_name=${3:-"$host:$port"}

    log_info "Checking TCP port for $service_name..."

    if timeout 5 bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null; then
        log_pass "TCP connection to $service_name succeeded"
    else
        log_fail "TCP connection to $service_name failed"
    fi
}

# Function to check service endpoints
check_service_endpoints() {
    log_info ""
    log_info "========== CHECKING SERVICE ENDPOINTS =========="

    local api_endpoint=$(kubectl get service api-service -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}' 2>/dev/null)
    local frontend_endpoint=$(kubectl get service frontend-service -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}' 2>/dev/null)
    local worker_endpoint=$(kubectl get service worker-service -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}' 2>/dev/null)

    if [ -z "$api_endpoint" ]; then
        log_fail "API service endpoint not found"
    else
        log_pass "API service endpoint: $api_endpoint:8000"
    fi

    if [ -z "$frontend_endpoint" ]; then
        log_fail "Frontend service endpoint not found"
    else
        log_pass "Frontend service endpoint: $frontend_endpoint:80"
    fi

    if [ -z "$worker_endpoint" ]; then
        log_fail "Worker service endpoint not found"
    else
        log_pass "Worker service endpoint: $worker_endpoint:5000"
    fi
}

# Function to check pod crashes
check_pod_crashes() {
    log_info ""
    log_info "========== CHECKING FOR POD CRASHES =========="

    local crashloop_pods=$(kubectl get pods -n "$NAMESPACE" -o json 2>/dev/null | jq -r '.items[] | select(.status.containerStatuses[]? and (.status.containerStatuses[0].state.waiting.reason=="CrashLoopBackOff")) | .metadata.name' 2>/dev/null || echo "")

    if [ -z "$crashloop_pods" ]; then
        log_pass "No pods in CrashLoopBackOff state"
    else
        log_fail "Pods in CrashLoopBackOff state: $crashloop_pods"
    fi

    local failed_pods=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Failed --no-headers 2>/dev/null | wc -l)

    if [ "$failed_pods" -eq 0 ]; then
        log_pass "No failed pods"
    else
        log_fail "$failed_pods failed pods found"
    fi
}

# Function to check resource usage
check_resource_usage() {
    log_info ""
    log_info "========== CHECKING RESOURCE USAGE =========="

    log_info "Pod resource requests and limits:"
    kubectl get pods -n "$NAMESPACE" -o json 2>/dev/null | jq -r '.items[] | "\(.metadata.name): CPU \(.spec.containers[0].resources.requests.cpu) / \(.spec.containers[0].resources.limits.cpu), Memory \(.spec.containers[0].resources.requests.memory) / \(.spec.containers[0].resources.limits.memory)"' | while read -r line; do
        log_info "$line"
    done
}

# Function to check persistent volumes
check_persistent_volumes() {
    log_info ""
    log_info "========== CHECKING PERSISTENT VOLUMES =========="

    local pvcs=$(kubectl get pvc -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
    local pvcs_bound=$(kubectl get pvc -n "$NAMESPACE" --field-selector=status.phase=Bound --no-headers 2>/dev/null | wc -l)

    if [ "$pvcs" -eq 0 ]; then
        log_pass "No persistent volume claims"
    elif [ "$pvcs" -eq "$pvcs_bound" ]; then
        log_pass "All $pvcs PVCs are bound"
    else
        log_fail "$pvcs_bound/$pvcs PVCs are bound"
    fi
}

# Main execution
main() {
    log_info "========== PHASE 5 HEALTH CHECK =========="
    log_info "Time: $(date)"
    log_info "Namespace: $NAMESPACE"
    echo ""

    # Check cluster access
    if ! kubectl cluster-info > /dev/null 2>&1; then
        log_fail "Cannot access Kubernetes cluster"
        exit 1
    fi
    log_pass "Kubernetes cluster accessible"

    echo ""
    log_info "========== CHECKING POD STATUS =========="
    check_pod_status "postgres" 3
    check_pod_status "neo4j" 3
    check_pod_status "redis" 3
    check_pod_status "milvus" 3
    check_pod_status "api" 3
    check_pod_status "frontend" 3
    check_pod_status "worker" 5

    echo ""
    log_info "========== CHECKING DEPLOYMENT STATUS =========="
    check_deployment_status "api"
    check_deployment_status "frontend"
    check_deployment_status "worker"

    echo ""
    log_info "========== CHECKING STATEFULSET STATUS =========="
    check_statefulset_status "postgres" 3
    check_statefulset_status "neo4j" 3
    check_statefulset_status "redis" 3
    check_statefulset_status "milvus" 3

    # Check service endpoints
    check_service_endpoints

    # Check for crashes
    check_pod_crashes

    # Check resource usage
    check_resource_usage

    # Check persistent volumes
    check_persistent_volumes

    echo ""
    log_info "========== CHECKING API HEALTH =========="
    # Note: These checks require pod exec, adjust as needed
    log_info "To check API health, run:"
    log_info "  kubectl exec -it deployment/api -n $NAMESPACE -- curl http://localhost:8000/health"

    echo ""
    log_info "========== HEALTH CHECK SUMMARY =========="
    log_info "Passed: $CHECKS_PASSED"
    log_info "Failed: $CHECKS_FAILED"
    log_info "Warned: $CHECKS_WARNED"

    if [ $CHECKS_FAILED -eq 0 ]; then
        log_pass "All health checks passed!"
        exit 0
    else
        log_fail "Some health checks failed!"
        exit 1
    fi
}

# Run main function
main "$@"

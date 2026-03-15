#!/bin/bash
# Kubernetes Deployment Validation Script
# Validates the deployed infrastructure

set -e

NAMESPACE="quran-system"
CHECKS_PASSED=0
CHECKS_FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((CHECKS_PASSED++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((CHECKS_FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Validation checks
print_header "Cluster Connectivity"

if kubectl cluster-info &> /dev/null; then
    check_pass "Kubernetes cluster accessible"
else
    check_fail "Kubernetes cluster not accessible"
    exit 1
fi

print_header "Namespace"

if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    check_pass "Namespace '$NAMESPACE' exists"
else
    check_fail "Namespace '$NAMESPACE' not found"
fi

print_header "StatefulSets"

STATEFULSETS=("postgres" "neo4j" "redis" "milvus")
for ss in "${STATEFULSETS[@]}"; do
    READY=$(kubectl get statefulset -n "$NAMESPACE" "$ss" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
    DESIRED=$(kubectl get statefulset -n "$NAMESPACE" "$ss" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")

    if [ "$READY" = "$DESIRED" ] && [ "$READY" != "0" ]; then
        check_pass "StatefulSet '$ss' ready ($READY/$DESIRED replicas)"
    else
        check_fail "StatefulSet '$ss' not ready ($READY/$DESIRED replicas)"
    fi
done

print_header "Deployments"

DEPLOYMENTS=("api" "frontend" "worker" "prometheus" "grafana")
for deploy in "${DEPLOYMENTS[@]}"; do
    READY=$(kubectl get deployment -n "$NAMESPACE" "$deploy" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
    DESIRED=$(kubectl get deployment -n "$NAMESPACE" "$deploy" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")

    if [ "$READY" = "$DESIRED" ] && [ "$READY" != "0" ]; then
        check_pass "Deployment '$deploy' ready ($READY/$DESIRED replicas)"
    else
        if [ "$DESIRED" != "0" ]; then
            check_fail "Deployment '$deploy' not ready ($READY/$DESIRED replicas)"
        fi
    fi
done

print_header "Services"

SERVICES=("api-service" "frontend-service" "postgres-service" "neo4j-service" "redis-service" "milvus-service" "prometheus" "grafana")
for svc in "${SERVICES[@]}"; do
    if kubectl get service -n "$NAMESPACE" "$svc" &> /dev/null; then
        check_pass "Service '$svc' exists"
    else
        check_fail "Service '$svc' not found"
    fi
done

print_header "ConfigMaps & Secrets"

if kubectl get configmap -n "$NAMESPACE" quran-config &> /dev/null; then
    check_pass "ConfigMap 'quran-config' exists"
else
    check_fail "ConfigMap 'quran-config' not found"
fi

if kubectl get secret -n "$NAMESPACE" quran-secrets &> /dev/null; then
    check_pass "Secret 'quran-secrets' exists"
else
    check_fail "Secret 'quran-secrets' not found"
fi

print_header "PersistentVolumes"

PVC_COUNT=$(kubectl get pvc -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
if [ "$PVC_COUNT" -gt 0 ]; then
    check_pass "PersistentVolumeClaims found: $PVC_COUNT"
    kubectl get pvc -n "$NAMESPACE" | tail -n +2 | while read -r line; do
        PVC_NAME=$(echo "$line" | awk '{print $1}')
        STATUS=$(echo "$line" | awk '{print $2}')
        if [ "$STATUS" = "Bound" ]; then
            check_pass "PVC '$PVC_NAME' is bound"
        else
            check_fail "PVC '$PVC_NAME' status: $STATUS"
        fi
    done
else
    check_fail "No PersistentVolumeClaims found"
fi

print_header "Ingress"

if kubectl get ingress -n "$NAMESPACE" &> /dev/null; then
    check_pass "Ingress rules exist"
else
    check_warn "No Ingress rules found"
fi

print_header "Pod Status"

echo ""
echo "Pod Summary:"
kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | while read -r line; do
    STATUS=$(echo "$line" | awk '{print $3}')
    POD_NAME=$(echo "$line" | awk '{print $1}')

    if [ "$STATUS" = "Running" ]; then
        check_pass "Pod '$POD_NAME' is Running"
    elif [ "$STATUS" = "Pending" ]; then
        check_warn "Pod '$POD_NAME' is Pending"
    else
        check_fail "Pod '$POD_NAME' status: $STATUS"
    fi
done

print_header "Resource Usage"

echo ""
echo "Pod Resource Usage:"
kubectl top pods -n "$NAMESPACE" 2>/dev/null || check_warn "Metrics server not ready (this is normal for first few minutes)"

print_header "HPA Status"

HPAS=$(kubectl get hpa -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
if [ "$HPAS" -gt 0 ]; then
    check_pass "Horizontal Pod Autoscalers configured: $HPAS"
    kubectl get hpa -n "$NAMESPACE" | tail -n +2 | while read -r line; do
        HPA_NAME=$(echo "$line" | awk '{print $1}')
        echo "  - $HPA_NAME"
    done
else
    check_fail "No Horizontal Pod Autoscalers found"
fi

print_header "Recent Events"

echo ""
echo "Recent cluster events:"
kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | tail -n 10

print_header "Deployment Validation Results"

TOTAL=$((CHECKS_PASSED + CHECKS_FAILED))
PASS_RATE=$((CHECKS_PASSED * 100 / TOTAL))

echo ""
echo "Results:"
echo "  Checks Passed: $CHECKS_PASSED"
echo "  Checks Failed: $CHECKS_FAILED"
echo "  Total Checks: $TOTAL"
echo "  Pass Rate: $PASS_RATE%"
echo ""

if [ "$CHECKS_FAILED" -eq 0 ]; then
    echo -e "${GREEN}✓ All deployment checks passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ Some checks failed. Please review the output above.${NC}"
    exit 1
fi

#!/bin/bash

################################################################################
# Phase 3 Embedding Service - Pre-Deployment Validation Script
#
# Validates that all Phase 3 optimization components are properly configured
# before deployment to Kubernetes.
#
# Usage: bash validate-phase3-setup.sh
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Phase 3 Embedding Service - Validation Checklist              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Helper functions
print_check() {
    local message=$1
    echo -ne "Checking: $message... "
}

print_pass() {
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
}

print_fail() {
    local error=$1
    echo -e "${RED}✗ FAIL${NC}"
    echo -e "${RED}  Error: $error${NC}"
    ((FAILED++))
}

print_warn() {
    local warning=$1
    echo -e "${YELLOW}⚠ WARN${NC}"
    echo -e "${YELLOW}  Warning: $warning${NC}"
    ((WARNINGS++))
}

# Section 1: File Existence Checks
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 1: Required Files${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

files_to_check=(
    "kubernetes/09-embedding-worker-hpa.yaml"
    "kubernetes/08-worker-deployment-optimized.yaml"
    "kubernetes/PHASE_3_OPTIMIZATION_GUIDE.md"
    "kubernetes/monitoring/embedding-monitoring-dashboard.json"
    "kubernetes/monitoring/embedding_monitoring.py"
    "quran-core/src/embedding/memory_optimization.py"
    "PHASE_3_SCALING_REPORT.md"
)

for file in "${files_to_check[@]}"; do
    print_check "File exists: $file"
    if [ -f "$REPO_ROOT/$file" ]; then
        print_pass
    else
        print_fail "File not found: $REPO_ROOT/$file"
    fi
done

echo ""

# Section 2: YAML Validation
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 2: YAML Configuration Validation${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Check for kubectl availability
print_check "kubectl is installed"
if command -v kubectl &> /dev/null; then
    print_pass
else
    print_warn "kubectl not found - YAML validation skipped"
fi

# Validate HPA YAML
print_check "HPA configuration is valid"
if kubectl apply -f "$REPO_ROOT/kubernetes/09-embedding-worker-hpa.yaml" --dry-run=client &>/dev/null; then
    print_pass
else
    print_fail "HPA YAML is malformed"
fi

# Validate Worker Deployment YAML
print_check "Worker deployment configuration is valid"
if kubectl apply -f "$REPO_ROOT/kubernetes/08-worker-deployment-optimized.yaml" --dry-run=client &>/dev/null; then
    print_pass
else
    print_fail "Worker deployment YAML is malformed"
fi

echo ""

# Section 3: Python Module Validation
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 3: Python Module Validation${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Check Python syntax
print_check "Memory optimization module has valid Python syntax"
if python3 -m py_compile "$REPO_ROOT/quran-core/src/embedding/memory_optimization.py" 2>/dev/null; then
    print_pass
else
    print_fail "Python syntax error in memory_optimization.py"
fi

print_check "Monitoring script has valid Python syntax"
if python3 -m py_compile "$REPO_ROOT/kubernetes/monitoring/embedding_monitoring.py" 2>/dev/null; then
    print_pass
else
    print_fail "Python syntax error in embedding_monitoring.py"
fi

# Check for required imports in memory optimization module
print_check "Memory optimization module has required imports"
required_imports=("gc" "logging" "mmap" "struct" "pathlib" "typing" "numpy")
missing_imports=()

for import in "${required_imports[@]}"; do
    if grep -q "import $import\|from $import" "$REPO_ROOT/quran-core/src/embedding/memory_optimization.py"; then
        :
    else
        missing_imports+=("$import")
    fi
done

if [ ${#missing_imports[@]} -eq 0 ]; then
    print_pass
else
    print_warn "Missing imports: ${missing_imports[*]}"
fi

echo ""

# Section 4: Configuration Validation
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 4: Configuration Values${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# HPA configuration checks
print_check "HPA minReplicas is set to 2"
if grep -q "minReplicas: 2" "$REPO_ROOT/kubernetes/09-embedding-worker-hpa.yaml"; then
    print_pass
else
    print_fail "HPA minReplicas not configured correctly"
fi

print_check "HPA maxReplicas is set to 6"
if grep -q "maxReplicas: 6" "$REPO_ROOT/kubernetes/09-embedding-worker-hpa.yaml"; then
    print_pass
else
    print_fail "HPA maxReplicas not configured correctly"
fi

print_check "HPA has CPU metric (70% threshold)"
if grep -q "averageUtilization: 70" "$REPO_ROOT/kubernetes/09-embedding-worker-hpa.yaml"; then
    print_pass
else
    print_fail "HPA CPU metric not configured correctly"
fi

# Worker deployment checks
print_check "Worker deployment has memory optimization enabled"
if grep -q "EMBEDDING_STREAMING_MODE.*true" "$REPO_ROOT/kubernetes/08-worker-deployment-optimized.yaml"; then
    print_pass
else
    print_fail "Memory streaming mode not enabled in worker deployment"
fi

print_check "Worker has Neo4j batch size set to 100"
if grep -q "NEO4J_BATCH_SIZE.*100" "$REPO_ROOT/kubernetes/08-worker-deployment-optimized.yaml"; then
    print_pass
else
    print_fail "Neo4j batch size not set to 100"
fi

print_check "Worker has connection pool timeout set to 45s"
if grep -q "NEO4J_CONNECTION_POOL_TIMEOUT.*45" "$REPO_ROOT/kubernetes/08-worker-deployment-optimized.yaml"; then
    print_pass
else
    print_fail "Neo4j connection pool timeout not set correctly"
fi

print_check "Worker has GC interval set to 1000 vectors"
if grep -q "EMBEDDING_GC_INTERVAL.*1000" "$REPO_ROOT/kubernetes/08-worker-deployment-optimized.yaml"; then
    print_pass
else
    print_fail "GC interval not set correctly"
fi

echo ""

# Section 5: Documentation Validation
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 5: Documentation${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

print_check "Optimization guide has deployment instructions"
if grep -q "Phase 1: Deploy HPA\|Phase 2: Update Worker" "$REPO_ROOT/kubernetes/PHASE_3_OPTIMIZATION_GUIDE.md"; then
    print_pass
else
    print_fail "Optimization guide missing deployment instructions"
fi

print_check "Optimization guide has troubleshooting section"
if grep -q "Troubleshooting\|Issue:" "$REPO_ROOT/kubernetes/PHASE_3_OPTIMIZATION_GUIDE.md"; then
    print_pass
else
    print_fail "Optimization guide missing troubleshooting section"
fi

print_check "Scaling report documents all deliverables"
if grep -q "Deliverable\|Location\|Purpose" "$REPO_ROOT/PHASE_3_SCALING_REPORT.md"; then
    print_pass
else
    print_fail "Scaling report missing deliverables section"
fi

print_check "Scaling report includes success criteria"
if grep -q "Success Criteria\|Checklist" "$REPO_ROOT/PHASE_3_SCALING_REPORT.md"; then
    print_pass
else
    print_fail "Scaling report missing success criteria"
fi

echo ""

# Section 6: Kubernetes Cluster Checks (if connected)
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 6: Kubernetes Cluster Readiness${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

print_check "Connected to Kubernetes cluster"
if kubectl cluster-info &>/dev/null; then
    print_pass

    # Check if namespace exists
    print_check "quran-system namespace exists"
    if kubectl get namespace quran-system &>/dev/null; then
        print_pass
    else
        print_fail "quran-system namespace not found"
    fi

    # Check for existing worker deployment
    print_check "Worker deployment exists"
    if kubectl get deployment/worker -n quran-system &>/dev/null; then
        print_pass

        # Check current replicas
        print_check "Worker deployment has 2+ replicas"
        replicas=$(kubectl get deployment/worker -n quran-system -o jsonpath='{.spec.replicas}')
        if [ "$replicas" -ge 2 ]; then
            echo -ne " (current: $replicas) "
            print_pass
        else
            print_warn "Worker deployment has fewer than 2 replicas (current: $replicas)"
        fi
    else
        print_warn "Worker deployment not found (new deployment will be created)"
    fi

    # Check for Redis
    print_check "Redis is available"
    if kubectl get pod -n quran-system -l app=redis &>/dev/null; then
        print_pass
    else
        print_warn "Redis pod not found (required for queue metrics)"
    fi

    # Check for Neo4j
    print_check "Neo4j is available"
    if kubectl get pod -n quran-system -l app=neo4j &>/dev/null; then
        print_pass
    else
        print_warn "Neo4j pod not found (required for memory monitoring)"
    fi

    # Check for Prometheus
    print_check "Prometheus is available"
    if kubectl get pod -n quran-system -l app=prometheus &>/dev/null; then
        print_pass
    else
        print_warn "Prometheus pod not found (required for HPA custom metrics)"
    fi

else
    print_warn "Not connected to Kubernetes cluster (skipping cluster checks)"
fi

echo ""

# Final Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}VALIDATION SUMMARY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

total=$((PASSED + FAILED + WARNINGS))

if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}✓ PASSED: $PASSED/$total checks${NC}"
else
    echo -e "${RED}✗ FAILED: $FAILED check(s)${NC}"
fi

if [ "$WARNINGS" -gt 0 ]; then
    echo -e "${YELLOW}⚠ WARNINGS: $WARNINGS check(s)${NC}"
fi

echo ""

if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}All checks passed! Ready for Phase 3 deployment.${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review: kubernetes/PHASE_3_OPTIMIZATION_GUIDE.md"
    echo "  2. Deploy HPA: kubectl apply -f kubernetes/09-embedding-worker-hpa.yaml"
    echo "  3. Update workers: kubectl apply -f kubernetes/08-worker-deployment-optimized.yaml"
    echo "  4. Monitor: python kubernetes/monitoring/embedding_monitoring.py"
    exit 0
else
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}$FAILED critical issue(s) must be resolved before deployment.${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    exit 1
fi

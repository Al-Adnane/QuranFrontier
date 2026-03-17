#!/bin/bash

################################################################################
# PHASE 5: DEPLOYMENT VERIFICATION
# Comprehensive verification of production deployment
# Verifies: database, Neo4j, embeddings, security, health checks, metrics
################################################################################

set -e  # Exit on error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="/tmp/phase5_verification_$(date +%s).log"

# Counters
PASSED=0
FAILED=0
WARNINGS=0

################################################################################
# Helper Functions
################################################################################

log() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"
    ((PASSED++))
}

error() {
    echo -e "${RED}✗${NC} $1" | tee -a "$LOG_FILE"
    ((FAILED++))
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1" | tee -a "$LOG_FILE"
    ((WARNINGS++))
}

header() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${BLUE}=== $1 ===${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

################################################################################
# Phase 5A: Database Verification
################################################################################

verify_database() {
    header "DATABASE VERIFICATION"

    # Check PostgreSQL connection
    log "Checking PostgreSQL connection..."
    python3 << 'EOF' >> "$LOG_FILE" 2>&1
import psycopg2
import os
import sys

try:
    db_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/quran")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Check tables exist
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema='public'
    """)
    tables = [row[0] for row in cur.fetchall()]

    required = ["verses", "tafsirs", "hadiths", "users", "audit_logs"]
    missing = [t for t in required if t not in tables]

    if missing:
        print(f"ERROR: Missing tables: {missing}", file=sys.stderr)
        sys.exit(1)

    # Check record counts
    cur.execute("SELECT COUNT(*) FROM verses")
    verse_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tafsirs")
    tafsir_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM hadiths")
    hadith_count = cur.fetchone()[0]

    print(f"PostgreSQL OK:")
    print(f"  - Verses: {verse_count}")
    print(f"  - Tafsirs: {tafsir_count}")
    print(f"  - Hadiths: {hadith_count}")

    cur.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
EOF

    if [ $? -eq 0 ]; then
        success "PostgreSQL verification passed"
    else
        error "PostgreSQL verification failed"
    fi
}

################################################################################
# Phase 5B: Neo4j Verification
################################################################################

verify_neo4j() {
    header "NEO4J VERIFICATION"

    log "Checking Neo4j connection..."
    python3 << 'EOF' >> "$LOG_FILE" 2>&1
import os
import sys

try:
    from neo4j import GraphDatabase

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()

    with driver.session() as session:
        result = session.run("MATCH (v:Verse) RETURN COUNT(v) as count")
        verse_count = result.single()["count"]

        result = session.run("MATCH ()-[r]->() RETURN COUNT(r) as count")
        relationship_count = result.single()["count"]

    print(f"Neo4j OK:")
    print(f"  - Verses: {verse_count}")
    print(f"  - Relationships: {relationship_count}")

    driver.close()
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
EOF

    if [ $? -eq 0 ]; then
        success "Neo4j verification passed"
    else
        warning "Neo4j verification failed (may not be configured)"
    fi
}

################################################################################
# Phase 5C: Embeddings Verification
################################################################################

verify_embeddings() {
    header "EMBEDDINGS VERIFICATION"

    log "Checking embeddings file..."
    python3 << 'EOF' >> "$LOG_FILE" 2>&1
import json
import sys

try:
    with open("../embeddings/corpus_embeddings.json") as f:
        data = json.load(f)

    verse_count = len(data.get("verses", []))
    tafsir_count = len(data.get("tafsirs", []))
    hadith_count = len(data.get("hadiths", []))

    if verse_count > 0:
        embedding_dim = len(data["verses"][0]["embedding"])
    else:
        embedding_dim = 0

    if embedding_dim != 768:
        print(f"ERROR: Expected 768-dim embeddings, got {embedding_dim}", file=sys.stderr)
        sys.exit(1)

    print(f"Embeddings OK:")
    print(f"  - Verses: {verse_count} x {embedding_dim}")
    print(f"  - Tafsirs: {tafsir_count}")
    print(f"  - Hadiths: {hadith_count}")
except FileNotFoundError:
    print(f"WARNING: Embeddings file not found", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
EOF

    if [ $? -eq 0 ]; then
        success "Embeddings verification passed"
    else
        warning "Embeddings verification failed (may not be generated yet)"
    fi
}

################################################################################
# Phase 5D: Security Verification
################################################################################

verify_security() {
    header "SECURITY VERIFICATION"

    log "Checking SQL injection protection..."
    python3 << 'EOF' >> "$LOG_FILE" 2>&1
import sys
sys.path.insert(0, ".")

from src.api.security import QueryValidator

test_cases = [
    ("'; DROP TABLE verses; --", False),
    ("1' OR '1'='1", False),
    ("mercy and compassion", True),
    ("Quranic wisdom", True),
]

for query, should_pass in test_cases:
    try:
        result = QueryValidator.validate_search_query(query)
        if should_pass:
            print(f"✓ Accepted: {query[:30]}")
        else:
            print(f"ERROR: Should have rejected: {query}", file=sys.stderr)
            sys.exit(1)
    except ValueError:
        if not should_pass:
            print(f"✓ Blocked: {query[:30]}")
        else:
            print(f"ERROR: Should have accepted: {query}", file=sys.stderr)
            sys.exit(1)
EOF

    if [ $? -eq 0 ]; then
        success "Security verification passed"
    else
        error "Security verification failed"
    fi
}

################################################################################
# Phase 5E: API Health Checks
################################################################################

verify_api_health() {
    header "API HEALTH CHECKS"

    # Check if API is running
    log "Checking API connectivity..."

    for i in {1..5}; do
        response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")

        if [ "$response" = "200" ] || [ "$response" = "503" ]; then
            success "API responding (HTTP $response)"
            break
        elif [ $i -lt 5 ]; then
            warning "API not responding (attempt $i/5), retrying..."
            sleep 2
        else
            error "API not responding"
        fi
    done
}

################################################################################
# Phase 5F: Metrics Verification
################################################################################

verify_metrics() {
    header "METRICS VERIFICATION"

    log "Checking Prometheus metrics endpoint..."

    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/metrics 2>/dev/null || echo "000")

    if [ "$response" = "200" ]; then
        success "Metrics endpoint responding"

        # Get metrics content
        metrics=$(curl -s http://localhost:8000/metrics 2>/dev/null)

        if echo "$metrics" | grep -q "api_requests_total"; then
            success "Request metrics being collected"
        fi

        if echo "$metrics" | grep -q "api_request_duration_seconds"; then
            success "Latency metrics being collected"
        fi
    elif [ "$response" = "404" ]; then
        warning "Metrics endpoint not configured"
    else
        error "Metrics endpoint error (HTTP $response)"
    fi
}

################################################################################
# Phase 5G: Integration Tests
################################################################################

verify_tests() {
    header "RUNNING INTEGRATION TESTS"

    log "Running pytest suite..."

    cd "$PROJECT_DIR"

    if python -m pytest tests/phase3/test_production_integration.py -v --tb=short >> "$LOG_FILE" 2>&1; then
        success "Integration tests passed"
    else
        warning "Some integration tests failed (see log)"
    fi
}

################################################################################
# Phase 5H: Docker Verification
################################################################################

verify_docker() {
    header "DOCKER VERIFICATION"

    log "Checking Docker Compose..."

    if [ -f "$PROJECT_DIR/docker-compose.yml" ]; then
        success "docker-compose.yml found"

        # Validate YAML
        if python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml'))" 2>/dev/null; then
            success "docker-compose.yml is valid YAML"
        else
            error "docker-compose.yml is invalid YAML"
        fi
    else
        warning "docker-compose.yml not found"
    fi
}

################################################################################
# Phase 5I: Kubernetes Verification
################################################################################

verify_kubernetes() {
    header "KUBERNETES VERIFICATION"

    log "Checking Kubernetes manifests..."

    k8s_dir="$PROJECT_DIR/k8s"

    if [ -d "$k8s_dir" ]; then
        success "K8s directory found"

        # Check for required manifests
        required_files=("deployment.yaml" "service.yaml" "configmap.yaml" "secret.yaml")

        for file in "${required_files[@]}"; do
            if [ -f "$k8s_dir/$file" ]; then
                success "  - $file present"
            else
                warning "  - $file missing"
            fi
        done
    else
        warning "K8s directory not found"
    fi
}

################################################################################
# Summary
################################################################################

print_summary() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${BLUE}=== DEPLOYMENT VERIFICATION SUMMARY ===${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo -e "${GREEN}Passed:${NC}  $PASSED" | tee -a "$LOG_FILE"
    echo -e "${RED}Failed:${NC}  $FAILED" | tee -a "$LOG_FILE"
    echo -e "${YELLOW}Warnings:${NC} $WARNINGS" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"

    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ Deployment verification PASSED${NC}" | tee -a "$LOG_FILE"
        return 0
    else
        echo -e "${RED}✗ Deployment verification FAILED${NC}" | tee -a "$LOG_FILE"
        return 1
    fi
}

################################################################################
# Main Execution
################################################################################

main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║        QuranFrontier - Phase 5: Deployment Verification        ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    log "Starting deployment verification..."
    log "Log file: $LOG_FILE"

    # Run all verification phases
    verify_database
    verify_neo4j
    verify_embeddings
    verify_security
    verify_api_health
    verify_metrics
    verify_tests
    verify_docker
    verify_kubernetes

    # Print summary
    print_summary
}

# Run main
main
exit $?

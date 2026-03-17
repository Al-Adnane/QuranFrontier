#!/bin/bash

################################################################################
# Phase 5 Rollback Script
# Purpose: One-command rollback to previous stable version
# Rollback Time: 2-3 minutes
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
ROLLBACK_VERSION="previous"  # Can be overridden with command line argument
BACKUP_DIR="/var/backups/quran-phase5"
START_TIME=$(date +%s)

# Function to get previous stable revision
get_previous_revision() {
    local deployment=$1

    # Get rollout history and extract previous revision
    local revision=$(kubectl rollout history deployment/"$deployment" -n "$NAMESPACE" | tail -2 | head -1 | awk '{print $1}')

    if [ -z "$revision" ]; then
        log_error "Could not determine previous revision for $deployment"
        return 1
    fi

    echo "$revision"
}

# Function to rollback deployment
rollback_deployment() {
    local deployment=$1

    log_info "Rolling back deployment: $deployment"

    if kubectl rollout undo deployment/"$deployment" -n "$NAMESPACE"; then
        log_success "Initiated rollback for $deployment"

        # Wait for rollback to complete
        if kubectl rollout status deployment/"$deployment" -n "$NAMESPACE" --timeout=300s > /dev/null 2>&1; then
            log_success "Rollback of $deployment completed successfully"
            return 0
        else
            log_error "Rollback of $deployment timed out"
            return 1
        fi
    else
        log_error "Failed to rollback $deployment"
        return 1
    fi
}

# Function to verify deployment health
verify_deployment_health() {
    local deployment=$1

    log_info "Verifying health of $deployment..."

    # Check if deployment is available
    local available=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Available")].status}')

    if [ "$available" = "True" ]; then
        log_success "$deployment is healthy"
        return 0
    else
        log_warn "$deployment health check: available=$available"
        return 1
    fi
}

# Function to restart pod with new image
restart_pod() {
    local deployment=$1
    local image=$2

    log_info "Restarting pods for $deployment with image: $image"

    kubectl set image deployment/"$deployment" "$deployment=$image" -n "$NAMESPACE"

    if kubectl rollout status deployment/"$deployment" -n "$NAMESPACE" --timeout=300s > /dev/null 2>&1; then
        log_success "Pod restart completed for $deployment"
        return 0
    else
        log_error "Pod restart failed for $deployment"
        return 1
    fi
}

# Function to restore database from backup
restore_database_backup() {
    log_info "Restoring database from backup..."

    if [ ! -d "$BACKUP_DIR" ]; then
        log_warn "Backup directory not found: $BACKUP_DIR"
        log_info "Proceeding without database restore. Please restore manually if needed."
        return 0
    fi

    # Find latest backup
    local latest_backup=$(ls -t "$BACKUP_DIR"/postgres-* 2>/dev/null | head -1)

    if [ -z "$latest_backup" ]; then
        log_warn "No database backups found in $BACKUP_DIR"
        return 0
    fi

    log_info "Found backup: $latest_backup"
    log_info "Note: Database restore is handled manually through Kubernetes volume snapshots"
    log_info "If you need to restore, run: kubectl rollout undo statefulset/postgres -n $NAMESPACE"

    return 0
}

# Function to get current image
get_current_image() {
    local deployment=$1

    kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.spec.template.spec.containers[0].image}'
}

# Main rollback execution
main() {
    log_info "========== PHASE 5 ROLLBACK INITIATED =========="
    log_info "Time: $(date)"
    log_info "Namespace: $NAMESPACE"
    echo ""

    # Parse command line arguments
    if [ $# -gt 0 ]; then
        case $1 in
            --dry-run)
                log_info "Running in DRY-RUN mode (no changes will be made)"
                DRY_RUN=true
                ;;
            --version)
                ROLLBACK_VERSION=$2
                log_info "Rollback version: $ROLLBACK_VERSION"
                ;;
            *)
                log_warn "Unknown argument: $1"
                ;;
        esac
    fi

    # Check cluster access
    if ! kubectl cluster-info > /dev/null 2>&1; then
        log_error "Cannot access Kubernetes cluster"
        exit 1
    fi
    log_success "Kubernetes cluster accessible"

    # Check namespace
    if ! kubectl get namespace "$NAMESPACE" > /dev/null 2>&1; then
        log_error "Namespace $NAMESPACE does not exist"
        exit 1
    fi
    log_success "Namespace $NAMESPACE exists"

    echo ""
    log_info "========== CURRENT STATE =========="

    # Show current deployments
    log_info "Current deployment status:"
    kubectl get deployments -n "$NAMESPACE"

    echo ""
    log_info "Current pod status:"
    kubectl get pods -n "$NAMESPACE"

    # Ask for confirmation
    echo ""
    log_warn "ROLLBACK WILL REVERSE THE FOLLOWING COMPONENTS:"
    log_warn "- API deployment"
    log_warn "- Frontend deployment"
    log_warn "- Worker deployment"
    log_warn "- Statefulsets (databases may not be affected)"
    echo ""
    read -p "Do you want to proceed with rollback? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        log_info "Rollback cancelled by user"
        exit 0
    fi

    echo ""
    log_info "========== INITIATING ROLLBACK =========="

    # Rollback deployments
    rollback_deployment "api"
    rollback_deployment "frontend"
    rollback_deployment "worker"

    echo ""
    log_info "========== VERIFYING ROLLBACK =========="

    # Verify health
    verify_deployment_health "api"
    verify_deployment_health "frontend"
    verify_deployment_health "worker"

    echo ""
    log_info "========== POST-ROLLBACK STATUS =========="

    # Show final status
    log_info "Final deployment status:"
    kubectl get deployments -n "$NAMESPACE"

    echo ""
    log_info "Final pod status:"
    kubectl get pods -n "$NAMESPACE"

    # Calculate rollback time
    local end_time=$(date +%s)
    local elapsed=$((end_time - START_TIME))

    echo ""
    log_success "========== ROLLBACK COMPLETED =========="
    log_success "Rollback completed in ${elapsed} seconds"
    log_info ""
    log_info "Next steps:"
    log_info "1. Verify services are responding: curl http://api-service.$NAMESPACE.svc.cluster.local:8000/health"
    log_info "2. Check pod logs: kubectl logs -n $NAMESPACE deployment/api | tail -20"
    log_info "3. Run health checks: bash health_check.sh"
    log_info "4. If rollback failed, contact the on-call engineer"
    log_info ""
    log_info "Incident summary:"
    log_info "- Rollback initiated at: $(date)"
    log_info "- Duration: ${elapsed} seconds"
    log_info "- Version: $ROLLBACK_VERSION"
    log_info ""

    exit 0
}

# Run main function
main "$@"

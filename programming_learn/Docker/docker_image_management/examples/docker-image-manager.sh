#!/bin/bash

# Docker Image Management Automation Script
# Provides common operations for building, tagging, and managing Docker images

set -e

# Configuration
REGISTRY="myregistry.com"
PROJECT_NAME="myapp"
BUILD_DIR="."
DOCKERFILE="Dockerfile"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to build image
build_image() {
    local tag=${1:-latest}
    local dockerfile=${2:-$DOCKERFILE}
    
    log_info "Building image: ${PROJECT_NAME}:${tag}"
    
    docker build \
        --tag "${PROJECT_NAME}:${tag}" \
        --file "${dockerfile}" \
        "${BUILD_DIR}"
    
    log_info "Build completed successfully"
}

# Function to build multi-platform image
build_multiplatform() {
    local tag=${1:-latest}
    local dockerfile=${2:-$DOCKERFILE}
    
    log_info "Building multi-platform image: ${PROJECT_NAME}:${tag}"
    
    # Ensure buildx is available
    docker buildx create --name multiarch --use 2>/dev/null || true
    
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        --tag "${PROJECT_NAME}:${tag}" \
        --file "${dockerfile}" \
        --push \
        "${BUILD_DIR}"
    
    log_info "Multi-platform build completed successfully"
}

# Function to tag image for registry
tag_for_registry() {
    local local_tag=${1:-latest}
    local registry_tag=${2:-$local_tag}
    
    log_info "Tagging ${PROJECT_NAME}:${local_tag} for registry"
    
    docker tag "${PROJECT_NAME}:${local_tag}" "${REGISTRY}/${PROJECT_NAME}:${registry_tag}"
    
    log_info "Tagged as ${REGISTRY}/${PROJECT_NAME}:${registry_tag}"
}

# Function to push image to registry
push_image() {
    local tag=${1:-latest}
    
    log_info "Pushing ${REGISTRY}/${PROJECT_NAME}:${tag} to registry"
    
    docker push "${REGISTRY}/${PROJECT_NAME}:${tag}"
    
    log_info "Push completed successfully"
}

# Function to scan image for vulnerabilities
scan_image() {
    local tag=${1:-latest}
    
    log_info "Scanning ${PROJECT_NAME}:${tag} for vulnerabilities"
    
    if command -v trivy &> /dev/null; then
        trivy image "${PROJECT_NAME}:${tag}"
    elif command -v docker-scout &> /dev/null; then
        docker scout cves "${PROJECT_NAME}:${tag}"
    else
        log_warn "No vulnerability scanner found. Install trivy or docker scout."
    fi
}

# Function to clean up old images
cleanup_images() {
    log_info "Cleaning up unused Docker images"
    
    # Remove dangling images
    docker image prune -f
    
    # Remove old versions (keep last 5)
    docker images "${PROJECT_NAME}" --format "table {{.Tag}}\t{{.CreatedAt}}" | \
        tail -n +6 | \
        awk '{print $1}' | \
        xargs -r docker rmi "${PROJECT_NAME}:" 2>/dev/null || true
    
    log_info "Cleanup completed"
}

# Function to run image locally
run_local() {
    local tag=${1:-latest}
    local port=${2:-8080}
    
    log_info "Running ${PROJECT_NAME}:${tag} locally on port ${port}"
    
    docker run --rm -it \
        --name "${PROJECT_NAME}-dev" \
        -p "${port}:${port}" \
        "${PROJECT_NAME}:${tag}"
}

# Function to generate image metadata
generate_metadata() {
    local tag=${1:-latest}
    
    log_info "Generating metadata for ${PROJECT_NAME}:${tag}"
    
    # Get image information
    docker inspect "${PROJECT_NAME}:${tag}" > "image-metadata-${tag}.json"
    
    # Get image history
    docker history "${PROJECT_NAME}:${tag}" > "image-history-${tag}.txt"
    
    # Get image size information
    docker images "${PROJECT_NAME}:${tag}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" > "image-size-${tag}.txt"
    
    log_info "Metadata files generated"
}

# Function to show help
show_help() {
    cat << EOF
Docker Image Management Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    build [TAG] [DOCKERFILE]    Build Docker image
    build-multi [TAG]           Build multi-platform image
    tag [LOCAL_TAG] [REG_TAG]   Tag image for registry
    push [TAG]                  Push image to registry
    scan [TAG]                  Scan image for vulnerabilities
    cleanup                     Clean up old images
    run [TAG] [PORT]            Run image locally
    metadata [TAG]              Generate image metadata
    help                        Show this help message

Examples:
    $0 build v1.0.0
    $0 build-multi latest
    $0 tag latest v1.0.0
    $0 push v1.0.0
    $0 scan latest
    $0 run latest 3000

Environment Variables:
    REGISTRY        Registry URL (default: myregistry.com)
    PROJECT_NAME    Project name (default: myapp)
    BUILD_DIR       Build context directory (default: .)
    DOCKERFILE      Dockerfile name (default: Dockerfile)

EOF
}

# Main script logic
case "${1:-help}" in
    build)
        build_image "$2" "$3"
        ;;
    build-multi)
        build_multiplatform "$2"
        ;;
    tag)
        tag_for_registry "$2" "$3"
        ;;
    push)
        push_image "$2"
        ;;
    scan)
        scan_image "$2"
        ;;
    cleanup)
        cleanup_images
        ;;
    run)
        run_local "$2" "$3"
        ;;
    metadata)
        generate_metadata "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac

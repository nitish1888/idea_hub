#!/bin/bash
# =============================================================================
# Red Hat Idea Hub - Docker Build and Push Script
# =============================================================================
#
# This script builds both frontend and backend Docker images and pushes them
# to Quay.io with proper versioning and latest tags.
#
# Usage:
#   ./build-and-push.sh [QUAY_ORG] [VERSION]
#
# Examples:
#   ./build-and-push.sh myorg 1.0.0
#   ./build-and-push.sh redhat latest
#
# Requirements:
# - Podman installed and running (or Docker as alternative)
# - Logged into Quay.io (podman login quay.io)
# - Proper permissions to push to the specified organization
#
# =============================================================================

set -e  # Exit on any error

# =============================================================================
# Configuration
# =============================================================================

# Default values
DEFAULT_QUAY_ORG="redhat-gss"
DEFAULT_VERSION="latest"

# Get parameters or use defaults
QUAY_ORG="${1:-$DEFAULT_QUAY_ORG}"
VERSION="${2:-$DEFAULT_VERSION}"

# Image names
BACKEND_IMAGE="quay.io/${QUAY_ORG}/idea-hub-backend"
FRONTEND_IMAGE="quay.io/${QUAY_ORG}/idea-hub-frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================

print_banner() {
    echo -e "${CYAN}"
    echo "==============================================================================="
    echo "  🚀 Red Hat Idea Hub - Docker Build & Push Script"
    echo "==============================================================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check if logged into Quay
    if ! docker info | grep -q "quay.io" 2>/dev/null; then
        print_warning "Not logged into Quay.io. Please run: docker login quay.io"
    fi
    
    print_success "Prerequisites check passed"
}

build_image() {
    local dockerfile=$1
    local image_name=$2
    local service_name=$3
    
    print_step "Building ${service_name} image: ${image_name}:${VERSION}"
    
    # Build with version tag
    docker build \
        -f "${dockerfile}" \
        -t "${image_name}:${VERSION}" \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg VCS_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
        --build-arg VERSION="${VERSION}" \
        .
    
    # Tag as latest if not already latest
    if [ "${VERSION}" != "latest" ]; then
        docker tag "${image_name}:${VERSION}" "${image_name}:latest"
        print_success "Tagged ${service_name} as latest"
    fi
    
    print_success "${service_name} image built successfully"
}

push_image() {
    local image_name=$1
    local service_name=$2
    
    print_step "Pushing ${service_name} image to Quay.io..."
    
    # Push version tag
    docker push "${image_name}:${VERSION}"
    print_success "Pushed ${image_name}:${VERSION}"
    
    # Push latest tag if different from version
    if [ "${VERSION}" != "latest" ]; then
        docker push "${image_name}:latest"
        print_success "Pushed ${image_name}:latest"
    fi
}

cleanup_local_images() {
    print_step "Cleaning up local intermediate images..."
    
    # Remove dangling images
    if docker images -f "dangling=true" -q | grep -q .; then
        docker images -f "dangling=true" -q | xargs docker rmi || true
        print_success "Cleaned up dangling images"
    else
        print_success "No dangling images to clean up"
    fi
}

show_summary() {
    echo -e "${PURPLE}"
    echo "==============================================================================="
    echo "  🎉 Build and Push Summary"
    echo "==============================================================================="
    echo -e "${NC}"
    echo "📦 Backend Image:  ${BACKEND_IMAGE}:${VERSION}"
    echo "🎨 Frontend Image: ${FRONTEND_IMAGE}:${VERSION}"
    echo ""
    echo "🔗 Quay.io Links:"
    echo "   Backend:  https://quay.io/repository/${QUAY_ORG}/idea-hub-backend"
    echo "   Frontend: https://quay.io/repository/${QUAY_ORG}/idea-hub-frontend"
    echo ""
    echo "🚀 Deploy with Docker Compose:"
    echo "   sed -i 's/YOUR_ORG/${QUAY_ORG}/g' docker-compose.yml"
    echo "   docker-compose pull && docker-compose up -d"
    echo ""
    echo "🛠️  Deploy individual containers:"
    echo "   docker run -p 5001:5001 --env-file .env ${BACKEND_IMAGE}:${VERSION}"
    echo "   docker run -p 8080:80 ${FRONTEND_IMAGE}:${VERSION}"
    echo -e "${PURPLE}"
    echo "==============================================================================="
    echo -e "${NC}"
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    print_banner
    
    echo "🎯 Building for organization: ${QUAY_ORG}"
    echo "🏷️  Version tag: ${VERSION}"
    echo ""
    
    # Confirm with user
    read -p "Continue with build and push? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Build cancelled by user"
        exit 0
    fi
    
    # Execute build pipeline
    check_prerequisites
    
    # Build backend
    build_image "Dockerfile.backend" "${BACKEND_IMAGE}" "Backend"
    
    # Build frontend
    build_image "Dockerfile.frontend" "${FRONTEND_IMAGE}" "Frontend"
    
    # Push to Quay
    push_image "${BACKEND_IMAGE}" "Backend"
    push_image "${FRONTEND_IMAGE}" "Frontend"
    
    # Cleanup
    cleanup_local_images
    
    # Show summary
    show_summary
    
    print_success "All images built and pushed successfully! 🎉"
}

# =============================================================================
# Script Entry Point
# =============================================================================

# Show help if requested
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Red Hat Idea Hub - Docker Build & Push Script"
    echo ""
    echo "Usage: $0 [QUAY_ORG] [VERSION]"
    echo ""
    echo "Parameters:"
    echo "  QUAY_ORG    Quay.io organization name (default: ${DEFAULT_QUAY_ORG})"
    echo "  VERSION     Image version tag (default: ${DEFAULT_VERSION})"
    echo ""
    echo "Examples:"
    echo "  $0 myorg 1.0.0      # Build myorg/idea-hub-*:1.0.0"
    echo "  $0 redhat latest     # Build redhat/idea-hub-*:latest"
    echo "  $0                   # Use defaults"
    echo ""
    echo "Prerequisites:"
    echo "  - Docker installed and running"
    echo "  - Logged into Quay.io: docker login quay.io"
    echo "  - Push permissions to specified organization"
    exit 0
fi

# Run main function
main "$@"

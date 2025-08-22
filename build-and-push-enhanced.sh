#!/bin/bash

# Build and Push Script for Enhanced Idea Hub with MCP Integration
# ================================================================

set -e

echo "🚀 Building Enhanced Idea Hub with MCP Integration"
echo "=================================================="

# Configuration
IMAGE_NAME="idea-hub-updated"
REGISTRY="quay.io/rhn-support-nitsingh"
TAG="latest"
FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"

echo "📝 Configuration:"
echo "   Image Name: ${IMAGE_NAME}"
echo "   Registry: ${REGISTRY}"
echo "   Tag: ${TAG}"
echo "   Full Image: ${FULL_IMAGE_NAME}"
echo ""

# Check if certificates exist
echo "🔍 Checking certificates..."
if [ ! -f "./aws-global-bundle.pem" ] || [ ! -f "./2022-IT-Root-CA.pem" ]; then
    echo "⚠️  Certificates not found. Creating dummy certificates for build..."
    touch ./aws-global-bundle.pem ./2022-IT-Root-CA.pem
    echo "   Note: Update certificates for production deployment"
fi

# Clean any existing containers/images
echo "🧹 Cleaning up existing images..."
podman rmi -f $FULL_IMAGE_NAME 2>/dev/null || true

# Build the enhanced image
echo "🔨 Building Enhanced Idea Hub image..."
echo "   Features included:"
echo "   ✅ MCP Client integration"
echo "   ✅ Enhanced AI service with fallbacks"
echo "   ✅ SSL certificate handling"
echo "   ✅ HuggingFace model pre-caching"
echo "   ✅ Production-ready configuration"
echo ""

podman build \
    --tag $FULL_IMAGE_NAME \
    --platform linux/amd64 \
    --no-cache \
    -f Dockerfile \
    .

if [ $? -eq 0 ]; then
    echo "✅ Image built successfully!"
    
    # Show image details
    echo ""
    echo "📊 Image details:"
    podman images | grep $IMAGE_NAME | head -1
    
    # Login to Quay (if needed)
    echo ""
    echo "🔐 Logging into Quay.io..."
    podman login quay.io
    
    # Push the image
    echo ""
    echo "📤 Pushing image to Quay.io..."
    podman push $FULL_IMAGE_NAME
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 SUCCESS! Enhanced Idea Hub image pushed successfully!"
        echo ""
        echo "📋 Next steps:"
        echo "1. Update OpenShift secrets in openshift/secrets.yaml"
        echo "2. Apply OpenShift manifests:"
        echo "   oc apply -f openshift/secrets.yaml"
        echo "   oc apply -f openshift/deployment.yaml"  
        echo "   oc apply -f openshift/route.yaml"
        echo ""
        echo "🔗 Image available at: $FULL_IMAGE_NAME"
        echo "🌐 Will be accessible at: OpenShift auto-generated route (check: oc get route idea-hub-updated)"
        echo ""
        echo "🏗️  Architecture:"
        echo "   Main App (Idea Hub) ⟷ MCP Server"
        echo "   Both running on OpenShift with internal networking"
    else
        echo "❌ Failed to push image to Quay.io"
        exit 1
    fi
else
    echo "❌ Failed to build image"
    exit 1
fi

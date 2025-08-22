#!/bin/bash

# Enhanced Build Script with Versioning
# Usage: ./scripts/build-with-version.sh [version]
# Example: ./scripts/build-with-version.sh v1.2.3

set -e

# Configuration
REGISTRY="quay.io/rhn-support-nitsingh"
IMAGE_NAME="idea-hub-updated"

# Get version from argument or generate timestamp-based version
if [ -n "$1" ]; then
    VERSION="$1"
else
    # Auto-generate version with timestamp
    TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
    VERSION="v$(date +"%Y.%m.%d")-${TIMESTAMP}"
fi

FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${VERSION}"
LATEST_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:latest"

echo "🚀 Building Enhanced Idea Hub with Version: $VERSION"
echo "=================================================="
echo "📝 Configuration:"
echo "   Image Name: $IMAGE_NAME"
echo "   Registry: $REGISTRY"
echo "   Version: $VERSION"
echo "   Full Image: $FULL_IMAGE_NAME"
echo "   Latest Tag: $LATEST_IMAGE_NAME"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the idea_hub directory"
    exit 1
fi

# Check certificates
echo "🔍 Checking certificates..."
if [ ! -f "./aws-global-bundle.pem" ] || [ ! -f "./2022-IT-Root-CA.pem" ]; then
    echo "⚠️  Warning: SSL certificates not found. Image will work but may have SSL issues."
fi

# Clean up existing images (optional)
echo "🧹 Cleaning up existing images..."
podman rmi $FULL_IMAGE_NAME 2>/dev/null || true
podman rmi $LATEST_IMAGE_NAME 2>/dev/null || true

# Build the image
echo "🔨 Building Enhanced Idea Hub image..."
echo "   Features included:"
echo "   ✅ MCP Client integration"
echo "   ✅ Enhanced AI service with fallbacks"
echo "   ✅ SSL certificate handling"
echo "   ✅ HuggingFace model pre-caching"
echo "   ✅ Production-ready configuration"
echo ""

# Use enhanced Dockerfile (same as build-and-push-enhanced.sh)
podman build \
    --file ./Dockerfile \
    --tag $FULL_IMAGE_NAME \
    --tag $LATEST_IMAGE_NAME \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Image built successfully!"
    echo ""
    echo "📊 Image details:"
    podman images | grep "$IMAGE_NAME" | head -2
    echo ""
    
    # Login to Quay (if needed)
    echo "🔐 Logging into Quay.io..."
    podman login quay.io
    
    # Push both tags
    echo ""
    echo "📤 Pushing versioned image to Quay.io..."
    podman push $FULL_IMAGE_NAME
    
    echo "📤 Pushing latest tag to Quay.io..."
    podman push $LATEST_IMAGE_NAME
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 SUCCESS! Enhanced Idea Hub image pushed successfully!"
        echo ""
        echo "📋 Images available:"
        echo "   Versioned: $FULL_IMAGE_NAME"
        echo "   Latest: $LATEST_IMAGE_NAME"
        echo ""
        echo "📋 Next steps:"
        echo "1. Deploy specific version:"
        echo "   ./scripts/deploy-version.sh $VERSION"
        echo ""
        echo "2. Or update manually:"
        echo "   oc set image deployment/idea-hub-updated idea-hub-updated=$FULL_IMAGE_NAME"
        echo ""
        echo "3. Check deployment status:"
        echo "   oc rollout status deployment/idea-hub-updated"
        echo ""
        
        # Save version info
        echo "$VERSION" > .last-built-version
        echo "💾 Version saved to .last-built-version"
        
    else
        echo "❌ Failed to push image to Quay.io"
        exit 1
    fi
else
    echo "❌ Failed to build image"
    exit 1
fi

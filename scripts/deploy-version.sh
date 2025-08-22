#!/bin/bash

# Quick Deployment Script for Version Updates
# Usage: ./scripts/deploy-version.sh [version]
# Example: ./scripts/deploy-version.sh v1.2.3

set -e

# Configuration
REGISTRY="quay.io/rhn-support-nitsingh"
IMAGE_NAME="idea-hub-updated"
DEPLOYMENT_NAME="idea-hub-updated"
NAMESPACE="trend-analysis-using-ai--runtime-int"

# Get version from argument or use last built version
if [ -n "$1" ]; then
    VERSION="$1"
elif [ -f ".last-built-version" ]; then
    VERSION=$(cat .last-built-version)
    echo "📁 Using last built version: $VERSION"
else
    echo "❌ Error: No version specified and no .last-built-version file found"
    echo "Usage: $0 [version]"
    echo "Example: $0 v1.2.3"
    exit 1
fi

FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${VERSION}"

echo "🚀 Deploying Idea Hub Version: $VERSION"
echo "======================================="
echo "📝 Configuration:"
echo "   Image: $FULL_IMAGE_NAME"
echo "   Deployment: $DEPLOYMENT_NAME"
echo "   Namespace: $NAMESPACE"
echo ""

# Check if we're logged into OpenShift
echo "🔍 Checking OpenShift connection..."
if ! oc whoami &> /dev/null; then
    echo "❌ Error: Not logged into OpenShift. Please run 'oc login' first."
    exit 1
fi

echo "✅ Connected to OpenShift as: $(oc whoami)"
echo "📍 Current project: $(oc project -q)"

# Switch to correct namespace if needed
if [ "$(oc project -q)" != "$NAMESPACE" ]; then
    echo "🔄 Switching to namespace: $NAMESPACE"
    oc project $NAMESPACE
fi

# Check if deployment exists
echo "🔍 Checking if deployment exists..."
if ! oc get deployment $DEPLOYMENT_NAME &> /dev/null; then
    echo "❌ Error: Deployment '$DEPLOYMENT_NAME' not found in namespace '$NAMESPACE'"
    echo "Available deployments:"
    oc get deployments
    exit 1
fi

echo "✅ Deployment found: $DEPLOYMENT_NAME"

# Get current image
CURRENT_IMAGE=$(oc get deployment $DEPLOYMENT_NAME -o jsonpath='{.spec.template.spec.containers[0].image}')
echo "📋 Current image: $CURRENT_IMAGE"
echo "🔄 New image: $FULL_IMAGE_NAME"

# Update the deployment with new image
echo ""
echo "🚀 Updating deployment with new image..."
oc set image deployment/$DEPLOYMENT_NAME $DEPLOYMENT_NAME=$FULL_IMAGE_NAME

if [ $? -eq 0 ]; then
    echo "✅ Image updated successfully!"
    echo ""
    echo "📊 Watching rollout status..."
    echo "   Press Ctrl+C to stop watching (deployment will continue)"
    echo ""
    
    # Watch the rollout
    oc rollout status deployment/$DEPLOYMENT_NAME --timeout=300s
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 SUCCESS! Deployment completed successfully!"
        echo ""
        echo "📋 Deployment Info:"
        oc get deployment $DEPLOYMENT_NAME
        echo ""
        echo "📋 Pod Status:"
        oc get pods -l app=$DEPLOYMENT_NAME
        echo ""
        echo "🌐 Application Routes:"
        oc get routes -l app=$DEPLOYMENT_NAME
        echo ""
        echo "📝 Recent Pod Logs (last 10 lines):"
        POD_NAME=$(oc get pods -l app=$DEPLOYMENT_NAME -o jsonpath='{.items[0].metadata.name}')
        if [ -n "$POD_NAME" ]; then
            oc logs $POD_NAME --tail=10
        fi
        echo ""
        echo "🔍 To view full logs: oc logs -f deployment/$DEPLOYMENT_NAME"
        echo "🔄 To rollback if needed: oc rollout undo deployment/$DEPLOYMENT_NAME"
        
        # Save deployment info
        echo "$VERSION" > .last-deployed-version
        echo "💾 Deployed version saved to .last-deployed-version"
        
    else
        echo "⚠️  Rollout timed out or failed. Check status manually:"
        echo "   oc rollout status deployment/$DEPLOYMENT_NAME"
        echo "   oc describe deployment $DEPLOYMENT_NAME"
        echo "   oc logs -f deployment/$DEPLOYMENT_NAME"
    fi
else
    echo "❌ Failed to update deployment image"
    exit 1
fi

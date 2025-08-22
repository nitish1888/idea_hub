# 🚀 Idea Hub - Image Update Guide

This guide provides step-by-step instructions for updating the Idea Hub application with new code changes.

## 📋 Table of Contents
- [Quick Update Process](#quick-update-process)
- [Detailed Steps](#detailed-steps)
- [Troubleshooting](#troubleshooting)
- [Verification](#verification)
- [Alternative Methods](#alternative-methods)

---

## ⚡ Quick Update Process

### One-Liner Command (Recommended)
```bash
./build-and-push-enhanced.sh && oc set image deployment/idea-hub-updated-new idea-hub-updated-new=quay.io/rhn-support-nitsingh/idea-hub-updated:latest && oc rollout status deployment/idea-hub-updated-new
```

### Step-by-Step (3 commands)
```bash
# 1. Build and push new image
./build-and-push-enhanced.sh

# 2. Update deployment with latest image
oc set image deployment/idea-hub-updated-new idea-hub-updated-new=quay.io/rhn-support-nitsingh/idea-hub-updated:latest

# 3. Watch rollout complete
oc rollout status deployment/idea-hub-updated-new
```

---

## 📝 Detailed Steps

### Prerequisites
- [x] You're logged into OpenShift CLI (`oc login`)
- [x] You're in the `idea_hub` directory
- [x] Pull secret is configured (already done)

### Step 1: Build and Push Image
```bash
# Navigate to project directory
cd /Users/nitsingh/idea_hub_updated/idea_hub

# Build and push enhanced image
./build-and-push-enhanced.sh
```

**What this does:**
- Builds Docker image with all your latest code changes
- Tags image as `quay.io/rhn-support-nitsingh/idea-hub-updated:latest`
- Pushes to Quay.io registry

### Step 2: Update Deployment
```bash
# Update deployment to use latest image
oc set image deployment/idea-hub-updated-new idea-hub-updated-new=quay.io/rhn-support-nitsingh/idea-hub-updated:latest
```

**What this does:**
- Updates the deployment configuration
- Triggers a new rollout with the latest image

### Step 3: Monitor Rollout
```bash
# Watch rollout progress (max 5 minutes)
oc rollout status deployment/idea-hub-updated-new --timeout=300s
```

**Expected output:**
```
deployment "idea-hub-updated-new" successfully rolled out
```

---

## ✅ Verification

### Check Pod Status
```bash
# Verify pod is running
oc get pods -l app=idea-hub-updated-new
```

**Expected output:**
```
NAME                                    READY   STATUS    RESTARTS   AGE
idea-hub-updated-new-857d57bfb9-mscsc   1/1     Running   0          2m
```

### Verify Image Version
```bash
# Check what image is running
POD_NAME=$(oc get pods -l app=idea-hub-updated-new -o jsonpath='{.items[0].metadata.name}')
oc describe pod $POD_NAME | grep "Image:"
```

### Get Application URL
```bash
# Get the application URL
oc get route idea-hub-updated-new -o jsonpath='{.spec.host}' && echo
```

### Test Application
Visit the URL in your browser:
```
https://idea-hub-updated-new-trend-analysis-using-ai--runtime-int.apps.int.spoke.preprod.us-east-1.aws.paas.redhat.com
```

---

## 🔧 Alternative Methods

### Method 1: Using Version Tags
```bash
# Build with specific version
./scripts/build-with-version.sh v1.2.3

# Deploy specific version
oc set image deployment/idea-hub-updated-new idea-hub-updated-new=quay.io/rhn-support-nitsingh/idea-hub-updated:v1.2.3

# Watch rollout
oc rollout status deployment/idea-hub-updated-new
```

### Method 2: Using ImageStream
```bash
# Build and push
./build-and-push-enhanced.sh

# Import to internal registry
oc import-image idea-hub-updated:latest --confirm

# Update deployment to use imagestream
oc set image deployment/idea-hub-updated-new idea-hub-updated-new=image-registry.openshift-image-registry.svc:5000/trend-analysis-using-ai--runtime-int/idea-hub-updated:latest

# Watch rollout
oc rollout status deployment/idea-hub-updated-new
```

---

## 🚨 Troubleshooting

### Issue: ImagePullBackOff
**Error:** `unauthorized: access to the requested resource is not authorized`

**Solution:** Verify pull secret exists
```bash
# Check if pull secret exists
oc get secrets | grep nitsingh-quay-pull-secret

# If missing, recreate it
oc create secret docker-registry nitsingh-quay-pull-secret \
  --docker-server=quay.io \
  --docker-username=rhn-support-nitsingh \
  --docker-password=WYMhHyCMjtm3RAEA+MaZZPb7GiFtWcxIW3JXa0+DdqtaqouieyOIyFOK/eYE8lJ0 \
  --docker-email=nitsingh@redhat.com

# Update deployment to use the secret
oc patch deployment idea-hub-updated-new -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"nitsingh-quay-pull-secret"}]}}}}'
```

### Issue: Rollout Stuck
**Symptoms:** Rollout hangs or takes too long

**Solution:** Check pod events
```bash
# Get failing pod name
oc get pods -l app=idea-hub-updated-new

# Describe the pod to see events
oc describe pod <pod-name>

# Check logs
oc logs <pod-name>
```

### Issue: Old Image Still Running
**Symptoms:** Pod shows old image SHA

**Solution:** Force restart
```bash
# Scale down and up to force new pods
oc scale deployment idea-hub-updated-new --replicas=0
sleep 5
oc scale deployment idea-hub-updated-new --replicas=1

# Or rollout restart
oc rollout restart deployment/idea-hub-updated-new
```

---

## 📚 Useful Commands

### Deployment Management
```bash
# Check deployment status
oc get deployment idea-hub-updated-new

# View deployment history
oc rollout history deployment/idea-hub-updated-new

# Rollback to previous version
oc rollout undo deployment/idea-hub-updated-new

# Scale deployment
oc scale deployment idea-hub-updated-new --replicas=2
```

### Monitoring
```bash
# Watch pods in real-time
oc get pods -l app=idea-hub-updated-new -w

# Follow logs
oc logs -f deployment/idea-hub-updated-new

# Get recent events
oc get events --sort-by=.metadata.creationTimestamp
```

### Image Information
```bash
# List available images in imagestream
oc get imagestream idea-hub-updated

# Get current deployment image
oc get deployment idea-hub-updated-new -o jsonpath='{.spec.template.spec.containers[0].image}'

# Check Quay.io images
podman search quay.io/rhn-support-nitsingh/idea-hub-updated
```

---

## 🎯 Quick Reference

### Essential Commands
| Action | Command |
|--------|---------|
| Build & Push | `./build-and-push-enhanced.sh` |
| Update Image | `oc set image deployment/idea-hub-updated-new idea-hub-updated-new=quay.io/rhn-support-nitsingh/idea-hub-updated:latest` |
| Watch Rollout | `oc rollout status deployment/idea-hub-updated-new` |
| Check Pods | `oc get pods -l app=idea-hub-updated-new` |
| Get URL | `oc get route idea-hub-updated-new -o jsonpath='{.spec.host}'` |
| View Logs | `oc logs -f deployment/idea-hub-updated-new` |
| Restart | `oc rollout restart deployment/idea-hub-updated-new` |
| Rollback | `oc rollout undo deployment/idea-hub-updated-new` |

### Configuration Details
- **Registry:** `quay.io/rhn-support-nitsingh/idea-hub-updated`
- **Deployment:** `idea-hub-updated-new`
- **Namespace:** `trend-analysis-using-ai--runtime-int`
- **Pull Secret:** `nitsingh-quay-pull-secret`
- **Port:** `8080`

---

## 📱 Application URLs

### Production
```
https://idea-hub-updated-new-trend-analysis-using-ai--runtime-int.apps.int.spoke.preprod.us-east-1.aws.paas.redhat.com
```

### Health Check
```
https://idea-hub-updated-new-trend-analysis-using-ai--runtime-int.apps.int.spoke.preprod.us-east-1.aws.paas.redhat.com/api/health
```

---

## 📅 Last Updated
**Date:** August 19, 2025  
**Version:** Enhanced with search fixes and duplicate removal  
**Image SHA:** `sha256:3ca4897954e4e14dc98bc6da33a795bd71c99ff9f3b63bfa64a07d8184b75c53`

---

## 🔗 Related Files
- `build-and-push-enhanced.sh` - Main build script
- `Dockerfile` - Container configuration
- `openshift/deployment.yaml` - Deployment manifest
- `requirements.txt` - Python dependencies

---

**💡 Pro Tip:** Bookmark this file for quick reference during deployments!

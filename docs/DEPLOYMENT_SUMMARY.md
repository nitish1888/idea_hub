# Idea Hub Updated - OpenShift Deployment Summary
==================================================

## Overview
This deployment includes your enhanced Idea Hub application with full MCP (Model Context Protocol) integration, deploying both the main application and MCP server as separate microservices on OpenShift.

## Architecture
```
┌─────────────────────┐    HTTPS/JSON    ┌─────────────────────┐
│   Idea Hub Updated  │ ◄──────────────► │   MCP Server        │
│   (Main App)        │                  │   (AI Tools)        │
│   Port 8080         │                  │   Port 8000/8443    │
└─────────────────────┘                  └─────────────────────┘
```

## Deployment Names & URLs

### Main Application (Enhanced Idea Hub)
- **Name**: `idea-hub-updated`
- **Image**: `quay.io/rhn-support-nitsingh/idea-hub-updated:latest`
- **URL**: `https://idea-hub-updated-trend-analysis-using-ai--runtime-int.apps.int.spoke.preprod.us-east-1.aws.paas.redhat.com`

### MCP Server (Already Deployed)
- **Name**: `idea-hub-mcp-server`
- **Image**: `quay.io/rhn-support-nitsingh/idea-hub-mcp-server:latest`
- **URL**: `https://idea-hub-mcp-server-trend-analysis-using-ai--runtime-int.apps.int.spoke.preprod.us-east-1.aws.paas.redhat.com`

## Key Features
- ✅ **MCP Integration**: Main app communicates with MCP server for AI operations
- ✅ **SSL/TLS**: Edge termination with proper certificate handling
- ✅ **Internal Routing**: OpenShift MPP compliant internal networking
- ✅ **Fallback Support**: Graceful fallback to local AI services
- ✅ **Enhanced AI**: Semantic search, duplicate detection, summarization
- ✅ **Production Ready**: Health checks, resource limits, security contexts

## Build & Deploy Commands

### 1. Build and Push Image
```bash
./build-and-push-enhanced.sh
```

### 2. Deploy to OpenShift
```bash
# Apply secrets (update base64 values first)
oc apply -f openshift/secrets.yaml

# Deploy application
oc apply -f openshift/deployment.yaml

# Create route
oc apply -f openshift/route.yaml
```

### 3. Verify Deployment
```bash
# Check pods
oc get pods -l app=idea-hub-updated

# Check services
oc get svc idea-hub-updated

# Check routes
oc get route idea-hub-updated
```

## Environment Variables
- **Database**: PostgreSQL connection via secrets
- **AI Services**: Google Gemini API key
- **MCP Server**: Internal OpenShift service URL
- **HuggingFace**: Model caching configuration

## Secrets Configuration
Update `openshift/secrets.yaml` with base64 encoded values:
```bash
echo -n "your_db_host" | base64
echo -n "5432" | base64
echo -n "idea_hub_db" | base64
echo -n "your_db_user" | base64
echo -n "your_db_password" | base64
echo -n "your_google_api_key" | base64
```

## Testing Endpoints
Once deployed, test these endpoints:
- **Health**: `/api/health`
- **MCP Test**: `/api/mcp/test`
- **Search**: `/api/ideas/search`
- **Web Interface**: `/`

## Resource Allocation
- **CPU**: 500m request, 2000m limit
- **Memory**: 1Gi request, 4Gi limit
- **Replicas**: 1 (can be scaled)

## Networking
- **Internal Communication**: idea-hub-updated ↔ idea-hub-mcp-server
- **External Access**: HTTPS via OpenShift routes
- **SSL**: Edge termination with redirect



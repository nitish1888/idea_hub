# Red Hat Idea Hub - Production Deployment Guide

## 🚀 **Production-Ready Application**

This repository contains a fully functional AI-powered Idea Hub with advanced duplicate detection and semantic search capabilities.

### ✅ **Key Features**
- **AI-Powered Duplicate Detection** with 78%+ similarity threshold
- **Rich User Interface** with "Submit Anyway" functionality  
- **Semantic Search** using HuggingFace embeddings
- **Vector Database** integration with pgvector
- **Multi-user Support** with contributor management
- **Admin Dashboard** with analytics and insights
- **PDF Upload** and processing capabilities
- **MCP Agentic AI** research integration

### 🏗️ **Architecture**
- **Backend**: Flask with modular route structure
- **Database**: PostgreSQL with pgvector extension
- **AI Services**: Google Gemini + HuggingFace transformers
- **Vector Store**: LangChain + PGVector for semantic search
- **Frontend**: Modern HTML/CSS/JS with Bootstrap
- **Deployment**: OpenShift/Kubernetes ready

### 📁 **Production File Structure**
```
idea_hub/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container build
├── entrypoint.sh         # Container startup
├── openshift-secret.yaml # OpenShift secrets template
├── config/               # Application configuration
├── models/               # Database models
├── routes/               # API route handlers
├── services/             # Business logic services
├── templates/            # HTML templates
├── static/               # CSS, JS, images
└── uploads/              # User file uploads
```

### 🔧 **Deployment Instructions**

#### **1. Build Container Image**
```bash
./build-and-push.sh
```

#### **2. Deploy to OpenShift**
```bash
# Create/update route with internal shard
oc apply -f openshift-secret.yaml
oc new-app quay.io/rhn-support-nitsingh/idea-hub-backend:latest
```

#### **3. Configure Environment Variables**
- `GEMINI_API_KEY` - Google Gemini API key
- `DATABASE_URL` - PostgreSQL connection string
- `HUGGINGFACE_MODEL` - Transformer model name
- `ALLOWED_ORIGINS` - CORS origins

### 🎯 **Production URLs**
- **Application**: https://idea-hub-backend-trend-analysis-using-ai--runtime-int.apps.int.spoke.preprod.us-east-1.aws.paas.redhat.com
- **Health Check**: `/api/health`
- **Submit Ideas**: `/submit`
- **Browse Ideas**: `/browse`
- **Admin Dashboard**: `/admin`

### 🔒 **Security Features**
- Environment-based configuration
- Input validation and sanitization
- CORS protection
- File upload restrictions
- SQL injection prevention

### 📊 **Monitoring & Health**
- Health check endpoint: `/api/health`
- System status: `/api/status`
- Database connectivity monitoring
- AI service availability checks

### ⚡ **Performance Optimizations**
- Vector database indexing for fast similarity search
- Async AI processing where possible
- Efficient database queries
- Static file caching
- Responsive frontend design

---

**Built by**: Red Hat Innovation Team  
**Last Updated**: August 2025  
**Version**: 1.0.0

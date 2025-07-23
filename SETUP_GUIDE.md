# Red Hat Idea Hub - Comprehensive Setup Guide

## 🎯 **Platform Overview**

Welcome to the Red Hat Idea Hub - a comprehensive AI-powered innovation management platform featuring:

- **🎨 Modern Streamlit Frontend**: Interactive web interface for idea management
- **🔧 Flask API Backend**: RESTful API with AI-powered intelligence  
- **🧠 Google Gemini Integration**: Advanced AI for similarity detection and insights
- **🗄️ PostgreSQL + pgvector**: Vector database for semantic search
- **📊 Analytics Dashboard**: Visual insights and trend analysis

## 📋 **Prerequisites Checklist**

### **✅ Required Software**
- [ ] **PostgreSQL 12+** with superuser access
- [ ] **Python 3.8+** (conda environment recommended)
- [ ] **Google Gemini API Key** (get from [Google AI Studio](https://makersuite.google.com/app/apikey))
- [ ] **Terminal/Command Line Access** for setup commands

### **✅ System Requirements**
- [ ] **8GB RAM** minimum (for AI model operations)
- [ ] **2GB free disk space** for dependencies and data
- [ ] **Internet connection** for AI API calls
- [ ] **Modern web browser** for frontend interface

## 🗄️ **Database Setup (Step 1)**

### **PostgreSQL Installation & Configuration**

#### **Option A: Using Homebrew (macOS)**
```bash
# Install PostgreSQL
brew install postgresql@14
brew services start postgresql@14

# Connect as superuser
psql postgres
```

#### **Option B: Using Official Installer**
1. Download from [PostgreSQL.org](https://www.postgresql.org/download/)
2. Install with default settings
3. Remember the superuser password you set

### **Database & User Creation**
```sql
-- Connect to PostgreSQL as superuser (postgres user)
psql -U postgres

-- Create database and user
CREATE DATABASE idea_hub_db;
CREATE USER idea_user WITH PASSWORD 'secure_idea_pass';
GRANT ALL PRIVILEGES ON DATABASE idea_hub_db TO idea_user;

-- Connect to the new database
\c idea_hub_db;

-- Install required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO idea_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO idea_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO idea_user;

-- Verify extensions
SELECT extname FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp');

-- Exit PostgreSQL
\q
```

### **Verify Database Setup**
```bash
# Test connection with the new user
psql -h localhost -U idea_user -d idea_hub_db -c "SELECT 1;"
# Should return: 1
```

## 🐍 **Python Environment Setup (Step 2)**

### **Conda Environment (Recommended)**
```bash
# Create new conda environment
conda create -n idea_hub python=3.9 -y
conda activate idea_hub

# Verify Python version
python --version  # Should show Python 3.9.x
```

### **Alternative: Virtual Environment**
```bash
# Create virtual environment
python -m venv idea_hub_env

# Activate (macOS/Linux)
source idea_hub_env/bin/activate

# Activate (Windows)
idea_hub_env\Scripts\activate
```

### **Install Dependencies**
```bash
# Ensure you're in the project directory
cd /path/to/idea_hub

# Install all required packages
pip install -r requirements.txt

# Verify key installations
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"
python -c "import flask; print('Flask:', flask.__version__)"
python -c "import psycopg2; print('PostgreSQL driver: OK')"
```

## 🔑 **API Key Configuration (Step 3)**

### **Get Google Gemini API Key**
1. **Visit**: [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Sign in** with your Google account
3. **Create API Key** (or use existing one)
4. **Copy** the API key (starts with `AIza...`)
5. **Keep it secure** - don't share or commit to git

### **Environment Configuration**
```bash
# Create .env file in project root
cat > .env << 'EOF'
# =============================================================================
# RED HAT IDEA HUB CONFIGURATION
# =============================================================================

# Database Configuration
PG_USER=idea_user
PG_PASS=secure_idea_pass
PG_DB=idea_hub_db
PG_HOST=localhost
PG_PORT=5432

# Google Gemini AI Configuration (REQUIRED)
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Flask Application Settings
SECRET_KEY=your_secure_secret_key_change_for_production
DEBUG=True

# Vector Store Configuration
COLLECTION_NAME=idea_hub_collection
VECTOR_TABLE_NAME=idea_hub_embeddings

# AI Similarity Thresholds
DUPLICATE_THRESHOLD=0.8      # 80% similarity = potential duplicate
COLLABORATION_THRESHOLD=0.7  # 70% similarity = collaboration opportunity
SEARCH_THRESHOLD=0.3         # 30% minimum search relevance

# Application Ports
BACKEND_PORT=5001           # Flask API server port
FRONTEND_PORT=8501          # Streamlit frontend port
EOF

# IMPORTANT: Replace 'your_actual_gemini_api_key_here' with your real API key
nano .env  # Edit and update GEMINI_API_KEY
```

### **Security Note**
```bash
# Add .env to .gitignore to prevent committing secrets
echo ".env" >> .gitignore
```

## 🚀 **Application Startup (Step 4)**

### **Method 1: Complete Setup Script** ⭐ **Recommended**

Create a startup script for easy management:

```bash
# Create startup script
cat > start_idea_hub.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting Red Hat Idea Hub Platform"
echo "===================================="

# Check if conda environment is active
if [[ "$CONDA_DEFAULT_ENV" != "idea_hub" ]]; then
    echo "⚠️  Please activate conda environment first:"
    echo "   conda activate idea_hub"
    exit 1
fi

# Check if .env file exists
if [[ ! -f .env ]]; then
    echo "❌ .env file not found. Please create it first."
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null; then
        echo "⚠️  Port $1 is already in use"
        return 1
    fi
    return 0
}

# Check ports
if ! check_port 5001; then
    echo "❌ Backend port 5001 is busy. Kill existing process or use different port."
    exit 1
fi

if ! check_port 8501; then
    echo "⚠️  Frontend port 8501 is busy. Streamlit will use next available port."
fi

echo ""
echo "🔧 Starting Backend API Server (Flask)..."
python app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend started successfully
if ! curl -s http://localhost:5001/api/health >/dev/null; then
    echo "❌ Backend failed to start. Check logs for errors."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Backend running on http://localhost:5001"
echo ""
echo "🎨 Starting Frontend Web Interface (Streamlit)..."
streamlit run streamlit_app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "🎉 Red Hat Idea Hub is now running!"
echo ""
echo "🌐 Frontend (Web UI): http://localhost:8501"
echo "🔧 Backend (API):     http://localhost:5001"
echo "💊 Health Check:      http://localhost:5001/api/health"
echo ""
echo "📋 To stop the platform:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "⌨️  Press Ctrl+C to stop all services"

# Wait for user to stop
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
wait
EOF

# Make script executable
chmod +x start_idea_hub.sh

# Run the platform
./start_idea_hub.sh
```

### **Method 2: Manual Terminal Setup**

#### **Terminal 1: Backend API Server**
```bash
# Activate environment
conda activate idea_hub

# Start Flask backend
python app.py

# You should see:
# 🚀 Starting Red Hat Idea Hub - Modular API Backend
# 🌐 Server starting on http://localhost:5001
```

#### **Terminal 2: Frontend Web Interface**
```bash
# Activate environment (new terminal)
conda activate idea_hub

# Start Streamlit frontend
streamlit run streamlit_app.py

# You should see:
# Local URL: http://localhost:8501
# Network URL: http://192.168.x.x:8501
```

#### **Terminal 3: Database Initialization**
```bash
# Initialize database (one-time setup)
curl -X POST http://localhost:5001/api/init-database

# Load sample data for testing
curl -X POST http://localhost:5001/api/load-sample-data

# Verify health
curl http://localhost:5001/api/health
```

## ✅ **Verification & Testing (Step 5)**

### **1. Health Check Verification**
```bash
# Check backend health
curl http://localhost:5001/api/health | jq

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected", 
#   "pgvector": "enabled",
#   "gemini": "enabled",
#   "version": "1.0.0"
# }
```

### **2. Database Verification**
```bash
# Check detailed system status
curl http://localhost:5001/api/status | jq

# Verify database tables exist
psql -h localhost -U idea_user -d idea_hub_db -c "\dt"
```

### **3. Frontend Verification**
1. **Open Web Browser**: Navigate to http://localhost:8501
2. **Check Navigation**: Verify all pages load (Submit Innovation, Search Ideas, Dashboard)
3. **Test Form**: Try submitting a test idea
4. **Check Search**: Test the search functionality

### **4. AI Integration Verification**
```bash
# Test idea submission with AI analysis
curl -X POST http://localhost:5001/api/ideas/submit \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test AI Integration",
    "description": "This is a test to verify AI-powered duplicate detection and similarity analysis.",
    "contributor": "Setup Tester",
    "category": "Testing",
    "impact": "Medium"
  }'

# Test semantic search
curl -X POST http://localhost:5001/api/ideas/search \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence automation"}'
```

## 📊 **Platform Usage Guide**

### **Web Interface Navigation**
- **🏠 Home Page**: Platform overview and navigation
- **💡 Submit Innovation**: Form-based idea submission with AI duplicate detection
- **🔍 Search Ideas**: Natural language search with semantic matching
- **📈 Dashboard**: Analytics, insights, and trend visualization

### **Key Features to Test**
1. **Duplicate Detection**: Submit similar ideas to see AI warnings
2. **Semantic Search**: Search for concepts using natural language
3. **Analytics Dashboard**: View platform statistics and insights
4. **PDF Upload**: Test document attachment functionality

## 🛠️ **Troubleshooting Common Issues**

### **Database Connection Errors**
```bash
# Check PostgreSQL service
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql      # Linux

# Test connection manually
psql -h localhost -U idea_user -d idea_hub_db

# Check logs
tail -f /usr/local/var/log/postgres.log  # macOS
```

### **API Key Issues**
```bash
# Verify API key is set
echo $GEMINI_API_KEY

# Test Gemini API directly
python -c "
import google.generativeai as genai
from config.settings import Config
genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content('Hello, test message')
print('✅ Gemini API working:', response.text[:50])
"
```

### **Port Conflicts**
```bash
# Check what's using port 5001
lsof -i :5001

# Kill process if needed
kill -9 $(lsof -ti :5001)

# Check what's using port 8501
lsof -i :8501
```

### **Python Environment Issues**
```bash
# Verify conda environment
conda info --envs

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check import issues
python -c "
import streamlit
import flask
import psycopg2
import google.generativeai
print('✅ All key packages imported successfully')
"
```

### **Application Logs**
```bash
# Backend logs (Flask)
tail -f logs/app.log  # If log file exists

# Frontend logs (Streamlit)
# Check the terminal where streamlit is running

# Database initialization logs
curl http://localhost:5001/api/status | jq '.database_info'
```

## 🔧 **Advanced Configuration**

### **Production Environment Setup**
```bash
# Create production .env
cp .env .env.production

# Edit for production settings
nano .env.production
# Set DEBUG=False
# Use strong SECRET_KEY
# Configure production database
```

### **Performance Optimization**
```bash
# For high-volume usage, consider:
# 1. Use PostgreSQL connection pooling
# 2. Implement Redis caching
# 3. Use gunicorn for Flask backend
# 4. Configure nginx reverse proxy
```

### **Security Hardening**
```bash
# Secure file permissions
chmod 600 .env

# Use environment variables instead of .env file
export GEMINI_API_KEY="your_key_here"
export SECRET_KEY="your_secret_here"
```

## 📚 **Next Steps & Resources**

### **After Successful Setup**
1. **📖 Read the README.md**: Complete feature documentation
2. **🧪 Load Sample Data**: `curl -X POST http://localhost:5001/api/load-sample-data`
3. **🎯 Test All Features**: Submit ideas, search, view dashboard
4. **👥 Invite Team Members**: Share the web interface URL
5. **📊 Monitor Usage**: Check dashboard analytics regularly

### **Development & Customization**
- **Code Documentation**: All files are comprehensively documented
- **API Reference**: Available at http://localhost:5001/api/docs (when implemented)
- **Configuration Options**: See `config/settings.py` for all settings
- **Database Schema**: Check `models/idea.py` for data structure

### **Support Resources**
- **Health Monitoring**: http://localhost:5001/api/health
- **System Status**: http://localhost:5001/api/status  
- **Application Logs**: `logs/` directory
- **Database Logs**: PostgreSQL log files

---

## 🎉 **Setup Complete!**

Your Red Hat Idea Hub is now fully operational with:

✅ **Modern Web Interface** at http://localhost:8501  
✅ **Robust API Backend** at http://localhost:5001  
✅ **AI-Powered Intelligence** with Gemini integration  
✅ **Vector Database** for semantic search  
✅ **Comprehensive Analytics** dashboard  

**🚀 Welcome to intelligent innovation management!**

*Need help? Check the troubleshooting section or review the comprehensive README.md documentation.* 
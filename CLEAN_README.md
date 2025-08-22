# 🤖 Idea Hub MCP Server - Usage Guide

## 🚀 Quick Start

The MCP (Model Context Protocol) Server provides AI-powered tools and vector search services for the Idea Hub platform.

### 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- Environment variables configured

### 🔧 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/nitish1888/idea-hub-mcp-server.git
cd idea-hub-mcp-server
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp env.example .env
# Edit .env with your database and API credentials
```

### 🔑 Environment Variables

Create a `.env` file with:

```env
# Database Configuration
PG_HOST=localhost
PG_PORT=5432
PG_DB=idea_hub_db
PG_USER=your_db_user
PG_PASS=your_db_password

# AI Service Configuration
GEMINI_API_KEY=your_gemini_api_key
HF_TOKEN=your_huggingface_token

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### 🏃‍♂️ Running the Server

#### **Local Development:**
```bash
# Activate environment
source venv/bin/activate

# Run the server
python src/web_server.py
```

The server will be available at: `http://localhost:8000`

#### **Docker Deployment:**
```bash
# Build container
docker build -t idea-hub-mcp-server .

# Run container
docker run -p 8000:8000 --env-file .env idea-hub-mcp-server
```

## 🛠️ API Endpoints

### **Health Check**
```bash
curl http://localhost:8000/api/health
```

### **Search Ideas**
```bash
curl -X POST http://localhost:8000/api/search-ideas \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "limit": 5}'
```

### **Detect Duplicates**
```bash
curl -X POST http://localhost:8000/api/detect-duplicates \
  -H "Content-Type: application/json" \
  -d '{"idea_text": "AI-powered automation tool"}'
```

### **Generate Summary**
```bash
curl -X POST http://localhost:8000/api/generate-summary \
  -H "Content-Type: application/json" \
  -d '{"content": "Your idea description here"}'
```

## 🔧 Integration with Main App

The MCP server works with the main Idea Hub application:

1. **Configure MCP Client** in main app:
```python
MCP_SERVER_URL = "http://localhost:8000"
```

2. **Test Connection:**
```bash
# From main app directory
python test_mcp_connection.py
```

## 🐳 Container Usage

### **Build and Push:**
```bash
# Build container
docker build -t your-registry/idea-hub-mcp-server .
docker push your-registry/idea-hub-mcp-server
```

### **Run with Docker Compose:**
```yaml
version: '3.8'
services:
  mcp-server:
    image: idea-hub-mcp-server
    ports:
      - "8000:8000"
    environment:
      - PG_HOST=postgres
      - PG_DB=idea_hub_db
    depends_on:
      - postgres
```

## 🔍 Troubleshooting

### **Common Issues:**

1. **Database Connection Failed:**
```bash
# Check database credentials
psql -h $PG_HOST -U $PG_USER -d $PG_DB

# Run database migration if needed
python database_migration.py
```

2. **API Key Issues:**
```bash
# Test Gemini API key
curl -H "Authorization: Bearer $GEMINI_API_KEY" \
  https://generativelanguage.googleapis.com/v1/models
```

3. **Port Already in Use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in .env
PORT=8001
```

### **Logs and Debugging:**
```bash
# Enable debug logging
export DEBUG=true

# Check container logs
docker logs idea-hub-mcp-server
```

## 📊 Monitoring

### **Health Checks:**
- Health endpoint: `GET /api/health`
- Metrics: Available via application logs
- Database connection: Tested on startup

### **Performance:**
- Response time: < 500ms for most operations
- Concurrent requests: Supports up to 100 concurrent connections
- Memory usage: ~512MB typical

## 🔐 Security

- **API Authentication:** Configure API keys in environment
- **HTTPS Support:** Use reverse proxy (nginx/Apache) for production
- **Database Security:** Use encrypted connections in production

## 📚 API Documentation

Full API documentation available at: `http://localhost:8000/docs` (when server is running)

## 🤝 Integration Examples

### **Python Client:**
```python
import requests

# Initialize client
mcp_url = "http://localhost:8000"

# Search ideas
response = requests.post(f"{mcp_url}/api/search-ideas", 
    json={"query": "AI innovation", "limit": 5})
ideas = response.json()
```

### **cURL Examples:**
```bash
# Quick health check
curl -s http://localhost:8000/api/health | jq

# Search with filters
curl -X POST http://localhost:8000/api/search-ideas \
  -H "Content-Type: application/json" \
  -d '{"query": "kubernetes", "search_type": "semantic", "limit": 10}' | jq
```

## 🔗 Related Resources

- **Main Idea Hub App:** https://github.com/nitish1888/idea_hub
- **Documentation:** See `/docs` directory for detailed guides
- **Examples:** Check example configurations and usage

## 💡 Usage Tips

1. **Start MCP server before main application**
2. **Use semantic search for better results**
3. **Monitor logs for performance optimization**
4. **Scale horizontally for high load**

---

**🚀 Ready to innovate with AI-powered idea management!**

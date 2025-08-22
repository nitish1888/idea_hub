# 🤖 Idea Hub MCP Server

## 🚀 Quick Start

The MCP (Model Context Protocol) Server provides AI-powered tools and vector search services for the Idea Hub platform.

### 📋 Prerequisites

- Python 3.8+
- PostgreSQL database with pgvector extension
- Environment variables configured

### 🔧 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/nitish1888/idea-hub-mcp-server.git
cd idea-hub-mcp-server
```

2. **Set up environment:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configure:**
```bash
cp env.example .env
# Edit .env with your credentials
```

### 🏃‍♂️ Running

```bash
# Development
python src/web_server.py

# Docker
docker build -t idea-hub-mcp-server .
docker run -p 8000:8000 --env-file .env idea-hub-mcp-server
```

## 🛠️ API Endpoints

- **Health:** `GET /api/health`
- **Search:** `POST /api/search-ideas`
- **Duplicates:** `POST /api/detect-duplicates`
- **Summary:** `POST /api/generate-summary`

## 🔧 Integration

Works with the main Idea Hub application. Configure:

```python
MCP_SERVER_URL = "http://localhost:8000"
```

## 📚 Documentation

Full API docs available at: `http://localhost:8000/docs`

## 🔗 Related

- **Main App:** https://github.com/nitish1888/idea_hub

---

**🚀 AI-powered idea management!**

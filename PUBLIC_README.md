# 🚀 Idea Hub - AI-Powered Innovation Platform

## 📖 Overview

Idea Hub is an AI-powered innovation management platform that helps organizations collect, analyze, and develop innovative ideas using cutting-edge artificial intelligence and vector search technology.

## ✨ Key Features

- 🤖 **AI Research Assistant** with 6 specialized tools
- 🔍 **Semantic Search** using vector embeddings
- 📊 **Real-time Analytics** and trend analysis
- 👥 **Contributor Management** system
- 🛡️ **Duplicate Detection** using AI similarity analysis
- 📋 **Admin Dashboard** for comprehensive management
- 🔧 **MCP Integration** for advanced AI capabilities

## 🚀 Quick Start

### 📋 Prerequisites

- Python 3.8+
- PostgreSQL database with pgvector extension
- Git

### 🔧 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/nitish1888/idea_hub.git
cd idea_hub
```

2. **Create virtual environment:**
```bash
python -m venv idea_hub_env
source idea_hub_env/bin/activate  # On Windows: idea_hub_env\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
# Update config/settings.py with your credentials
cp config/settings.py.example config/settings.py
```

### 🔑 Environment Configuration

Set up these environment variables or update `config/settings.py`:

```python
# Database Configuration
PG_HOST = "localhost"
PG_PORT = 5432
PG_DB = "idea_hub_db"
PG_USER = "your_db_user"
PG_PASS = "your_db_password"

# AI Service Configuration
GEMINI_API_KEY = "your_gemini_api_key"

# Application Settings
SECRET_KEY = "your_secret_key_here"
DEBUG = True
```

### 🗄️ Database Setup

1. **Create PostgreSQL database:**
```sql
CREATE DATABASE idea_hub_db;
CREATE EXTENSION IF NOT EXISTS vector;
```

2. **Initialize database:**
```bash
python -c "from database.setup import init_database; init_database()"
```

## 🏃‍♂️ Running the Application

### **Development Mode:**
```bash
# Activate environment
source idea_hub_env/bin/activate

# Run the application
python app.py
```

The application will be available at: `http://localhost:8080`

## 🌐 Application Structure

### **Web Interface:**
- **Main Dashboard:** `http://localhost:8080/`
- **Submit Ideas:** `http://localhost:8080/submit`
- **Search Ideas:** `http://localhost:8080/search`
- **Browse Ideas:** `http://localhost:8080/browse`
- **Contributors:** `http://localhost:8080/contributors`

### **Admin Interface:**
- **Admin Login:** `http://localhost:8080/admin/login`
- **AI Research:** `http://localhost:8080/admin/ai-research`
- **Analytics:** `http://localhost:8080/admin/analytics`
- **Manage Ideas:** `http://localhost:8080/admin/ideas`

## 🤖 AI Research Tools

The AI Research Assistant includes 6 specialized tools:

1. **search_similar_ideas** - Find related ideas using semantic search
2. **get_innovation_trends** - Get statistics and trends analysis
3. **get_idea_details** - Retrieve comprehensive idea information
4. **analyze_contributor_skills** - Match skills with contributors
5. **evaluate_idea_feasibility** - AI-powered feasibility assessment
6. **create_implementation_roadmap** - Generate project roadmaps

### **Example Usage:**
```bash
# Test AI research via API
curl -X POST http://localhost:8080/api/mcp/research \
  -H "Content-Type: application/json" \
  -d '{"query": "How many AI ideas do we have and what are the trends?"}'
```

## 🔍 Search Functionality

### **Semantic Search:**
```bash
curl -X POST http://localhost:8080/api/ideas/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning automation", "limit": 10}'
```

### **Search Features:**
- **AI-powered similarity matching**
- **Configurable similarity thresholds**
- **Category-based filtering**
- **Real-time duplicate detection**

## 🐳 Docker Deployment

### **Build Container:**
```bash
docker build -t idea-hub:latest .
```

### **Run with Docker:**
```bash
docker run -p 8080:8080 \
  -e PG_HOST=your_db_host \
  -e PG_DB=idea_hub_db \
  -e PG_USER=your_user \
  -e PG_PASS=your_password \
  -e GEMINI_API_KEY=your_api_key \
  idea-hub:latest
```

### **Docker Compose:**
```yaml
version: '3.8'
services:
  idea-hub:
    build: .
    ports:
      - "8080:8080"
    environment:
      - PG_HOST=postgres
      - PG_DB=idea_hub_db
      - PG_USER=postgres
      - PG_PASS=password
    depends_on:
      - postgres
      
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: idea_hub_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 🔧 Configuration Options

### **Search Configuration:**
```python
SEARCH_THRESHOLD = 0.7  # Similarity threshold (0.0-1.0)
MAX_SEARCH_RESULTS = 50
DUPLICATE_THRESHOLD = 0.8
```

### **AI Configuration:**
```python
MCP_ENABLED = True
MCP_SERVER_URL = "http://localhost:8000"  # Optional MCP server
GEMINI_MODEL = "gemini-1.5-pro"
```

## 🧪 Testing

### **Test API Endpoints:**
```bash
# Health check
curl http://localhost:8080/api/health

# Test search
curl -X POST http://localhost:8080/api/ideas/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test idea"}'

# Test AI research
curl -X POST http://localhost:8080/api/mcp/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me innovation statistics"}'
```

## 🔍 Troubleshooting

### **Common Issues:**

1. **Database Connection Failed:**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -U your_user -d idea_hub_db
```

2. **Vector Extension Missing:**
```sql
-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
```

3. **Port Already in Use:**
```bash
# Find process using port 8080
lsof -ti:8080 | xargs kill -9
```

## 📊 Monitoring & Analytics

### **Built-in Analytics:**
- **Idea submission trends**
- **Search pattern analysis**
- **Contributor activity metrics**
- **AI tool usage statistics**

### **API Metrics:**
```bash
# Dashboard KPIs
curl http://localhost:8080/api/dashboard/kpis

# Trend analysis
curl http://localhost:8080/api/dashboard/trends
```

## 🚀 Advanced Features

### **MCP Server Integration:**
For enhanced AI capabilities, you can run the separate MCP server:

1. **Clone MCP Server:**
```bash
git clone https://github.com/nitish1888/idea-hub-mcp-server.git
```

2. **Configure MCP URL:**
```python
MCP_SERVER_URL = "http://localhost:8000"
```

## 🔐 Security

### **Production Security:**
- Use environment variables for sensitive data
- Enable HTTPS with reverse proxy
- Set up proper database permissions
- Use secure session keys

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues:** https://github.com/nitish1888/idea_hub/issues
- **Documentation:** See `/docs` directory for detailed guides

---

**🚀 Start innovating with AI-powered idea management today!**
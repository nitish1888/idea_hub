"""
Red Hat Idea Hub - Configuration Settings
=========================================

This module contains all configuration settings for the Red Hat Idea Hub application.
Based on patterns from idea_borad.ipynb notebook with environment variable support.

Configuration Categories:
-------------------------
1. Database Configuration: PostgreSQL connection settings
2. Vector Store Configuration: Settings for semantic search capabilities  
3. AI Service Configuration: API keys and model settings
4. Flask Application Configuration: Web server settings
5. Business Logic Configuration: Similarity thresholds and rules

Environment Variables:
---------------------
The following environment variables can be set to override default values:

Database:
- PG_DB: PostgreSQL database name (default: idea_hub_db)
- PG_USER: PostgreSQL username (default: idea_user)  
- PG_PASS: PostgreSQL password (default: secure_idea_pass)
- PG_HOST: PostgreSQL host (default: localhost)
- PG_PORT: PostgreSQL port (default: 5432)

AI Services:
- GEMINI_API_KEY: Google Gemini API key (required for AI features)
- GEMINI_MODEL: Gemini model version (default: gemini-2.5-flash)

Application:
- SECRET_KEY: Flask secret key (change for production)
- DEBUG: Enable debug mode (default: True)
- COLLECTION_NAME: Vector collection name (default: idea_hub_collection)

Usage:
------
from config.settings import Config

# Access database configuration
db_config = Config.DB_CONFIG

# Access AI configuration  
api_key = Config.GEMINI_API_KEY

Author: Red Hat Innovation Team
Last Updated: 2025
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
# This allows for local development configuration without hardcoding secrets
load_dotenv()

#=============================================================================
# MAIN CONFIGURATION CLASS
#=============================================================================

class Config:
    """
    Main configuration class for Red Hat Idea Hub
    
    This class centralizes all configuration settings and provides sensible
    defaults while allowing environment variable overrides for flexibility.
    
    Based on patterns established in idea_borad.ipynb notebook for consistency
    with the original development environment.
    """
    
    #=========================================================================
    # DATABASE CONFIGURATION
    #=========================================================================
    
    # PostgreSQL database connection settings
    # Static configuration for OpenShift deployment
    DB_CONFIG = {
        "dbname": os.getenv("PG_DB"),                          # Database name (from secret)
        "user": os.getenv("PG_USER"),                          # Database user (from secret)
        "password": os.getenv("PG_PASS"),                      # Database password (from secret)
        "host": os.getenv("PG_HOST"),                          # Database host (from secret)
        "port": os.getenv("PG_PORT")                           # Database port (from secret)
    }
    
    # Complete PostgreSQL connection string for database operations
    # Used by various database services and vector operations
    DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    
    #=========================================================================
    # VECTOR STORE CONFIGURATION
    #=========================================================================
    
    # Vector database settings for semantic search capabilities (static configuration)
    # These enable AI-powered similarity detection and search functionality
    VECTOR_TABLE_NAME = "idea_hub_embeddings"                 # Table storing vector embeddings
    COLLECTION_NAME = "idea_hub_collection"                    # Vector collection identifier (static)
    
    #=========================================================================
    # AI SERVICE CONFIGURATION
    #=========================================================================
    
    # Google Gemini AI configuration for text generation and analysis
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")              # API key (from secret)
    GEMINI_MODEL = "gemini-2.5-flash"                         # Model version (static)
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Smaller, reliable embedding model (384 dim)
    
    # Note: GEMINI_API_KEY must be set for AI features to work
    # Get your API key from: https://makersuite.google.com/app/apikey
    
    #=========================================================================
    # MCP AGENTIC AI CONFIGURATION
    #=========================================================================
    
    # MCP (Model Context Protocol) configuration for tool calling with Gemini (static)
    # MCP enables Gemini to use tools and interact with external systems autonomously
    MCP_ENABLED = True                                         # Always enabled (static)
    
    #=========================================================================
    # FLASK APPLICATION CONFIGURATION
    #=========================================================================
    
    # Flask web application settings (static for OpenShift)
    SECRET_KEY = "f9db3a3845ebd2c5ce837b44ed420a09ce915f7d88edfbd3943da2305fc4d740"  # Session encryption key (static)
    DEBUG = False                                              # Debug mode disabled for production (static)
    
    # SECURITY NOTE: Change SECRET_KEY for production deployment
    # Generate a secure key with: python -c "import secrets; print(secrets.token_hex(16))"
    
    #=========================================================================
    # BUSINESS LOGIC CONFIGURATION
    #=========================================================================
    
    # Similarity thresholds for AI-powered duplicate detection and collaboration
    # These values are based on testing and notebook analysis patterns
    DUPLICATE_THRESHOLD = 0.8      # 80% similarity = likely duplicate (show warning)
    COLLABORATION_THRESHOLD = 0.7  # 70% similarity = suggest collaboration (show in UI)
    SEARCH_THRESHOLD = 0.3         # 30% minimum relevance for search results (filter out noise)
    
    # Threshold Usage:
    # - DUPLICATE_THRESHOLD: Used in idea submission to detect potential duplicates
    # - COLLABORATION_THRESHOLD: Used to suggest similar ideas for collaboration
    # - SEARCH_THRESHOLD: Used to filter out irrelevant search results

#=============================================================================
# CONFIGURATION VALIDATION
#=============================================================================

def validate_config():
    """
    Validate that all required configuration is present and valid
    
    Returns:
        tuple: (is_valid: bool, error_message: str)
    
    This function should be called at application startup to ensure
    proper configuration before the application starts processing requests.
    """
    
    # Check for required AI configuration
    if not Config.GEMINI_API_KEY:
        return False, "GEMINI_API_KEY environment variable is required for AI features"
    
    # Validate database configuration
    required_db_fields = ["dbname", "user", "password", "host", "port"]
    for field in required_db_fields:
        if not Config.DB_CONFIG.get(field):
            return False, f"Database configuration missing: {field}"
    
    # Validate similarity thresholds
    if not (0 <= Config.SEARCH_THRESHOLD <= Config.COLLABORATION_THRESHOLD <= Config.DUPLICATE_THRESHOLD <= 1):
        return False, "Similarity thresholds must be in ascending order between 0 and 1"
    
    return True, "Configuration is valid"

#=============================================================================
# DEVELOPMENT HELPER FUNCTIONS
#=============================================================================

def print_config_summary():
    """
    Print a summary of current configuration settings
    
    Useful for debugging and verifying configuration during development.
    Sensitive information (passwords, API keys) are masked for security.
    """
    
    print("📋 Red Hat Idea Hub Configuration Summary")
    print("=" * 50)
    
    # Database configuration (mask password)
    print(f"🗄️  Database: {Config.DB_CONFIG['dbname']} @ {Config.DB_CONFIG['host']}:{Config.DB_CONFIG['port']}")
    print(f"👤 User: {Config.DB_CONFIG['user']}")
    print(f"🔒 Password: {'*' * len(Config.DB_CONFIG['password']) if Config.DB_CONFIG['password'] else 'NOT SET'}")
    
    # AI configuration (mask API key)
    print(f"🤖 AI Model: {Config.GEMINI_MODEL}")
    print(f"🔑 API Key: {'*' * 20}...{Config.GEMINI_API_KEY[-4:] if len(Config.GEMINI_API_KEY) > 4 else 'NOT SET'}")
    
    # Application configuration
    print(f"⚙️  Debug Mode: {Config.DEBUG}")
    print(f"📊 Vector Table: {Config.VECTOR_TABLE_NAME}")
    
    # Thresholds
    print(f"🎯 Duplicate Threshold: {Config.DUPLICATE_THRESHOLD * 100}%")
    print(f"🤝 Collaboration Threshold: {Config.COLLABORATION_THRESHOLD * 100}%")
    print(f"🔍 Search Threshold: {Config.SEARCH_THRESHOLD * 100}%")
    
    print("=" * 50)

#=============================================================================
# END OF CONFIGURATION
#============================================================================= 
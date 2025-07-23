#!/usr/bin/env python3
"""
Red Hat Idea Hub - Flask API Backend Server
===========================================

This is the main Flask application server that provides the REST API backend
for the Red Hat Idea Hub innovation management platform.

Architecture:
------------
- Modular design with separate blueprints for different functionality
- Based on patterns from idea_borad.ipynb notebook
- Clean separation of concerns (routes, models, services, config)

Key Features:
------------
- RESTful API endpoints for idea management
- AI-powered semantic search and duplicate detection
- PostgreSQL database integration with vector extensions
- CORS enabled for frontend communication
- Comprehensive logging and error handling

Dependencies:
------------
- Flask: Web framework
- Flask-CORS: Cross-origin resource sharing
- PostgreSQL: Primary database
- Vector extensions: For semantic search
- AI services: Gemini, HuggingFace

File Structure Integration:
--------------------------
- config/: Configuration management
- routes/: API endpoint blueprints  
- models/: Data models and database operations
- services/: AI and external service integrations
- database/: Database connection and setup

Usage:
-----
1. Ensure PostgreSQL is running with vector extensions
2. Set environment variables (GEMINI_API_KEY, DATABASE_URL)
3. Run: python app.py
4. API available at: http://localhost:5001

Author: Red Hat Innovation Team
Last Updated: 2025
"""

import logging
from flask import Flask
from flask_cors import CORS

# Import our modular components
from config.settings import Config
from routes import register_blueprints

#=============================================================================
# APPLICATION FACTORY
#=============================================================================

def create_app():
    """
    Create and configure the Flask application
    
    This function implements the application factory pattern, allowing
    for easy testing and configuration management.
    
    Returns:
        Flask: Configured Flask application instance
    
    Configuration:
        - Loads settings from Config class
        - Enables CORS for frontend communication
        - Sets up logging with appropriate format
        - Registers all API blueprint routes
    """
    
    # Create Flask app instance
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for frontend-backend communication
    # Allows Streamlit app (port 8501) to communicate with Flask API (port 5001)
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",                                    # Allow all origins (configure for production)
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allowed HTTP methods
            "allow_headers": ["Content-Type", "Authorization"]       # Allowed headers
        }
    })
    
    # Configure application logging
    # Provides structured logs for debugging and monitoring
    logging.basicConfig(
        level=logging.INFO,                                    # Log level (INFO and above)
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Log format
    )
    
    # Register all route blueprints from routes/ directory
    # This modular approach keeps routes organized by functionality
    register_blueprints(app)
    
    return app

#=============================================================================
# MAIN APPLICATION ENTRY POINT
#=============================================================================

def main():
    """
    Main entry point for the Flask API server
    
    This function:
    1. Creates the Flask application using the factory pattern
    2. Displays startup information and available endpoints
    3. Starts the development server
    
    Server Configuration:
        - Host: 0.0.0.0 (accessible from all interfaces)
        - Port: 5001 (must match frontend API_BASE_URL)
        - Debug: Controlled by Config.DEBUG setting
    """
    
    # Create the Flask application
    app = create_app()
    
    # Display startup banner and information
    print("🚀 Starting Red Hat Idea Hub - Modular API Backend")
    print("📝 Based on idea_borad.ipynb notebook patterns")
    print("\n🔍 Available endpoints:")
    
    # Health and Status endpoints
    print("  GET  /api/health - Health check")
    print("  GET  /api/status - Detailed system status")
    
    # Database management endpoints
    print("  POST /api/init-database - Initialize database")
    print("  POST /api/load-sample-data - Load notebook sample data")
    
    # Core idea management endpoints
    print("  GET  /api/ideas - Get all ideas")
    print("  GET  /api/ideas/<id> - Get specific idea") 
    print("  POST /api/ideas/submit - Submit new idea with AI analysis")
    print("  POST /api/ideas/search - AI-powered semantic search")
    
    # Dashboard and analytics endpoints
    print("  GET  /api/dashboard/kpis - Dashboard metrics")
    print("  GET  /api/dashboard/insights - AI-generated insights")
    print("  GET  /api/dashboard/trends - Trend analysis")
    
    # Display configuration information
    print(f"\n🌐 Server starting on http://localhost:5001")
    print(f"🗄️  Database: {Config.DB_CONFIG['dbname']}")
    print(f"🤖 AI Service: {'Enabled' if Config.GEMINI_API_KEY else 'Disabled (set GEMINI_API_KEY)'}")
    print(f"📊 Vector Store: {Config.VECTOR_TABLE_NAME}")
    
    # Start the Flask development server
    # Note: For production, use a WSGI server like gunicorn
    app.run(
        debug=Config.DEBUG,        # Enable/disable debug mode
        host='0.0.0.0',           # Listen on all interfaces
        port=5001                 # API server port (must match frontend)
    )

#=============================================================================
# SCRIPT EXECUTION
#=============================================================================

if __name__ == "__main__":
    """
    Direct script execution entry point
    
    This allows the script to be run directly with:
    python app.py
    
    For production deployment, use a WSGI server:
    gunicorn -w 4 -b 0.0.0.0:5001 app:create_app()
    """
    main()

#=============================================================================
# END OF FILE
#============================================================================= 
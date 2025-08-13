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
import warnings
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user

# Suppress non-critical SSL warnings in development
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")

# Import our modular components
from config.settings import Config
from routes import register_blueprints
from routes.mcp_routes import mcp_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.user import user_bp
from models.admin import AdminAuth

#=============================================================================
# APPLICATION FACTORY
#=============================================================================

def create_app():
    """
    Create and configure the Flask application with dual-view architecture
    
    This function implements the application factory pattern with:
    - User view (public, no login required)
    - Admin view (protected, authentication required)
    
    Returns:
        Flask: Configured Flask application instance
    
    Configuration:
        - Loads settings from Config class
        - Sets up Flask-Login for admin authentication
        - Enables CORS for frontend communication
        - Sets up logging with appropriate format
        - Registers all blueprint routes (user, admin, auth, API)
    """
    
    # Create Flask app instance
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Set secret key for sessions
    app.secret_key = Config.SECRET_KEY or 'dev-secret-key-change-in-production'
    
    # Initialize Flask-Login for admin authentication
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.admin_login'
    login_manager.login_message = 'Please log in to access admin features.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load admin user for Flask-Login"""
        return AdminAuth.get_admin_by_id(user_id)
    
    # Enable CORS for frontend-backend communication  
    # Production: Configure specific allowed origins for security
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5001,http://127.0.0.1:5001").split(",")
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,                        # Specific allowed origins for production security
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allowed HTTP methods
            "allow_headers": ["Content-Type", "Authorization"]       # Allowed headers
        }
    })
    
    # Configure application logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register blueprint routes
    register_blueprints(app)          # Original API routes
    app.register_blueprint(mcp_bp)    # MCP agentic AI routes
    app.register_blueprint(auth_bp)   # Authentication routes
    app.register_blueprint(admin_bp)  # Admin-protected routes  
    app.register_blueprint(user_bp)   # Public user routes
    
    # Register dual-view frontend routes
    register_frontend_routes(app)
    
    return app

#=============================================================================
# FRONTEND ROUTES - NEW WEB UI
#=============================================================================

def register_frontend_routes(app):
    """Register dual-view frontend routes (user vs admin)"""
    
    @app.route('/')
    def landing_page():
        """Landing page - redirect based on authentication"""
        if current_user.is_authenticated:
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('user.user_landing'))
    
    @app.route('/dashboard')
    @login_required
    def legacy_dashboard():
        """Legacy dashboard redirect to admin dashboard"""
        return redirect(url_for('admin.admin_dashboard'))
    
    @app.route('/submit')
    def submit_idea():
        """Submit idea page"""
        return render_template('submit.html')
    
    @app.route('/search')
    def search_ideas():
        """Search ideas page"""
        return render_template('search.html')
    
    @app.route('/browse')
    def browse_ideas():
        """Browse ideas page"""
        return render_template('browse.html')
    
    @app.route('/health-check')
    def health_check():
        """Quick health check page"""
        return render_template('health.html')
    
    @app.route('/contributors')
    def contributors():
        """Contributors page"""
        return render_template('contributors.html')
    
    @app.route('/ai-research')
    def ai_research():
        """AI Research Assistant page"""
        return render_template('ai_research.html')
    
    @app.route('/api/contributors', methods=['GET', 'POST'])
    def handle_contributors():
        """Handle contributor registration and listing using database"""
        from models.contributor import ContributorModel
        
        if request.method == 'POST':
            try:
                # Get and validate contributor data
                data = request.get_json()
                
                # Map frontend field names to database field names
                contributor_data = {
                    'name': data.get('name'),
                    'manager_name': data.get('manager'),  # Frontend sends 'manager'
                    'skillset': data.get('skillset'),
                    'hours_available': data.get('hours'),  # Frontend sends 'hours'
                    'email': data.get('email'),
                    'department': data.get('department')
                }
                
                # Validate required fields
                required_fields = ['name', 'manager_name', 'skillset', 'hours_available']
                for field in required_fields:
                    if not contributor_data.get(field):
                        return jsonify({
                            "status": "error", 
                            "message": f"Missing required field: {field}"
                        }), 400
                
                # Create contributor in database
                new_contributor = ContributorModel.create_contributor(contributor_data)
                
                return jsonify({
                    "status": "success", 
                    "contributor": new_contributor
                })
                
            except Exception as e:
                logging.error(f"Error creating contributor: {e}")
                return jsonify({
                    "status": "error",
                    "message": "Failed to register contributor"
                }), 500
        
        else:
            # GET request - get all contributors
            try:
                contributors = ContributorModel.get_all_contributors()
                return jsonify({"contributors": contributors})
                
            except Exception as e:
                logging.error(f"Error fetching contributors: {e}")
                return jsonify({
                    "status": "error",
                    "message": "Failed to fetch contributors"
                }), 500
    
    @app.route('/api/contributors/<int:contributor_id>', methods=['GET', 'PUT', 'DELETE'])
    def handle_single_contributor(contributor_id):
        """Handle individual contributor operations"""
        from models.contributor import ContributorModel
        
        if request.method == 'GET':
            try:
                contributor = ContributorModel.get_contributor_by_id(contributor_id)
                if not contributor:
                    return jsonify({"status": "error", "message": "Contributor not found"}), 404
                
                return jsonify({"contributor": contributor})
                
            except Exception as e:
                logging.error(f"Error fetching contributor {contributor_id}: {e}")
                return jsonify({"status": "error", "message": "Failed to fetch contributor"}), 500
        
        elif request.method == 'PUT':
            try:
                data = request.get_json()
                updated_contributor = ContributorModel.update_contributor(contributor_id, data)
                
                if not updated_contributor:
                    return jsonify({"status": "error", "message": "Contributor not found"}), 404
                
                return jsonify({
                    "status": "success",
                    "contributor": updated_contributor
                })
                
            except Exception as e:
                logging.error(f"Error updating contributor {contributor_id}: {e}")
                return jsonify({"status": "error", "message": "Failed to update contributor"}), 500
        
        elif request.method == 'DELETE':
            try:
                success = ContributorModel.delete_contributor(contributor_id)
                
                if not success:
                    return jsonify({"status": "error", "message": "Contributor not found"}), 404
                
                return jsonify({"status": "success", "message": "Contributor deleted"})
                
            except Exception as e:
                logging.error(f"Error deleting contributor {contributor_id}: {e}")
                return jsonify({"status": "error", "message": "Failed to delete contributor"}), 500
    
    @app.route('/api/contributors/stats')
    def get_contributor_stats():
        """Get contributor statistics for dashboard"""
        try:
            from models.contributor import ContributorModel
            stats = ContributorModel.get_contributor_stats()
            return jsonify(stats)
            
        except Exception as e:
            logging.error(f"Error fetching contributor stats: {e}")
            return jsonify({
                "total_contributors": 0,
                "total_hours_per_week": 0,
                "unique_skills": 0,
                "recent_registrations": 0
            }), 500
    
    @app.route('/api/contributors/search')
    def search_contributors():
        """Search contributors with filters"""
        try:
            from models.contributor import ContributorModel
            
            search_term = request.args.get('q')
            skill_filter = request.args.get('skill')
            hours_filter = request.args.get('hours')
            
            contributors = ContributorModel.search_contributors(
                search_term=search_term,
                skill_filter=skill_filter,
                hours_filter=hours_filter
            )
            
            return jsonify({"contributors": contributors})
            
        except Exception as e:
            logging.error(f"Error searching contributors: {e}")
            return jsonify({"status": "error", "message": "Search failed"}), 500

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
    print("🚀 Starting Red Hat Idea Hub - Modern Web Application")
    print("📝 Flask backend with modern HTML/CSS/JS frontend")
    print("\n🎨 Web Interface:")
    print("  GET  / - Main Dashboard")
    print("  GET  /submit - Submit Innovation Ideas")
    print("  GET  /search - AI-Powered Search")
    print("  GET  /browse - Browse All Ideas")
    print("  GET  /contributors - Innovation Contributors")
    print("  GET  /health-check - System Health Monitor")
    
    print("\n🔍 API endpoints:")
    
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
    
    # Contributor management endpoints
    print("  GET/POST /api/contributors - Contributor management")
    print("  GET  /api/contributors/stats - Contributor statistics")
    print("  GET  /api/contributors/search - Search contributors")
    print("  GET/PUT/DELETE /api/contributors/<id> - Individual contributor operations")
    
    # MCP Agentic AI endpoints
    print("  GET  /api/mcp/status - MCP agent status and capabilities")
    print("  POST /api/mcp/research - Autonomous AI research with tool calling")
    
    # Display configuration information
    print(f"\n🌐 Web Application: http://localhost:5001")
    print(f"🌐 API Server: http://localhost:5001/api")
    print(f"🗄️  Database: {Config.DB_CONFIG['dbname']}")
    print(f"🤖 AI Service: {'Enabled' if Config.GEMINI_API_KEY else 'Disabled (set GEMINI_API_KEY)'}")
    print(f"📊 Vector Store: {Config.VECTOR_TABLE_NAME}")
    
    # Initialize admin authentication system
    print(f"\n🔐 Initializing admin authentication system...")
    if AdminAuth.initialize_admin_system():
        print(f"✅ Admin system ready - Access via /admin/login")
    else:
        print(f"⚠️  Admin system initialization failed - check database connection")
    
    print(f"\n💡 Open http://localhost:5001 in your browser to access the Idea Hub")
    
    # Start the Flask development server
    # Note: For production, use a WSGI server like gunicorn
    app.run(
        debug=Config.DEBUG,        # Enable/disable debug mode
        host='0.0.0.0',           # Listen on all interfaces
        port=8080,                  # API server port (OpenShift standard)               
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
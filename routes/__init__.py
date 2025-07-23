"""
Routes package initialization
Registers all blueprints with the Flask app
"""

from .health import health_bp
from .ideas import ideas_bp
from .dashboard import dashboard_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(health_bp)
    app.register_blueprint(ideas_bp)
    app.register_blueprint(dashboard_bp)

__all__ = ['register_blueprints'] 
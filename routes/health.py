"""
Idea Hub - Health Check API Routes
==========================================

This module contains Flask Blueprint routes for monitoring application health
and system status. These endpoints are essential for:

- Application monitoring and alerting
- Load balancer health checks  
- Container orchestration readiness probes
- Development debugging and troubleshooting

API Endpoints:
-------------
- GET /api/health: Basic health check for quick status verification
- GET /api/status: Detailed system status with component breakdown

Dependencies Checked:
--------------------
- PostgreSQL database connectivity and extensions
- AI service (Gemini) availability and configuration
- Vector store readiness for semantic search

Usage:
------
# Basic health check
curl http://localhost:5001/api/health

# Detailed status
curl http://localhost:5001/api/status

Response Formats:
----------------
Health endpoint returns:
{
    "status": "healthy|error",
    "database": "connected|disconnected", 
    "pgvector": "enabled|not_installed",
    "gemini": "enabled|disabled",
    "version": "1.0.0"
}

Status endpoint returns:
{
    "status": "healthy|degraded|error",
    "services": {
        "database": "healthy|error",
        "ai_service": "available|unavailable", 
        "vector_store": "ready|error"
    },
    "database_info": { ... }
}

Author: Innovation Team
Last Updated: 2025
"""

from flask import Blueprint, jsonify
from database.connection import test_connection
from services.ai_service import gemini_service

#=============================================================================
# HEALTH CHECK BLUEPRINT
#=============================================================================

# Create Flask Blueprint for health-related routes
# This allows modular organization of routes by functionality
health_bp = Blueprint('health', __name__)

#=============================================================================
# BASIC HEALTH CHECK ENDPOINT
#=============================================================================

@health_bp.route('/api/health', methods=['GET'])
def health_check():
    """
    Basic health check endpoint for quick system status verification
    
    Returns:
        JSON response with system health status
        
    HTTP Status Codes:
        200: System is healthy and operational
        500: Critical system error (handled by Flask error handlers)
    
    This endpoint is designed for:
    - Load balancer health checks (fast response)
    - Container orchestration readiness probes
    - Basic monitoring and alerting systems
    - Development environment verification
    
    Response includes:
    - Database connectivity status
    - PostgreSQL vector extension availability
    - AI service (Gemini) status
    - Application version
    
    Example Response:
    {
        "status": "healthy",
        "database": "connected",
        "pgvector": "enabled", 
        "gemini": "enabled",
        "version": "1.0.0"
    }
    """
    
    # Test database connection and extensions
    # This verifies PostgreSQL connectivity and required extensions
    db_status = test_connection()
    
    # Check AI service availability
    # This verifies Gemini API configuration and connectivity
    ai_status = "enabled" if gemini_service.is_available() else "disabled"
    
    # Return combined health status
    # Includes all critical system components
    return jsonify({
        **db_status,                    # Spread database status (status, database, pgvector, config)
        "gemini": ai_status,           # AI service status
        "version": "1.0.0"             # Application version for compatibility tracking
    })

#=============================================================================
# DETAILED STATUS ENDPOINT
#=============================================================================

@health_bp.route('/api/status', methods=['GET'])
def detailed_status():
    """
    Detailed system status endpoint for comprehensive health monitoring
    
    Returns:
        JSON response with detailed component status
        
    HTTP Status Codes:
        200: Status retrieved successfully (may indicate degraded services)
        500: Critical system error preventing status check
    
    This endpoint provides:
    - Individual service health status
    - Overall system health assessment
    - Detailed error information for troubleshooting
    - Component-specific status details
    
    Used for:
    - Administrative monitoring dashboards
    - Detailed troubleshooting and debugging
    - Service dependency analysis
    - Performance monitoring integration
    
    Overall Status Logic:
    - "healthy": All services operational
    - "degraded": Some non-critical services unavailable
    - "error": Critical services unavailable
    
    Example Response:
    {
        "status": "healthy",
        "services": {
            "database": "healthy",
            "ai_service": "available",
            "vector_store": "ready"
        },
        "database_info": {
            "status": "healthy",
            "database": "connected",
            "pgvector": "enabled",
            "config": "idea_hub_db"
        }
    }
    """
    
    # Test database connection with detailed information
    db_status = test_connection()
    
    # Assess individual service status
    # Each service is evaluated independently for granular monitoring
    services = {
        "database": db_status.get("status", "unknown"),           # PostgreSQL connectivity
        "ai_service": "available" if gemini_service.is_available() else "unavailable",  # Gemini AI
        "vector_store": "ready"                                   # Vector search capability
        # Note: Could add more specific vector service checks here in the future
    }
    
    # Determine overall system health based on service status
    # System is healthy only if all critical services are operational
    healthy_statuses = ["healthy", "connected", "available", "ready"]
    overall_status = "healthy" if all(
        status in healthy_statuses for status in services.values()
    ) else "degraded"
    
    # Return comprehensive status information
    return jsonify({
        "status": overall_status,       # Overall system health assessment
        "services": services,           # Individual service status
        "database_info": db_status      # Detailed database information
    })

#=============================================================================
# END OF HEALTH CHECK ROUTES
#============================================================================= 
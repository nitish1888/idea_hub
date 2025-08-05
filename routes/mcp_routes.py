"""
Red Hat Idea Hub - MCP Agentic AI Routes
========================================

API endpoints for MCP-based agentic AI features
"""

from flask import Blueprint, request, jsonify
import logging
import asyncio
from services.mcp_agentic_service import mcp_agentic_service

# Create blueprint for MCP agentic AI routes
mcp_bp = Blueprint('mcp_agentic', __name__)

@mcp_bp.route('/api/mcp/status', methods=['GET'])
def get_mcp_status():
    """Get MCP agentic AI service status"""
    try:
        status = {
            "available": mcp_agentic_service.is_available(),
            "service_type": "MCP-powered Gemini Agent",
            "capabilities": [
                "Autonomous research with tool calling",
                "Database queries and vector search",
                "Multi-step reasoning workflows",
                "Implementation roadmap generation",
                "Feasibility analysis"
            ],
            "tools_available": [
                "search_similar_ideas",
                "get_idea_details", 
                "analyze_contributor_skills",
                "get_innovation_trends",
                "evaluate_idea_feasibility",
                "create_implementation_roadmap"
            ]
        }
        
        if not status["available"]:
            status["setup_required"] = "Configure GEMINI_API_KEY in .env file"
        
        return jsonify(status)
        
    except Exception as e:
        logging.error(f"Error getting MCP status: {e}")
        return jsonify({"error": str(e)}), 500

@mcp_bp.route('/api/mcp/research', methods=['POST'])
def autonomous_research():
    """Execute autonomous research using MCP tools"""
    try:
        if not mcp_agentic_service.is_available():
            return jsonify({
                "status": "error",
                "message": "MCP service not available - check Gemini API key configuration"
            }), 503
        
        data = request.get_json()
        research_query = data.get('query')
        
        if not research_query:
            return jsonify({"error": "Research query is required"}), 400
        
        # Run async research
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                mcp_agentic_service.execute_autonomous_research(research_query)
            )
        finally:
            loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error in MCP research: {e}")
        return jsonify({
            "status": "error",
            "message": f"Research failed: {str(e)}"
        }), 500
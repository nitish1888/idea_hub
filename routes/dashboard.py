"""
Dashboard routes for KPIs and AI insights
"""

from flask import Blueprint, jsonify
from datetime import datetime
from models.idea import IdeaModel
from services.ai_service import gemini_service
import logging

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api/dashboard/kpis', methods=['GET'])
def get_dashboard_kpis():
    """Get dashboard KPIs and statistics"""
    try:
        # Get idea stats (includes unique idea submitters)
        stats = IdeaModel.get_dashboard_stats()
        
        # Get actual contributor stats (people who joined as contributors)
        from models.contributor import ContributorModel
        contributor_stats = ContributorModel.get_contributor_stats()
        
        # Combine both stats with clear naming
        combined_stats = {
            **stats,
            "total_contributors": contributor_stats.get("total_contributors", 0),  # People who joined as contributors
            "idea_authors": stats.get("unique_contributors", 0),  # People who submitted ideas
            "last_updated": datetime.now().isoformat()
        }
        
        return jsonify(combined_stats)
        
    except Exception as e:
        logging.error(f"Error getting dashboard KPIs: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/api/dashboard/insights', methods=['GET'])
def get_ai_insights():
    """Get AI-generated insights about the idea hub"""
    if not gemini_service.is_available():
        return jsonify({
            "error": "AI service not available",
            "insights": ["AI insights require Gemini API key configuration"]
        }), 503
    
    try:
        # Get current statistics
        stats = IdeaModel.get_dashboard_stats()
        
        # Generate AI insights
        insights = gemini_service.generate_insights({
            "total_ideas": stats.get("total_ideas", 0),
            "categories": stats.get("category_breakdown", {}),
            "impacts": stats.get("impact_breakdown", {})
        })
        
        return jsonify({
            "insights": insights,
            "data_summary": stats,
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error generating AI insights: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/api/dashboard/trends', methods=['GET'])
def get_trends():
    """Get trend analysis of ideas"""
    try:
        stats = IdeaModel.get_dashboard_stats()
        
        # Basic trend analysis
        trends = {
            "most_popular_category": max(stats.get("category_breakdown", {}).items(), 
                                       key=lambda x: x[1], default=("N/A", 0)),
            "highest_impact_count": stats.get("impact_breakdown", {}).get("High", 0),
            "total_contributors": stats.get("unique_contributors", 0),
            "recent_activity": stats.get("recent_submissions", 0)
        }
        
        return jsonify({
            "trends": trends,
            "breakdown": {
                "categories": stats.get("category_breakdown", {}),
                "impacts": stats.get("impact_breakdown", {}),
                "statuses": stats.get("status_breakdown", {})
            },
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error getting trends: {e}")
        return jsonify({"error": str(e)}), 500 
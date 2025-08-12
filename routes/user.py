"""
Red Hat Idea Hub - User Routes
==============================

Public user routes for the dual-view architecture.
Provides simplified, clean interface for basic functionality.
"""

from flask import Blueprint, render_template, request, jsonify
from models.idea import IdeaModel
from models.contributor import ContributorModel
from services.ai_service import gemini_service
from services.vector_service import vector_service
import logging

# Create blueprint for public user routes
user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def user_landing():
    """Clean user landing page - no KPIs, focused on actions"""
    return render_template('user/landing.html')

@user_bp.route('/submit')
def user_submit():
    """User idea submission page"""
    return render_template('user/submit.html')

@user_bp.route('/contributors')
def user_contributors():
    """Find contributors page for users"""
    return render_template('user/contributors.html')

@user_bp.route('/contribute')
def user_contribute():
    """Join as contributor page"""
    return render_template('user/contribute.html')

@user_bp.route('/browse')
def user_browse():
    """Browse ideas page (simplified for users)"""
    return render_template('user/browse.html')

# API Routes for user functionality

@user_bp.route('/api/user/submit-idea', methods=['POST'])
def submit_idea():
    """Submit a new idea (user-friendly version)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        submitter_name = data.get('submitter_name', '').strip()
        submitter_email = data.get('submitter_email', '').strip()
        
        if not all([title, description, submitter_name, submitter_email]):
            return jsonify({
                "status": "error",
                "message": "All fields are required: title, description, name, and email"
            }), 400
        
        # Optional fields
        category = data.get('category', 'General')
        impact = data.get('impact', 'Medium')
        effort = data.get('effort', 'Medium')
        looking_for_contributors = data.get('looking_for_contributors', False)
        
        # Add collaboration indicator to description if needed
        if looking_for_contributors and 'looking for' not in description.lower():
            description += '\n\nNote: This idea is actively looking for contributors and collaborators.'
        
        # Submit the idea (map to database fields correctly)
        idea_data = {
            'title': title,
            'description': description,
            'contributor': submitter_name,  # Map submitter_name to contributor field
            'category': category,
            'impact': impact,
            'status': 'Under Review'  # Use consistent status
        }
        
        result = IdeaModel.create_idea(idea_data)
        
        if result.get('status') == 'success':
            # Add to vector store for similarity search
            try:
                if vector_service.is_available():
                    vector_service.add_idea_to_vector_store(result['idea'])
            except Exception as ve:
                logging.warning(f"Vector store update failed: {ve}")
            
            return jsonify({
                "status": "success",
                "message": "Your idea has been submitted successfully! Thank you for contributing to Red Hat innovation.",
                "idea_id": result.get('idea_id'),
                "next_steps": [
                    "Your idea will be reviewed by our innovation team",
                    "You'll receive email updates on its progress",
                    "Consider browsing for contributors who can help implement it"
                ]
            })
        else:
            return jsonify({
                "status": "error", 
                "message": result.get('message', 'Failed to submit idea')
            }), 500
    
    except Exception as e:
        logging.error(f"❌ Error submitting user idea: {e}")
        return jsonify({
            "status": "error",
            "message": "Sorry, there was an issue submitting your idea. Please try again."
        }), 500

@user_bp.route('/api/user/contributors/search')
def search_contributors():
    """Search for contributors by skills"""
    try:
        query = request.args.get('skills', '').strip()
        
        if not query:
            # Return all contributors if no specific search
            contributors = ContributorModel.get_all_contributors()
        else:
            # Search contributors by skills
            contributors = ContributorModel.search_contributors(query)
        
        # Format for user-friendly display
        formatted_contributors = []
        for contributor in contributors:
            # Map database fields to user-friendly format
            formatted_contributor = {
                "id": contributor.get('id'),
                "name": contributor.get('name'),
                "skills": contributor.get('skillset', ''),  # Database field is 'skillset'
                "experience": contributor.get('experience', 'Mid-level'),  # Default experience level
                "availability": contributor.get('hours', 'Flexible'),  # Database field is 'hours'
                "email": contributor.get('email', ''),
                "department": contributor.get('department', '')
            }
            formatted_contributors.append(formatted_contributor)
        
        return jsonify({
            "status": "success",
            "contributors": formatted_contributors,
            "total_found": len(formatted_contributors),
            "search_query": query or "all contributors"
        })
        
    except Exception as e:
        logging.error(f"❌ Error searching contributors: {e}")
        return jsonify({
            "status": "error",
            "message": "Sorry, there was an issue searching for contributors."
        }), 500

@user_bp.route('/api/user/contribute', methods=['POST'])
def join_as_contributor():
    """Join as a contributor (user-friendly version)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        skills = data.get('skills', '').strip()
        
        if not all([name, email, skills]):
            return jsonify({
                "status": "error",
                "message": "Name, email, and skills are required to join as a contributor"
            }), 400
        
        # Optional fields with user-friendly defaults
        experience = data.get('experience', 'Mid-level')
        hours_per_week = data.get('hours_per_week', 5)  # Default 5 hours
        motivation = data.get('motivation', 'Contributing to Red Hat innovation')
        
        contributor_data = {
            'name': name,
            'email': email,
            'skillset': skills,  # Map to database field name
            'hours_available': f"{hours_per_week} hours/week",  # Map to database field name  
            'manager_name': motivation or 'Self-motivated contributor',  # Use motivation as manager for now
            'department': 'Innovation Community'  # Default department
        }
        
        result = ContributorModel.create_contributor(contributor_data)
        
        if result.get('status') == 'success':
            return jsonify({
                "status": "success",
                "message": f"Welcome aboard, {name}! You're now part of the Red Hat innovation community.",
                "contributor_id": result.get('contributor_id'),
                "next_steps": [
                    "Browse innovative ideas that match your skills",
                    "Connect with idea submitters to offer your expertise",
                    "Join our innovation community discussions"
                ]
            })
        else:
            return jsonify({
                "status": "error",
                "message": result.get('message', 'Failed to register as contributor')
            }), 500
    
    except Exception as e:
        logging.error(f"❌ Error registering contributor: {e}")
        return jsonify({
            "status": "error",
            "message": "Sorry, there was an issue with your registration. Please try again."
        }), 500

@user_bp.route('/api/user/ideas/browse')
def browse_ideas():
    """Browse ideas (user-simplified version)"""
    try:
        ideas = IdeaModel.get_all_ideas()
        
        # Simplify ideas for user view - remove admin-specific data
        user_friendly_ideas = []
        for idea in ideas:
            # Determine collaboration status based on idea content
            description_lower = (idea.get('description', '') + ' ' + idea.get('title', '')).lower()
            looking_for_help = any(keyword in description_lower for keyword in [
                'looking for', 'need', 'seeking', 'want', 'require', 'help', 
                'collaborate', 'contributor', 'team', 'partner', 'assist',
                'join', 'work with', 'collaboration', 'together'
            ])
            
            user_idea = {
                "id": idea.get('id'),
                "title": idea.get('title'),
                "description": idea.get('description'),
                "category": idea.get('category', 'General'),
                "impact": idea.get('impact', 'Medium'),
                "submitter_name": idea.get('submitter_name', 'Anonymous'),
                "date_submitted": idea.get('created_at', 'Recently'),
                "looking_for_contributors": looking_for_help,  # Dynamic based on content
                "collaboration_status": "seeking_collaborators" if looking_for_help else "open_to_collaboration",
                "skills_needed": idea.get('tags', '').split(',') if idea.get('tags') else []
            }
            user_friendly_ideas.append(user_idea)
        
        return jsonify({
            "status": "success",
            "ideas": user_friendly_ideas,
            "total_ideas": len(user_friendly_ideas),
            "categories": list(set([idea.get('category', 'General') for idea in user_friendly_ideas]))
        })
        
    except Exception as e:
        logging.error(f"❌ Error browsing ideas: {e}")
        return jsonify({
            "status": "error",
            "message": "Sorry, there was an issue loading ideas."
        }), 500

@user_bp.route('/api/user/system/status')
def user_system_status():
    """Simple system status for users"""
    try:
        return jsonify({
            "status": "online",
            "message": "Red Hat Idea Hub is ready for your innovations!",
            "services": {
                "idea_submission": "available",
                "contributor_search": "available", 
                "community_features": "available"
            },
            "user_features": [
                "Submit innovative ideas",
                "Find skilled contributors", 
                "Join as a contributor",
                "Browse community innovations"
            ]
        })
        
    except Exception as e:
        logging.error(f"❌ Error getting user system status: {e}")
        return jsonify({
            "status": "error",
            "message": "System status unavailable"
        }), 500
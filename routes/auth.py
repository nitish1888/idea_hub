"""
Idea Hub - Authentication Routes
========================================

Authentication routes for the dual-view architecture.
Handles admin login/logout and session management.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models.admin import AdminAuth
import logging

# Create blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page and authentication handler"""
    
    if request.method == 'GET':
        # Render login page
        return render_template('admin/login.html')
    
    try:
        # Handle login form submission
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            if request.is_json:
                return jsonify({
                    "status": "error", 
                    "message": "Username and password are required"
                }), 400
            flash("Username and password are required", "error")
            return render_template('admin/login.html')
        
        # Verify admin credentials
        admin_user = AdminAuth.verify_password(username, password)
        
        if admin_user:
            # Login successful
            login_user(admin_user, remember=True)
            
            # Log successful login
            logging.info(f"✅ Admin login successful: {username}")
            
            if request.is_json:
                return jsonify({
                    "status": "success",
                    "message": "Login successful",
                    "redirect_url": "/admin/dashboard",
                    "admin": {
                        "username": username,
                        "id": admin_user.id
                    }
                })
            
            flash(f"Welcome back, {username}!", "success")
            next_page = request.args.get('next')
            return redirect(next_page if next_page else '/admin/dashboard')
        
        else:
            # Login failed
            logging.warning(f"❌ Admin login failed: {username}")
            
            if request.is_json:
                return jsonify({
                    "status": "error",
                    "message": "Invalid username or password"
                }), 401
            
            flash("Invalid username or password", "error")
            return render_template('admin/login.html')
    
    except Exception as e:
        logging.error(f"❌ Error in admin login: {e}")
        if request.is_json:
            return jsonify({"status": "error", "message": "Login system error"}), 500
        flash("Login system error. Please try again.", "error")
        return render_template('admin/login.html')

@auth_bp.route('/admin/logout', methods=['GET', 'POST'])
@login_required
def admin_logout():
    """Admin logout handler"""
    try:
        username = current_user.username if current_user.is_authenticated else "Unknown"
        logout_user()
        session.clear()
        
        logging.info(f"✅ Admin logout: {username}")
        
        if request.is_json:
            return jsonify({
                "status": "success",
                "message": "Logged out successfully",
                "redirect_url": "/"
            })
        
        flash("You have been logged out successfully", "info")
        return redirect('/')
    
    except Exception as e:
        logging.error(f"❌ Error in admin logout: {e}")
        if request.is_json:
            return jsonify({"status": "error", "message": "Logout error"}), 500
        return redirect('/')

@auth_bp.route('/api/admin/status', methods=['GET'])
def admin_status():
    """Get current admin authentication status"""
    try:
        if current_user.is_authenticated:
            return jsonify({
                "authenticated": True,
                "admin": {
                    "username": current_user.username,
                    "id": current_user.id
                },
                "permissions": [
                    "dashboard_access",
                    "idea_management", 
                    "ai_research",
                    "analytics_access",
                    "contributor_management"
                ]
            })
        else:
            return jsonify({
                "authenticated": False,
                "redirect_url": "/admin/login"
            })
    
    except Exception as e:
        logging.error(f"❌ Error checking admin status: {e}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/api/admin/info', methods=['GET'])
def admin_info():
    """Get admin system information (for development/setup)"""
    try:
        info = AdminAuth.get_admin_info()
        
        # Add demo credentials for development
        info["demo_credentials"] = {
            "admin": "hello",
            "rhadmin": "company123"
        }
        
        return jsonify(info)
    
    except Exception as e:
        logging.error(f"❌ Error getting admin info: {e}")
        return jsonify({"error": str(e)}), 500
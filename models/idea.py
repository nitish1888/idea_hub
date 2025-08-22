"""
Idea Hub - Idea Data Model
==================================

This module contains the IdeaModel class which handles all database operations
related to innovation ideas. It provides a clean interface between the application
logic and the PostgreSQL database.

Key Features:
------------
- CRUD operations for innovation ideas
- PDF metadata management
- Batch operations for data loading
- Dashboard analytics and statistics
- Comprehensive error handling and logging

Database Schema:
---------------
The ideas table contains the following columns:
- id: Primary key (auto-incrementing integer)
- title: Idea title (VARCHAR, required)
- description: Detailed description (TEXT, required)
- abstract: Short summary (TEXT, optional)
- contributor: Person who submitted the idea (VARCHAR, required)
- category: Idea category (VARCHAR, required)
- impact: Expected impact level (VARCHAR, required)
- status: Current status (VARCHAR, default: 'Under Review')
- pdf_filename: Associated PDF filename (VARCHAR, optional)
- pdf_pages: Number of pages in PDF (INTEGER, optional)
- pdf_size: PDF file size in bytes (INTEGER, optional)
- created_at: Timestamp when idea was created (TIMESTAMP, auto)
- updated_at: Timestamp when idea was last updated (TIMESTAMP, auto)

Usage:
------
from models.idea import IdeaModel

# Create a new idea
idea_data = {
    'title': 'AI-Powered Analytics',
    'description': 'Advanced analytics platform...',
    'contributor': 'John Doe',
    'category': 'AI/ML',
    'impact': 'High'
}
new_idea = IdeaModel.create_idea(idea_data)

# Get all ideas
ideas = IdeaModel.get_all_ideas()

# Update PDF metadata
IdeaModel.update_pdf_info(idea_id, pdf_metadata)

Author: Innovation Team
Last Updated: 2025
"""

import logging
from datetime import datetime
from database.connection import get_db_connection

#=============================================================================
# IDEA DATA MODEL CLASS
#=============================================================================

class IdeaModel:
    """
    Data model class for managing innovation ideas in the database
    
    This class provides static methods for all database operations related
    to innovation ideas. It handles:
    
    - Creating new ideas with validation
    - Retrieving ideas with filtering and pagination
    - Updating idea metadata (especially PDF information)
    - Generating dashboard statistics and analytics
    - Loading sample/test data for development
    
    All methods include comprehensive error handling and logging.
    Database connections are managed automatically within each method.
    
    Note: All methods are static as this is a data access layer without
    instance state. Each method manages its own database connection.
    """
    
    @staticmethod
    def create_idea(idea_data):
        """Create a new idea in the database"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO ideas (title, description, abstract, contributor, category, impact, status, pdf_filename, pdf_pages, pdf_size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (
                idea_data['title'],
                idea_data['description'],
                idea_data.get('abstract', ''),
                idea_data['contributor'],
                idea_data['category'],
                idea_data['impact'],
                idea_data.get('status', 'Under Review'),
                idea_data.get('pdf_filename'),
                idea_data.get('pdf_pages'),
                idea_data.get('pdf_size')
            ))
            
            result = cur.fetchone()
            idea_id, created_at = result
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {
                "status": "success", 
                "idea_id": idea_id,
                "id": idea_id,
                "created_at": created_at,
                **idea_data
            }
            
        except Exception as e:
            logging.error(f"Error creating idea: {e}")
            raise
    
    @staticmethod
    def update_pdf_info(idea_id, pdf_info):
        """Update PDF information for an existing idea"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE ideas 
                SET pdf_filename = %s, pdf_pages = %s, pdf_size = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (
                pdf_info.get('pdf_filename'),
                pdf_info.get('pdf_pages'),
                pdf_info.get('pdf_size'),
                idea_id
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            logging.info(f"✅ Updated PDF info for idea {idea_id}")
            
        except Exception as e:
            logging.error(f"Error updating PDF info for idea {idea_id}: {e}")
            raise
    
    @staticmethod
    def get_all_ideas():
        """Get all ideas from database"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT id, title, description, abstract, contributor, category, impact, status, pdf_filename, pdf_pages, pdf_size, created_at, updated_at
                FROM ideas 
                ORDER BY created_at DESC
            """)
            
            ideas = []
            for row in cur.fetchall():
                ideas.append({
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "abstract": row[3],
                    "contributor": row[4],
                    "category": row[5],
                    "impact": row[6],
                    "status": row[7],
                    "pdf_filename": row[8],
                    "pdf_pages": row[9],
                    "pdf_size": row[10],
                    "created_at": row[11].isoformat() if row[11] else None,
                    "updated_at": row[12].isoformat() if row[12] else None
                })
            
            cur.close()
            conn.close()
            
            return ideas
            
        except Exception as e:
            logging.error(f"Error getting ideas: {e}")
            raise
    
    @staticmethod
    def get_idea_by_id(idea_id):
        """Get a specific idea by ID"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT id, title, description, abstract, contributor, category, impact, status, created_at, updated_at
                FROM ideas 
                WHERE id = %s
            """, (idea_id,))
            
            row = cur.fetchone()
            if not row:
                return None
            
            idea = {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "abstract": row[3],
                "contributor": row[4],
                "category": row[5],
                "impact": row[6],
                "status": row[7],
                "created_at": row[8].isoformat() if row[8] else None,
                "updated_at": row[9].isoformat() if row[9] else None
            }
            
            cur.close()
            conn.close()
            
            return idea
            
        except Exception as e:
            logging.error(f"Error getting idea {idea_id}: {e}")
            raise
    
    @staticmethod
    def get_dashboard_stats():
        """Get dashboard statistics"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Total ideas
            cur.execute("SELECT COUNT(*) FROM ideas")
            total_ideas = cur.fetchone()[0]
            
            # Ideas by category
            cur.execute("SELECT category, COUNT(*) FROM ideas GROUP BY category")
            category_counts = {row[0]: row[1] for row in cur.fetchall()}
            
            # Ideas by impact
            cur.execute("SELECT impact, COUNT(*) FROM ideas GROUP BY impact")
            impact_counts = {row[0]: row[1] for row in cur.fetchall()}
            
            # Ideas by status
            cur.execute("SELECT status, COUNT(*) FROM ideas GROUP BY status")
            status_counts = {row[0]: row[1] for row in cur.fetchall()}
            
            # Unique contributors
            cur.execute("SELECT COUNT(DISTINCT contributor) FROM ideas")
            unique_contributors = cur.fetchone()[0]
            
            # Recent submissions (last 7 days)
            cur.execute("SELECT COUNT(*) FROM ideas WHERE created_at >= NOW() - INTERVAL '7 days'")
            recent_submissions = cur.fetchone()[0]
            
            cur.close()
            conn.close()
            
            return {
                "total_ideas": total_ideas,
                "unique_contributors": unique_contributors,
                "recent_submissions": recent_submissions,
                "category_breakdown": category_counts,
                "impact_breakdown": impact_counts,
                "status_breakdown": status_counts
            }
            
        except Exception as e:
            logging.error(f"Error getting dashboard stats: {e}")
            raise
    
    @staticmethod
    def clear_all_ideas():
        """Clear all ideas (useful for reset)"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("DELETE FROM ideas")
            
            conn.commit()
            cur.close()
            conn.close()
            
            logging.info("✅ All ideas cleared from database")
            
        except Exception as e:
            logging.error(f"Error clearing ideas: {e}")
            raise 
    
    @staticmethod
    def update_idea_status(idea_id, new_status, admin_notes=''):
        """Update the status of an idea and optionally add admin notes"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # First, check if admin_notes column exists, if not add it
            try:
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='ideas' AND column_name='admin_notes'
                """)
                column_exists = cur.fetchone() is not None
                
                if not column_exists:
                    logging.info("Adding admin_notes column to ideas table...")
                    cur.execute("ALTER TABLE ideas ADD COLUMN admin_notes TEXT DEFAULT ''")
                    conn.commit()
                    logging.info("✅ Added admin_notes column to ideas table")
                    
            except Exception as schema_error:
                logging.warning(f"Schema check/update warning: {schema_error}")
            
            # Update the idea status and admin notes
            update_query = """
                UPDATE ideas 
                SET status = %s, 
                    admin_notes = %s,
                    updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
            """
            
            cur.execute(update_query, (new_status, admin_notes, idea_id))
            
            if cur.rowcount == 0:
                cur.close()
                conn.close()
                logging.warning(f"No idea found with ID {idea_id}")
                return False
                
            conn.commit()
            cur.close()
            conn.close()
            
            logging.info(f"✅ Idea {idea_id} status updated to '{new_status}'")
            return True
            
        except Exception as e:
            logging.error(f"Error updating idea status: {e}")
            raise
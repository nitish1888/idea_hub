"""
Red Hat Idea Hub - Contributor Data Model
=========================================

This module contains the ContributorModel class which handles all database operations
related to innovation contributors. It provides a clean interface between the application
logic and the PostgreSQL database.

Key Features:
------------
- CRUD operations for contributor profiles
- Skills and availability management
- Statistics and analytics for contributor data
- Comprehensive error handling and logging

Database Schema:
---------------
The contributors table contains the following columns:
- id: Primary key (auto-incrementing integer)
- name: Full name of the contributor (VARCHAR, required)
- manager_name: Name of contributor's manager (VARCHAR, required)
- skillset: Comma-separated list of skills/expertise (TEXT, required)
- hours_available: Available hours per week (VARCHAR, required)
- email: Contact email (VARCHAR, optional)
- department: Department/team (VARCHAR, optional)
- created_at: Timestamp when contributor registered (TIMESTAMP, auto)
- updated_at: Timestamp when profile was last updated (TIMESTAMP, auto)

Usage:
------
from models.contributor import ContributorModel

# Register a new contributor
contributor_data = {
    'name': 'John Doe',
    'manager_name': 'Jane Smith',
    'skillset': 'Python, React, AI/ML',
    'hours_available': '6-10'
}
new_contributor = ContributorModel.create_contributor(contributor_data)

# Get all contributors
contributors = ContributorModel.get_all_contributors()

Author: Red Hat Innovation Team
Last Updated: 2025
"""

import logging
from datetime import datetime
from database.connection import get_db_connection

#=============================================================================
# CONTRIBUTOR DATA MODEL CLASS
#=============================================================================

class ContributorModel:
    """
    Data model class for managing innovation contributors in the database
    
    This class provides static methods for all database operations related
    to innovation contributors. It handles:
    
    - Creating new contributor profiles with validation
    - Retrieving contributors with filtering and analytics
    - Updating contributor information
    - Generating statistics and insights
    - Skills analysis and availability tracking
    
    All methods include comprehensive error handling and logging.
    Database connections are managed automatically within each method.
    
    Note: All methods are static as this is a data access layer without
    instance state. Each method manages its own database connection.
    """
    
    @staticmethod
    def create_table_if_not_exists():
        """Create the contributors table if it doesn't exist"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS contributors (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    manager_name VARCHAR(255) NOT NULL,
                    skillset TEXT NOT NULL,
                    hours_available VARCHAR(50) NOT NULL,
                    email VARCHAR(255),
                    department VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_contributors_name ON contributors(name)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_contributors_manager ON contributors(manager_name)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_contributors_hours ON contributors(hours_available)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_contributors_created_at ON contributors(created_at)
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            
            logging.info("✅ Contributors table ensured in database")
            
        except Exception as e:
            logging.error(f"Error creating contributors table: {e}")
            raise
    
    @staticmethod
    def create_contributor(contributor_data):
        """Create a new contributor in the database"""
        try:
            # Ensure table exists
            ContributorModel.create_table_if_not_exists()
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO contributors (name, manager_name, skillset, hours_available, email, department)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (
                contributor_data['name'],
                contributor_data['manager_name'],
                contributor_data['skillset'],
                contributor_data['hours_available'],
                contributor_data.get('email'),
                contributor_data.get('department')
            ))
            
            result = cur.fetchone()
            contributor_id, created_at = result
            
            conn.commit()
            cur.close()
            conn.close()
            
            logging.info(f"✅ Created new contributor: {contributor_data['name']} (ID: {contributor_id})")
            
            return {
                "status": "success",
                "contributor_id": contributor_id,
                "id": contributor_id,
                "created_at": created_at.isoformat(),
                **contributor_data
            }
            
        except Exception as e:
            logging.error(f"Error creating contributor: {e}")
            raise
    
    @staticmethod
    def get_all_contributors():
        """Get all contributors from database"""
        try:
            # Ensure table exists
            ContributorModel.create_table_if_not_exists()
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT id, name, manager_name, skillset, hours_available, email, department, created_at, updated_at
                FROM contributors 
                ORDER BY created_at DESC
            """)
            
            contributors = []
            for row in cur.fetchall():
                contributors.append({
                    "id": row[0],
                    "name": row[1],
                    "manager": row[2],  # Keep 'manager' for frontend compatibility
                    "skillset": row[3],
                    "hours": row[4],   # Keep 'hours' for frontend compatibility
                    "email": row[5],
                    "department": row[6],
                    "registered_at": row[7].isoformat() if row[7] else None,
                    "updated_at": row[8].isoformat() if row[8] else None
                })
            
            cur.close()
            conn.close()
            
            return contributors
            
        except Exception as e:
            logging.error(f"Error getting contributors: {e}")
            raise
    
    @staticmethod
    def get_contributor_by_id(contributor_id):
        """Get a specific contributor by ID"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT id, name, manager_name, skillset, hours_available, email, department, created_at, updated_at
                FROM contributors 
                WHERE id = %s
            """, (contributor_id,))
            
            row = cur.fetchone()
            if not row:
                return None
            
            contributor = {
                "id": row[0],
                "name": row[1],
                "manager": row[2],
                "skillset": row[3],
                "hours": row[4],
                "email": row[5],
                "department": row[6],
                "registered_at": row[7].isoformat() if row[7] else None,
                "updated_at": row[8].isoformat() if row[8] else None
            }
            
            cur.close()
            conn.close()
            
            return contributor
            
        except Exception as e:
            logging.error(f"Error getting contributor {contributor_id}: {e}")
            raise
    
    @staticmethod
    def update_contributor(contributor_id, update_data):
        """Update contributor information"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Build dynamic UPDATE query based on provided fields
            set_clauses = []
            values = []
            
            if 'name' in update_data:
                set_clauses.append("name = %s")
                values.append(update_data['name'])
            
            if 'manager_name' in update_data or 'manager' in update_data:
                set_clauses.append("manager_name = %s")
                values.append(update_data.get('manager_name', update_data.get('manager')))
            
            if 'skillset' in update_data:
                set_clauses.append("skillset = %s")
                values.append(update_data['skillset'])
            
            if 'hours_available' in update_data or 'hours' in update_data:
                set_clauses.append("hours_available = %s")
                values.append(update_data.get('hours_available', update_data.get('hours')))
            
            if 'email' in update_data:
                set_clauses.append("email = %s")
                values.append(update_data['email'])
            
            if 'department' in update_data:
                set_clauses.append("department = %s")
                values.append(update_data['department'])
            
            # Always update the updated_at timestamp
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(contributor_id)
            
            if not set_clauses[:-1]:  # No fields to update except timestamp
                return None
            
            query = f"""
                UPDATE contributors 
                SET {', '.join(set_clauses)}
                WHERE id = %s
                RETURNING id, name, manager_name, skillset, hours_available, email, department, updated_at
            """
            
            cur.execute(query, values)
            result = cur.fetchone()
            
            if not result:
                return None
            
            conn.commit()
            cur.close()
            conn.close()
            
            logging.info(f"✅ Updated contributor {contributor_id}")
            
            return {
                "id": result[0],
                "name": result[1],
                "manager": result[2],
                "skillset": result[3],
                "hours": result[4],
                "email": result[5],
                "department": result[6],
                "updated_at": result[7].isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error updating contributor {contributor_id}: {e}")
            raise
    
    @staticmethod
    def delete_contributor(contributor_id):
        """Delete a contributor from the database"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("DELETE FROM contributors WHERE id = %s RETURNING name", (contributor_id,))
            result = cur.fetchone()
            
            if not result:
                return False
            
            conn.commit()
            cur.close()
            conn.close()
            
            logging.info(f"✅ Deleted contributor: {result[0]} (ID: {contributor_id})")
            return True
            
        except Exception as e:
            logging.error(f"Error deleting contributor {contributor_id}: {e}")
            raise
    
    @staticmethod
    def get_contributor_stats():
        """Get comprehensive contributor statistics"""
        try:
            # Ensure table exists
            ContributorModel.create_table_if_not_exists()
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Total contributors
            cur.execute("SELECT COUNT(*) FROM contributors")
            total_contributors = cur.fetchone()[0]
            
            # Calculate total available hours (approximate)
            cur.execute("SELECT hours_available, COUNT(*) FROM contributors GROUP BY hours_available")
            hours_data = cur.fetchall()
            
            total_hours = 0
            for hours_range, count in hours_data:
                # Convert ranges to approximate values for calculation
                if hours_range == '1-5':
                    avg_hours = 3
                elif hours_range == '6-10':
                    avg_hours = 8
                elif hours_range == '11-20':
                    avg_hours = 15
                elif hours_range == '21+':
                    avg_hours = 25
                else:
                    avg_hours = 0
                
                total_hours += avg_hours * count
            
            # Unique skills analysis
            cur.execute("SELECT skillset FROM contributors")
            all_skillsets = cur.fetchall()
            
            all_skills = []
            for skillset_row in all_skillsets:
                if skillset_row[0]:
                    skills = [skill.strip() for skill in skillset_row[0].split(',')]
                    all_skills.extend(skills)
            
            unique_skills = len(set(skill.lower() for skill in all_skills if skill))
            
            # Recent registrations (last 7 days)
            cur.execute("SELECT COUNT(*) FROM contributors WHERE created_at >= NOW() - INTERVAL '7 days'")
            recent_registrations = cur.fetchone()[0]
            
            # Hours availability breakdown
            hours_breakdown = {hours_range: count for hours_range, count in hours_data}
            
            # Top skills
            skill_counts = {}
            for skill in all_skills:
                skill_clean = skill.strip().lower()
                if skill_clean:
                    skill_counts[skill_clean] = skill_counts.get(skill_clean, 0) + 1
            
            # Get top 10 skills
            top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            cur.close()
            conn.close()
            
            return {
                "total_contributors": total_contributors,
                "total_hours_per_week": total_hours,
                "unique_skills": unique_skills,
                "recent_registrations": recent_registrations,
                "hours_breakdown": hours_breakdown,
                "top_skills": [{"skill": skill, "count": count} for skill, count in top_skills]
            }
            
        except Exception as e:
            logging.error(f"Error getting contributor stats: {e}")
            # Return empty stats if table doesn't exist or other error
            return {
                "total_contributors": 0,
                "total_hours_per_week": 0,
                "unique_skills": 0,
                "recent_registrations": 0,
                "hours_breakdown": {},
                "top_skills": []
            }
    
    @staticmethod
    def search_contributors(search_term=None, skill_filter=None, hours_filter=None):
        """Search contributors with optional filters"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Build dynamic query with filters
            where_clauses = []
            values = []
            
            if search_term:
                where_clauses.append("(LOWER(name) LIKE %s OR LOWER(manager_name) LIKE %s OR LOWER(skillset) LIKE %s)")
                search_pattern = f"%{search_term.lower()}%"
                values.extend([search_pattern, search_pattern, search_pattern])
            
            if skill_filter:
                where_clauses.append("LOWER(skillset) LIKE %s")
                values.append(f"%{skill_filter.lower()}%")
            
            if hours_filter:
                where_clauses.append("hours_available = %s")
                values.append(hours_filter)
            
            where_clause = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            query = f"""
                SELECT id, name, manager_name, skillset, hours_available, email, department, created_at, updated_at
                FROM contributors 
                {where_clause}
                ORDER BY created_at DESC
            """
            
            cur.execute(query, values)
            
            contributors = []
            for row in cur.fetchall():
                contributors.append({
                    "id": row[0],
                    "name": row[1],
                    "manager": row[2],
                    "skillset": row[3],
                    "hours": row[4],
                    "email": row[5],
                    "department": row[6],
                    "registered_at": row[7].isoformat() if row[7] else None,
                    "updated_at": row[8].isoformat() if row[8] else None
                })
            
            cur.close()
            conn.close()
            
            return contributors
            
        except Exception as e:
            logging.error(f"Error searching contributors: {e}")
            raise
    
    @staticmethod
    def clear_all_contributors():
        """Clear all contributors (useful for reset/testing)"""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("DELETE FROM contributors")
            
            conn.commit()
            cur.close()
            conn.close()
            
            logging.info("✅ All contributors cleared from database")
            
        except Exception as e:
            logging.error(f"Error clearing contributors: {e}")
            raise

#=============================================================================
# END OF CONTRIBUTOR DATA MODEL MODULE
#=============================================================================
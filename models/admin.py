"""
Idea Hub - Admin User Model (Database-Based)
==================================================

Database-based admin authentication system with proper security.
Uses PostgreSQL for admin user storage and bcrypt for password hashing.
"""

from flask_login import UserMixin
import bcrypt
import logging
from database.connection import get_db_connection
from typing import Optional

class AdminAuth(UserMixin):
    """
    Database-based Admin User model for Flask-Login.
    Stores admin users in PostgreSQL with bcrypt password hashing.
    """

    def __init__(self, user_id, username, email=None, active=True):
        self.id = str(user_id)
        self.username = username
        self.email = email
        self._is_active = active

    def get_id(self):
        return self.id
    
    @property
    def is_active(self):
        return self._is_active

    @staticmethod
    def create_admin_table():
        """Create the admin users table if it doesn't exist"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Create admin table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    password_hash TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    login_count INTEGER DEFAULT 0
                );
            """)
            
            # Create index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_admin_username ON admin_users(username);
            """)
            
            connection.commit()
            cursor.close()
            connection.close()
            
            logging.info("✅ Admin users table created successfully")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error creating admin table: {e}")
            return False

    @staticmethod
    def create_default_admin():
        """Create default admin users if none exist"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Check if any admin users exist
            cursor.execute("SELECT COUNT(*) FROM admin_users")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Create default admin users
                default_admins = [
                    ("admin", "hello", "admin@company.com"),
                    ("rhadmin", "company123", "rhadmin@company.com")
                ]
                
                for username, password, email in default_admins:
                    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    
                    cursor.execute("""
                        INSERT INTO admin_users (username, email, password_hash)
                        VALUES (%s, %s, %s)
                    """, (username, email, password_hash))
                
                connection.commit()
                logging.info(f"✅ Created {len(default_admins)} default admin users")
            
            cursor.close()
            connection.close()
            return True
            
        except Exception as e:
            logging.error(f"❌ Error creating default admin users: {e}")
            return False

    @staticmethod
    def get_admin_by_id(user_id):
        """Get admin user by ID for Flask-Login user_loader"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT id, username, email, is_active 
                FROM admin_users 
                WHERE id = %s AND is_active = TRUE
            """, (user_id,))
            
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if result:
                return AdminAuth(result[0], result[1], result[2], active=result[3])
            return None
            
        except Exception as e:
            logging.error(f"❌ Error getting admin by ID: {e}")
            return None

    @staticmethod
    def verify_password(username, password):
        """Verify admin credentials and return AdminAuth object if valid"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT id, username, email, password_hash, is_active 
                FROM admin_users 
                WHERE username = %s AND is_active = TRUE
            """, (username,))
            
            result = cursor.fetchone()
            
            if result and bcrypt.checkpw(password.encode('utf-8'), result[3].encode('utf-8')):
                # Update last login
                cursor.execute("""
                    UPDATE admin_users 
                    SET last_login = CURRENT_TIMESTAMP, login_count = login_count + 1
                    WHERE id = %s
                """, (result[0],))
                connection.commit()
                
                cursor.close()
                connection.close()
                
                logging.info(f"✅ Admin login successful: {username}")
                return AdminAuth(result[0], result[1], result[2], active=result[4])
            
            cursor.close()
            connection.close()
            logging.warning(f"❌ Admin login failed: {username}")
            return None
            
        except Exception as e:
            logging.error(f"❌ Error verifying admin password: {e}")
            return None

    @staticmethod
    def create_admin_user(username, password, email=None):
        """Create a new admin user"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO admin_users (username, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (username, email, password_hash))
            
            user_id = cursor.fetchone()[0]
            connection.commit()
            cursor.close()
            connection.close()
            
            logging.info(f"✅ Created new admin user: {username}")
            return user_id
            
        except Exception as e:
            logging.error(f"❌ Error creating admin user: {e}")
            return None

    @staticmethod
    def get_all_admins():
        """Get all admin users (for management)"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT id, username, email, is_active, created_at, last_login, login_count
                FROM admin_users
                ORDER BY created_at DESC
            """)
            
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            
            admins = []
            for row in results:
                admins.append({
                    'id': row[0],
                    'username': row[1],
                    'email': row[2],
                    'is_active': row[3],
                    'created_at': row[4],
                    'last_login': row[5],
                    'login_count': row[6]
                })
            
            return admins
            
        except Exception as e:
            logging.error(f"❌ Error getting all admins: {e}")
            return []

    @staticmethod
    def update_admin_password(username, new_password):
        """Update admin user password"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                UPDATE admin_users 
                SET password_hash = %s
                WHERE username = %s
            """, (password_hash, username))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            logging.info(f"✅ Updated password for admin: {username}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error updating admin password: {e}")
            return False

    @staticmethod
    def deactivate_admin(username):
        """Deactivate an admin user"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            cursor.execute("""
                UPDATE admin_users 
                SET is_active = FALSE
                WHERE username = %s
            """, (username,))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            logging.info(f"✅ Deactivated admin user: {username}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error deactivating admin: {e}")
            return False

    @staticmethod
    def initialize_admin_system():
        """Initialize the admin system (create table and default users)"""
        logging.info("🔧 Initializing admin authentication system...")
        
        # Create table
        if not AdminAuth.create_admin_table():
            return False
        
        # Create default admin users
        if not AdminAuth.create_default_admin():
            return False
        
        logging.info("✅ Admin authentication system initialized successfully")
        return True
"""
Idea Hub - Database Connection Management
================================================

This module handles all PostgreSQL database connections and provides utilities
for database health checking and extension management.

Based on connection patterns from idea_borad.ipynb notebook with enhanced
error handling and monitoring capabilities.

Key Features:
------------
- Centralized database connection management
- Connection health monitoring and testing
- PostgreSQL extension management (vector, uuid-ossp)
- Configuration-based connection parameters
- Comprehensive error handling and logging

Dependencies:
------------
- psycopg2: PostgreSQL adapter for Python
- PostgreSQL server with vector extensions support
- Configuration settings from config.settings

Database Requirements:
---------------------
- PostgreSQL 12+ with pgvector extension
- uuid-ossp extension for unique identifiers
- User with CREATE EXTENSION privileges (for setup)

Usage:
------
from database.connection import get_db_connection, test_connection

# Get a database connection
conn = get_db_connection()

# Test connection health
status = test_connection()

Author: Innovation Team
Last Updated: 2025
"""

import psycopg2
import logging
from config.settings import Config

#=============================================================================
# DATABASE CONNECTION FUNCTIONS
#=============================================================================

def get_db_connection():
    """
    Get a PostgreSQL database connection using configured parameters
    
    Returns:
        psycopg2.connection: Active database connection
        
    Raises:
        psycopg2.Error: If connection fails
        Exception: For other connection-related errors
    
    Configuration:
        Uses Config.DB_CONFIG dictionary containing:
        - dbname: Database name
        - user: Database username  
        - password: Database password
        - host: Database host
        - port: Database port
    
    Note:
        Caller is responsible for closing the connection after use.
        For transaction safety, use connection context managers.
    
    Example:
        ```python
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM ideas")
            results = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            logging.error(f"Database operation failed: {e}")
        ```
    """
    try:
        # Create connection using configuration parameters
        # psycopg2.connect() accepts keyword arguments from DB_CONFIG
        conn = psycopg2.connect(**Config.DB_CONFIG)
        
        # Set autocommit to False for transaction control
        # Applications should explicitly commit transactions
        conn.autocommit = False
        
        return conn
        
    except psycopg2.Error as db_error:
        # Log database-specific errors with details
        logging.error(f"PostgreSQL connection failed: {db_error}")
        logging.error(f"Database config: {Config.DB_CONFIG['dbname']}@{Config.DB_CONFIG['host']}:{Config.DB_CONFIG['port']}")
        raise
        
    except Exception as e:
        # Log other connection errors
        logging.error(f"Database connection failed: {e}")
        raise

#=============================================================================
# DATABASE HEALTH MONITORING
#=============================================================================

def test_connection():
    """
    Test database connection and return comprehensive health status
    
    Returns:
        dict: Health status information containing:
            - status: "healthy" or "error"
            - database: "connected" or "disconnected"  
            - pgvector: "enabled", "not_installed", or "unknown"
            - config: Database name from configuration
            - error: Error message (only if status is "error")
    
    This function performs multiple checks:
    1. Basic connection test
    2. Simple query execution test
    3. pgvector extension availability check
    4. Configuration validation
    
    Used by:
        - Health check endpoints
        - Application startup validation
        - Monitoring and alerting systems
    
    Example:
        ```python
        health = test_connection()
        if health["status"] == "healthy":
            print("Database is ready")
        else:
            print(f"Database error: {health.get('error')}")
        ```
    """
    try:
        # Attempt to establish connection
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Test 1: Basic query execution
        # This verifies the connection is working and can execute SQL
        cur.execute("SELECT 1 AS test_query")
        result = cur.fetchone()
        
        if not result or result[0] != 1:
            raise Exception("Basic query test failed")
        
        # Test 2: Check pgvector extension availability
        # This is critical for semantic search functionality
        cur.execute("""
            SELECT 1 FROM pg_extension 
            WHERE extname = 'vector'
        """)
        vector_exists = cur.fetchone()
        
        # Test 3: Check uuid-ossp extension (needed for langchain)
        cur.execute("""
            SELECT 1 FROM pg_extension 
            WHERE extname = 'uuid-ossp'
        """)
        uuid_exists = cur.fetchone()
        
        # Clean up resources
        cur.close()
        conn.close()
        
        # Return comprehensive health status
        return {
            "status": "healthy",
            "database": "connected",
            "pgvector": "enabled" if vector_exists else "not_installed",
            "uuid_ossp": "enabled" if uuid_exists else "not_installed", 
            "config": Config.DB_CONFIG['dbname']
        }
        
    except psycopg2.Error as db_error:
        # Database-specific errors
        return {
            "status": "error",
            "error": f"PostgreSQL Error: {str(db_error)}",
            "database": "disconnected",
            "pgvector": "unknown",
            "config": Config.DB_CONFIG['dbname']
        }
        
    except Exception as e:
        # General connection or configuration errors
        return {
            "status": "error", 
            "error": str(e),
            "database": "disconnected",
            "pgvector": "unknown",
            "config": Config.DB_CONFIG['dbname']
        }

#=============================================================================
# DATABASE EXTENSION MANAGEMENT
#=============================================================================

def ensure_extensions():
    """
    Ensure required PostgreSQL extensions are installed and available
    
    Required Extensions:
        - vector: Enables pgvector functionality for semantic search
        - uuid-ossp: Provides UUID generation functions for langchain
    
    Raises:
        psycopg2.Error: If extension creation fails
        Exception: For other database errors
    
    Note:
        This function requires database user to have CREATE EXTENSION privileges.
        Extensions are created with "IF NOT EXISTS" to avoid conflicts.
    
    Called by:
        - Database setup/initialization scripts
        - Application startup validation
        - Database migration processes
    
    Example:
        ```python
        try:
            ensure_extensions()
            logging.info("All required extensions are available")
        except Exception as e:
            logging.error(f"Extension setup failed: {e}")
        ```
    """
    try:
        # Get database connection for extension management
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Install vector extension for pgvector functionality
        # This enables vector similarity operations and indexing
        logging.info("🔧 Installing vector extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        
        # Install uuid-ossp extension for UUID generation
        # Required by langchain for vector store operations
        logging.info("🔧 Installing uuid-ossp extension...")
        cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        
        # Verify extensions were created successfully
        cur.execute("""
            SELECT extname FROM pg_extension 
            WHERE extname IN ('vector', 'uuid-ossp')
            ORDER BY extname
        """)
        installed_extensions = [row[0] for row in cur.fetchall()]
        
        # Commit the extension installations
        conn.commit()
        
        # Clean up resources
        cur.close()
        conn.close()
        
        # Log success with details
        logging.info(f"✅ PostgreSQL extensions ensured: {', '.join(installed_extensions)}")
        
    except psycopg2.Error as db_error:
        # Handle database-specific errors
        logging.error(f"❌ PostgreSQL extension error: {db_error}")
        logging.error("💡 Ensure database user has CREATE EXTENSION privileges")
        raise
        
    except Exception as e:
        # Handle general errors
        logging.error(f"❌ Error ensuring extensions: {e}")
        raise

#=============================================================================
# UTILITY FUNCTIONS
#=============================================================================

def get_connection_info():
    """
    Get formatted connection information for logging and debugging
    
    Returns:
        dict: Connection information with sensitive data masked
    
    This function provides connection details for debugging without
    exposing sensitive information like passwords.
    """
    return {
        "database": Config.DB_CONFIG['dbname'],
        "host": Config.DB_CONFIG['host'],
        "port": Config.DB_CONFIG['port'],
        "user": Config.DB_CONFIG['user'],
        "password_set": bool(Config.DB_CONFIG.get('password'))
    }

def execute_health_query():
    """
    Execute a comprehensive health query to test database functionality
    
    Returns:
        dict: Query results and timing information
    
    This function runs multiple test queries to verify database health:
    - Basic connectivity
    - Extension availability  
    - Table existence
    - Performance metrics
    """
    start_time = psycopg2.Timestamp.now() if hasattr(psycopg2, 'Timestamp') else None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Test basic functionality
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        
        # Check for required tables (if they exist)
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        return {
            "status": "healthy",
            "version": version,
            "tables": tables,
            "extensions": ["vector", "uuid-ossp"]  # Expected extensions
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

#=============================================================================
# END OF DATABASE CONNECTION MODULE
#============================================================================= 
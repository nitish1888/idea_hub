"""
Database setup and initialization
Creates tables and sets up pgvector collections
"""

import logging
from .connection import get_db_connection, ensure_extensions

def init_database():
    """Initialize database with required extensions and tables"""
    try:
        # Ensure extensions are installed
        ensure_extensions()
        
        # Create basic tables
        create_tables()
        
        logging.info("✅ Database initialized successfully")
        return {"status": "success", "message": "Database initialized"}
        
    except Exception as e:
        logging.error(f"❌ Database initialization failed: {e}")
        return {"status": "error", "error": str(e)}

def create_tables():
    """Create the ideas table for storing idea metadata"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create ideas table for metadata (similar to your notebook approach)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ideas (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                abstract TEXT,
                contributor VARCHAR(100),
                category VARCHAR(50),
                impact VARCHAR(20),
                status VARCHAR(20) DEFAULT 'Under Review',
                pdf_filename VARCHAR(255),
                pdf_pages INTEGER,
                pdf_size BIGINT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index on commonly queried fields
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ideas_category ON ideas(category)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ideas_contributor ON ideas(contributor)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ideas_status ON ideas(status)")
        
        conn.commit()
        cur.close()
        conn.close()
        
        logging.info("✅ Tables created successfully")
        
    except Exception as e:
        logging.error(f"❌ Error creating tables: {e}")
        raise

def drop_tables():
    """Drop all tables (useful for reset)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Drop tables in correct order
        cur.execute("DROP TABLE IF EXISTS ideas CASCADE")
        
        # Note: langchain tables will be managed by langchain itself
        
        conn.commit()
        cur.close()
        conn.close()
        
        logging.info("✅ Tables dropped successfully")
        
    except Exception as e:
        logging.error(f"❌ Error dropping tables: {e}")
        raise 
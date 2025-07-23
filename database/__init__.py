"""
Database module for Red Hat Idea Hub
"""

from .connection import get_db_connection, test_connection
from .setup import init_database, create_tables

__all__ = ['get_db_connection', 'test_connection', 'init_database', 'create_tables'] 
"""
Centralized database initialization module
This module provides a single entry point for all database operations
"""

from database_manager import db_manager
from app import create_app
import os
import sys


def init_database(app=None, use_migrations=True):
    """
    Initialize the database with proper configuration
    
    Args:
        app: Flask app instance (if None, creates a new one)
        use_migrations: Whether to use migrations (True) or create_all (False)
    """
    if app is None:
        app = create_app()
    
    with app.app_context():
        if use_migrations:
            # In production, use migrations exclusively
            print("Using database migrations for initialization...")
        else:
            # For development/testing, can use create_all
            print("Creating all database tables...")
            db_manager.create_tables(app)
    
    return app


def run_migrations():
    """
    Run database migrations using Alembic
    """
    import subprocess
    try:
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                              capture_output=True, text=True, check=True)
        print("Migrations completed successfully")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Migrations failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Alembic not found. Please ensure it's installed.")
        return False
    
    return True


def init_db_with_migrations():
    """
    Initialize database using migrations
    """
    app = create_app()
    
    # Run migrations first
    success = run_migrations()
    if not success:
        print("Failed to run migrations. Falling back to create_all...")
        db_manager.create_tables(app)
    
    return app


def create_test_db():
    """
    Create a test database with test data
    """
    # Create app with test configuration
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # Initialize with create_all for tests
    db_manager.init_app(app)
    db_manager.create_tables(app)
    
    return app


if __name__ == "__main__":
    # Allow command-line usage for database operations
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "migrate":
            run_migrations()
        elif command == "init":
            init_db_with_migrations()
        elif command == "create_test":
            create_test_db()
            print("Test database created")
        else:
            print(f"Unknown command: {command}")
            print("Available commands: migrate, init, create_test")
    else:
        print("Usage: python db_init.py [migrate|init|create_test]")
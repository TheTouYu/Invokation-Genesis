"""
Configuration for testing environment
"""
import os
from database_manager import db_manager


class TestConfig:
    """Configuration class for tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing


def create_test_app():
    """Create a Flask app configured for testing"""
    from app import create_app
    
    app = create_app()
    app.config.from_object(TestConfig)
    
    # Initialize database for test
    db_manager.init_app(app)
    
    return app
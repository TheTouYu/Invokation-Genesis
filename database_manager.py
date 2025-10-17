"""
Database management module for centralized database operations
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os


class DatabaseManager:
    """
    A centralized database manager to handle database operations
    """
    
    def __init__(self):
        self.db = SQLAlchemy()
        self.migrate = Migrate()
    
    def init_app(self, app):
        """
        Initialize the database with the Flask app
        """
        # Configure the database URI based on environment
        if app.config.get('TESTING'):
            # Use in-memory database for tests
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        elif os.environ.get('DATABASE_URL'):
            # Use environment variable if set
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
        else:
            # Default to instance directory
            db_path = os.path.join(app.instance_path, 'game.db')
            os.makedirs(app.instance_path, exist_ok=True)
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        
        # Initialize extensions
        self.db.init_app(app)
        self.migrate.init_app(app, self.db)
        
        return self.db
    
    def create_tables(self, app):
        """
        Create all database tables - only for non-production environments
        This is for backward compatibility and development purposes.
        In production, always use migrations.
        """
        if app.config.get('ENV') != 'production':
            with app.app_context():
                from models.db_models import init_models_db
                init_models_db(self.db)
                # For development/testing, we can use create_all
                # In production, migrations should be used exclusively
                self.db.create_all()
    
    def get_db(self):
        """
        Get the database instance
        """
        return self.db


# Global instance
db_manager = DatabaseManager()
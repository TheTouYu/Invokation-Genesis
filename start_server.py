"""
Script to start the Genshin Impact Card Game server with deck builder functionality
"""
import os
import sys
from app import create_app
from flask_socketio import SocketIO

def main():
    # Create the Flask app
    app = create_app()
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    print("Starting Genshin Impact Card Game server...")
    print("Available endpoints:")
    print("  - http://localhost:5000/health - Health check")
    print("  - http://localhost:5000/deck-builder - Deck builder interface")
    print("  - http://localhost:5000/api/test - API test page")
    print("\nTo access the deck builder, visit: http://localhost:5000/deck-builder")
    
    # Initialize database tables
    with app.app_context():
        from models.db_models import db
        db.create_all()
    
    # Run the server
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=False,
        allow_unsafe_werkzeug=True  # Needed for SocketIO in development
    )

if __name__ == "__main__":
    main()
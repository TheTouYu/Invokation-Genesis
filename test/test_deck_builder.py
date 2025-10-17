#!/usr/bin/env python3
"""
Test script to verify the deck builder functionality works correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from api.deck_builder.api_routes import validate_deck_api
from utils.deck_validator import validate_deck_composition
from models.db_models import db, CardData

def test_deck_builder():
    print("Testing deck builder functionality...")
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        print("✓ App context created successfully")
        
        # Test if routes exist
        deck_builder_route = None
        validate_route = None
        for rule in app.url_map.iter_rules():
            if str(rule) == '/deck-builder':
                deck_builder_route = rule
            elif str(rule) == '/api/deck/validate':
                validate_route = rule
        
        if deck_builder_route:
            print(f"✓ Deck builder route exists: {deck_builder_route.rule}")
        else:
            print("✗ Deck builder route not found")
            
        if validate_route:
            print(f"✓ Validation route exists: {validate_route.rule}")
        else:
            print("✗ Validation route not found")
        
        # Test validation function
        try:
            test_deck_data = {
                "characters": [],
                "cards": [],
                "deck_name": "Test Deck"
            }
            
            result = validate_deck_composition(test_deck_data)
            print(f"✓ Validation function works, result keys: {list(result.keys())}")
            print(f"  Is valid by default: {result.get('is_valid', 'unknown')}")
        except Exception as e:
            print(f"✗ Validation function failed: {e}")
    
    print("\nDeck builder functionality test completed!")

if __name__ == "__main__":
    test_deck_builder()
"""
Data Access Layer (DAL) for the Genshin Impact card game
This module provides a centralized interface for all database operations
"""

from typing import List, Optional, Dict, Any
from database_manager import db_manager
from models.db_models import User, CardData, Deck, GameHistory
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc
import logging


class UserDAL:
    """Data Access Layer for User operations"""
    
    @staticmethod
    def create_user(username: str, email: str, password_hash: str) -> User:
        """Create a new user"""
        try:
            user = User(
                username=username,
                email=email,
                password_hash=password_hash
            )
            db_manager.db.session.add(user)
            db_manager.db.session.commit()
            return user
        except SQLAlchemyError as e:
            db_manager.db.session.rollback()
            logging.error(f"Error creating user: {e}")
            raise
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            return User.query.filter_by(id=user_id).first()
        except SQLAlchemyError as e:
            logging.error(f"Error getting user by ID: {e}")
            return None
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username"""
        try:
            return User.query.filter_by(username=username).first()
        except SQLAlchemyError as e:
            logging.error(f"Error getting user by username: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return User.query.filter_by(email=email).first()
        except SQLAlchemyError as e:
            logging.error(f"Error getting user by email: {e}")
            return None
    
    @staticmethod
    def update_user(user_id: str, **kwargs) -> bool:
        """Update user fields"""
        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return False
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            db_manager.db.session.commit()
            return True
        except SQLAlchemyError as e:
            db_manager.db.session.rollback()
            logging.error(f"Error updating user: {e}")
            return False
    
    @staticmethod
    def delete_user(user_id: str) -> bool:
        """Delete user"""
        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return False
            
            db_manager.db.session.delete(user)
            db_manager.db.session.commit()
            return True
        except SQLAlchemyError as e:
            db_manager.db.session.rollback()
            logging.error(f"Error deleting user: {e}")
            return False


class CardDataDAL:
    """Data Access Layer for CardData operations"""
    
    @staticmethod
    def create_card(**kwargs) -> CardData:
        """Create a new card"""
        try:
            card = CardData(**kwargs)
            db_manager.db.session.add(card)
            db_manager.db.session.commit()
            return card
        except SQLAlchemyError as e:
            db_manager.db.session.rollback()
            logging.error(f"Error creating card: {e}")
            raise
    
    @staticmethod
    def get_card_by_id(card_id: str) -> Optional[CardData]:
        """Get card by ID"""
        try:
            return CardData.query.filter_by(id=card_id).first()
        except SQLAlchemyError as e:
            logging.error(f"Error getting card by ID: {e}")
            return None
    
    @staticmethod
    def get_cards_by_type(card_type: str, limit: Optional[int] = None) -> List[CardData]:
        """Get cards by type"""
        try:
            query = CardData.query.filter_by(card_type=card_type)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            logging.error(f"Error getting cards by type: {e}")
            return []
    
    @staticmethod
    def get_cards_by_rarity(rarity: int) -> List[CardData]:
        """Get cards by rarity"""
        try:
            return CardData.query.filter_by(rarity=rarity).all()
        except SQLAlchemyError as e:
            logging.error(f"Error getting cards by rarity: {e}")
            return []
    
    @staticmethod
    def search_cards(query_str: str) -> List[CardData]:
        """Search cards by name or description"""
        try:
            search = f"%{query_str}%"
            return CardData.query.filter(
                or_(
                    CardData.name.ilike(search),
                    CardData.description.ilike(search)
                )
            ).all()
        except SQLAlchemyError as e:
            logging.error(f"Error searching cards: {e}")
            return []
    
    @staticmethod
    def update_card(card_id: str, **kwargs) -> bool:
        """Update card fields"""
        try:
            card = CardData.query.filter_by(id=card_id).first()
            if not card:
                return False
            
            for key, value in kwargs.items():
                if hasattr(card, key):
                    setattr(card, key, value)
            
            db_manager.db.session.commit()
            return True
        except SQLAlchemyError as e:
            db_manager.db.session.rollback()
            logging.error(f"Error updating card: {e}")
            return False


class DeckDAL:
    """Data Access Layer for Deck operations"""
    
    @staticmethod
    def create_deck(name: str, user_id: str, cards: List[str], description: str = "", is_public: bool = False) -> Deck:
        """Create a new deck"""
        try:
            deck = Deck(
                name=name,
                user_id=user_id,
                card_ids=cards,
                description=description,
                is_public=is_public
            )
            db_manager.db.session.add(deck)
            db_manager.db.session.commit()
            return deck
        except SQLAlchemyError as e:
            db_manager.db.session.rollback()
            logging.error(f"Error creating deck: {e}")
            raise
    
    @staticmethod
    def get_deck_by_id(deck_id: str) -> Optional[Deck]:
        """Get deck by ID"""
        try:
            return Deck.query.filter_by(id=deck_id).first()
        except SQLAlchemyError as e:
            logging.error(f"Error getting deck by ID: {e}")
            return None
    
    @staticmethod
    def get_decks_by_user(user_id: str) -> List[Deck]:
        """Get all decks for a user"""
        try:
            return Deck.query.filter_by(user_id=user_id).all()
        except SQLAlchemyError as e:
            logging.error(f"Error getting decks by user: {e}")
            return []
    
    @staticmethod
    def get_public_decks(limit: Optional[int] = None) -> List[Deck]:
        """Get all public decks"""
        try:
            query = Deck.query.filter_by(is_public=True)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            logging.error(f"Error getting public decks: {e}")
            return []
    
    @staticmethod
    def update_deck(deck_id: str, **kwargs) -> bool:
        """Update deck fields"""
        try:
            deck = Deck.query.filter_by(id=deck_id).first()
            if not deck:
                return False
            
            for key, value in kwargs.items():
                if hasattr(deck, key):
                    setattr(deck, key, value)
            
            db_manager.db.session.commit()
            return True
        except SQLAlchemyError as e:
            db_manager.db.session.rollback()
            logging.error(f"Error updating deck: {e}")
            return False
    
    @staticmethod
    def delete_deck(deck_id: str) -> bool:
        """Delete deck"""
        try:
            deck = Deck.query.filter_by(id=deck_id).first()
            if not deck:
                return False
            
            db_manager.db.session.delete(deck)
            db_manager.db.session.commit()
            return True
        except SQLAlchemyError as e:
            db_manager.db.session.rollback()
            logging.error(f"Error deleting deck: {e}")
            return False


class GameHistoryDAL:
    """Data Access Layer for GameHistory operations"""
    
    @staticmethod
    def create_game_history(
        player1_id: str, 
        player2_id: str, 
        game_data: Dict[str, Any], 
        winner_id: Optional[str] = None,
        deck1_id: Optional[str] = None,
        deck2_id: Optional[str] = None,
        game_result: Optional[str] = None,
        duration: Optional[int] = None
    ) -> GameHistory:
        """Create a new game history record"""
        try:
            game_history = GameHistory(
                player1_id=player1_id,
                player2_id=player2_id,
                winner_id=winner_id,
                deck1_id=deck1_id,
                deck2_id=deck2_id,
                game_data=game_data,
                game_result=game_result,
                duration=duration
            )
            db_manager.db.session.add(game_history)
            db_manager.db.session.commit()
            return game_history
        except SQLAlchemyError as e:
            db_manager.db.session.rollback()
            logging.error(f"Error creating game history: {e}")
            raise
    
    @staticmethod
    def get_game_history_by_id(game_id: str) -> Optional[GameHistory]:
        """Get game history by ID"""
        try:
            return GameHistory.query.filter_by(id=game_id).first()
        except SQLAlchemyError as e:
            logging.error(f"Error getting game history by ID: {e}")
            return None
    
    @staticmethod
    def get_games_by_user(user_id: str) -> List[GameHistory]:
        """Get games where user participated (either as player1 or player2)"""
        try:
            return GameHistory.query.filter(
                or_(GameHistory.player1_id == user_id, GameHistory.player2_id == user_id)
            ).order_by(desc(GameHistory.created_at)).all()
        except SQLAlchemyError as e:
            logging.error(f"Error getting games by user: {e}")
            return []
    
    @staticmethod
    def get_games_by_winner(winner_id: str) -> List[GameHistory]:
        """Get games won by a specific user"""
        try:
            return GameHistory.query.filter_by(winner_id=winner_id).order_by(desc(GameHistory.created_at)).all()
        except SQLAlchemyError as e:
            logging.error(f"Error getting games by winner: {e}")
            return []
    
    @staticmethod
    def get_recent_games(limit: int = 10) -> List[GameHistory]:
        """Get recent games"""
        try:
            return GameHistory.query.order_by(desc(GameHistory.created_at)).limit(limit).all()
        except SQLAlchemyError as e:
            logging.error(f"Error getting recent games: {e}")
            return []


class DatabaseDAL:
    """Main Database DAL class that encompasses all specific DALs"""
    
    def __init__(self):
        self.users = UserDAL()
        self.cards = CardDataDAL()
        self.decks = DeckDAL()
        self.game_history = GameHistoryDAL()
    
    @staticmethod
    def init_db():
        """Initialize database tables"""
        # This would typically call the db_manager's create_tables function
        pass
    
    @staticmethod
    def get_session():
        """Get the database session"""
        return db_manager.db.session


# Global instance
db_dal = DatabaseDAL()
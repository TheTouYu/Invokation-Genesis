"""
Script to add test accounts with usernames test0 through test9 and password 'test'
"""

import os
from app import create_app
from database_manager import db_manager
from models.db_models import model_container
from werkzeug.security import generate_password_hash


def create_test_accounts():
    """创建测试账号"""
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Get database instance from the database manager
        db = db_manager.get_db()
        
        # Get the User model from the model container
        User = model_container.User
        
        # Create test accounts
        for i in range(10):
            username = f"test{i}"
            password = "test"
            email = f"test{i}@example.com"
            
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"用户 {username} 已存在，跳过创建")
                continue
            
            # Create new user
            hashed_password = generate_password_hash(password)
            
            user = User(
                username=username,
                email=email,
                password_hash=hashed_password
            )
            
            db.session.add(user)
            print(f"已创建用户: {username}，密码: {password}")
        
        # Commit all changes
        db.session.commit()
        print("所有测试账号创建完成！")


if __name__ == "__main__":
    create_test_accounts()
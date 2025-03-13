"""
Script to create a test user in the database.
Run this script to ensure there's a valid user for testing login.
"""
import sys
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User
from app.auth.utils import get_password_hash

def create_test_user():
    """Create a test user in the database."""
    db = SessionLocal()
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print("Test user already exists.")
            return
        
        # Create test user
        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            full_name="Test User",
            operation_name="Test Operation",
            operation_type="daycare",
            state="Texas",
            phone_number="555-123-4567",
            is_active=True
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"Test user created with ID: {test_user.id}")
        print("Email: test@example.com")
        print("Password: password123")
    except Exception as e:
        print(f"Error creating test user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user() 
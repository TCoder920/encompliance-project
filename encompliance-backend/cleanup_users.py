import os
import sys
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.user_settings import UserSettings
from app.database import Base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def cleanup_users(confirm=False, admin_only=True):
    """
    Remove all users from the database.
    
    Args:
        confirm: If True, proceed without confirmation
        admin_only: If True, keep admin users
    """
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Connect to database
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Count users to be deleted
        if admin_only:
            # Define your admin users by their usernames or emails
            admin_users = ["admin@encompliance.io"]
            count = db.query(User).filter(~User.email.in_(admin_users)).count()
            print(f"Found {count} non-admin users to delete")
        else:
            count = db.query(User).count()
            print(f"Found {count} users to delete")
        
        # Confirm deletion
        if not confirm:
            response = input("Are you sure you want to delete these users? (y/n): ")
            if response.lower() != "y":
                print("Operation cancelled")
                return
        
        # Delete users
        if admin_only:
            admin_users = ["admin@encompliance.io"]
            users = db.query(User).filter(~User.email.in_(admin_users)).all()
        else:
            users = db.query(User).all()
        
        # Delete associated user settings first
        for user in users:
            # Delete settings (will be cascade deleted, but explicitly doing it for clarity)
            settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
            if settings:
                db.delete(settings)
            
            # Delete user
            db.delete(user)
            
        # Commit changes
        db.commit()
        print(f"Successfully deleted {len(users)} users")
    
    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up users from the database")
    parser.add_argument("--confirm", action="store_true", help="Proceed without confirmation")
    parser.add_argument("--all", action="store_true", help="Delete all users, including admins")
    args = parser.parse_args()
    
    cleanup_users(confirm=args.confirm, admin_only=not args.all) 
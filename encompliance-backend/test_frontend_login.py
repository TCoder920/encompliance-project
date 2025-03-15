import requests
import json

# Server URL
BASE_URL = "http://localhost:8000/api/v1"

def test_frontend_login():
    """Test the login in a way that replicates how the frontend makes the request"""
    print("Testing login with the same approach as the frontend...")

    # Test with our known working user
    test_working_user = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    # Test with the user that was being used in the frontend (which might not exist)
    test_frontend_user = {
        "email": "testuser5@gmail.com",
        "password": "password123"  # assuming this password
    }
    
    # Try login with working user
    print("\n=== Testing with working test user ===")
    try_login(test_working_user)
    
    # Try login with frontend user
    print("\n=== Testing with frontend user (might not exist) ===")
    try_login(test_frontend_user)
    
    # Create frontend user if needed
    print("\n=== Creating the frontend user for future use ===")
    create_frontend_user()
    
    # Try login with frontend user again
    print("\n=== Testing with frontend user again (after creation) ===")
    try_login(test_frontend_user)

def try_login(credentials):
    """Attempt to login with the given credentials"""
    try:
        # Make the login request
        response = requests.post(
            f"{BASE_URL}/email-login", 
            json=credentials,
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:5173",  # Same origin as frontend
                "Referer": "http://localhost:5173/"
            }
        )
        
        # Print the response
        print(f"Response Status Code: {response.status_code}")
        
        # Try to parse the response body
        try:
            response_body = response.json()
            print(f"Response Body: {json.dumps(response_body, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response Text (not JSON): {response.text}")
        
        # Check if login was successful
        if response.status_code == 200 and "access_token" in response.json():
            print("Login successful!")
            return True
        else:
            print("Login failed!")
            return False
            
    except Exception as e:
        print(f"Error during login test: {e}")
        return False

def create_frontend_user():
    """Create the user that the frontend is trying to login with"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.user import User
    from app.core.config import get_settings
    from passlib.context import CryptContext
    
    settings = get_settings()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Create DB session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if user already exists
        test_email = "testuser5@gmail.com"
        test_user = db.query(User).filter(User.email == test_email).first()
        
        if test_user:
            print(f"User {test_email} already exists, no need to create")
            return test_user
        
        # Create the test user with valid fields only
        print(f"Creating user: {test_email}")
        test_user = User(
            email=test_email,
            username="testuser5",
            hashed_password=pwd_context.hash("password123"),
            full_name="Test User 5",
            operation_name="Test Operation",
            is_active=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"User {test_email} created successfully")
        
        return test_user
    
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    test_frontend_login() 
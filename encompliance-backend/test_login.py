import requests
import json

# Server URL
BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """Test the email-login endpoint with our test user"""
    print("Testing login with test user...")
    
    # Credentials for our test user
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        # Make the login request
        response = requests.post(
            f"{BASE_URL}/email-login", 
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Print the response
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        
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

if __name__ == "__main__":
    test_login() 
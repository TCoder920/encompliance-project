import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

def test_signup():
    """Test user signup endpoint."""
    url = f"{BASE_URL}/signup"
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    }
    
    response = requests.post(url, json=data)
    print(f"Signup Response Status: {response.status_code}")
    print(f"Signup Response Body: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_login():
    """Test user login endpoint."""
    url = f"{BASE_URL}/login"
    data = {
        "username": "testuser",
        "password": "password123"
    }
    
    response = requests.post(url, data=data)
    print(f"Login Response Status: {response.status_code}")
    print(f"Login Response Body: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_protected_endpoint(token):
    """Test a protected endpoint."""
    url = f"{BASE_URL}/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Protected Endpoint Response Status: {response.status_code}")
    print(f"Protected Endpoint Response Body: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

if __name__ == "__main__":
    # Test signup
    try:
        user = test_signup()
        print("\nSignup successful!\n")
    except Exception as e:
        print(f"\nSignup failed: {e}\n")
        user = None
    
    # Test login
    try:
        token_data = test_login()
        token = token_data.get("access_token")
        print("\nLogin successful!\n")
    except Exception as e:
        print(f"\nLogin failed: {e}\n")
        token = None
    
    # Test protected endpoint
    if token:
        try:
            protected_data = test_protected_endpoint(token)
            print("\nAccessed protected endpoint successfully!\n")
        except Exception as e:
            print(f"\nFailed to access protected endpoint: {e}\n")
    else:
        print("\nSkipping protected endpoint test because login failed.\n") 
"""
Test script to verify that the config module works correctly.
"""
from app.core.config import get_settings

def main():
    """Test that the config module works."""
    try:
        # Try to get settings
        settings = get_settings()
        print("Success! Settings loaded correctly:")
        print(f"DATABASE_URL: {settings.DATABASE_URL}")
        print(f"API_V1_STR: {settings.API_V1_STR}")
        return True
    except Exception as e:
        print(f"Error loading settings: {str(e)}")
        return False

if __name__ == "__main__":
    main() 
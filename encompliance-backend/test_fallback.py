from app.services.llm_service import get_error_response

def test_error_response():
    """Test the error response function."""
    error_message = "Failed to connect to LLM service at http://127.0.0.1:1234"
    
    response = get_error_response(error_message)
    print(f"Response: {response}")

if __name__ == "__main__":
    test_error_response() 
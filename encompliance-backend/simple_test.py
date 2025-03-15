def get_error_response(error_message):
    """
    Format an error message for display to users when LLM services are unavailable.
    """
    return f"""I apologize, but I encountered a technical issue processing your request.

Error details: {error_message}

Please try the following:
1. Check that your local model server is running if using the Local LLM
2. Verify your API keys are properly configured if using OpenAI models
3. Contact system administrator if the issue persists"""

def test_error_response():
    """Test the error response function."""
    error_message = "Cannot connect to LLM service at http://127.0.0.1:1234"
    
    response = get_error_response(error_message)
    print(f"Response: {response}")

if __name__ == "__main__":
    test_error_response() 
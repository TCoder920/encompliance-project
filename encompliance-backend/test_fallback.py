from app.services.llm_service import get_fallback_response

def test_fallback():
    """Test the fallback response function."""
    prompt = "What are the requirements for background checks?"
    operation_type = "daycare"
    
    response = get_fallback_response(prompt, operation_type)
    print(f"Response: {response}")

if __name__ == "__main__":
    test_fallback() 
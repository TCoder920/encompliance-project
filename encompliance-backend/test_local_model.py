import asyncio
import os
from app.services.llm_service import call_local_model_api, get_fallback_response
from app.core.config import get_settings

settings = get_settings()

async def test_local_model():
    """Test the local model API."""
    prompt = "What are the requirements for background checks in daycare operations?"
    operation_type = "daycare"
    
    # Test with USE_LOCAL_MODEL set to true
    os.environ["USE_LOCAL_MODEL"] = "true"
    
    try:
        print("Testing local model API...")
        response = await call_local_model_api(
            prompt=prompt,
            operation_type=operation_type,
            message_history=None,
            model=settings.LOCAL_MODEL_NAME
        )
        print(f"Local model response: {response}")
    except Exception as e:
        print(f"Error calling local model API: {str(e)}")
        print("Falling back to demo response...")
        response = get_fallback_response(prompt, operation_type)
        print(f"Fallback response: {response}")

if __name__ == "__main__":
    asyncio.run(test_local_model()) 
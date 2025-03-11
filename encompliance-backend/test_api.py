import httpx
import asyncio
import json

async def test_chat_endpoint():
    """Test the /chat endpoint with a simple query."""
    url = "http://localhost:8000/api/v1/chat"
    
    payload = {
        "prompt": "What are the requirements for background checks?",
        "operation_type": "daycare",
        "model": "demo"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_chat_endpoint()) 
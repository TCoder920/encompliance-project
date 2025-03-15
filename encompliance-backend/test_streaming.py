import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the LM Studio URL from environment variables
LM_STUDIO_URL = os.getenv("LOCAL_MODEL_URL", "http://localhost:1234/v1")

# Remove trailing slash if present
if LM_STUDIO_URL.endswith('/'):
    LM_STUDIO_URL = LM_STUDIO_URL[:-1]

# Check if /v1 is already in the base URL to avoid duplication
if '/v1' in LM_STUDIO_URL:
    CHAT_ENDPOINT = f"{LM_STUDIO_URL}/chat/completions"
else:
    CHAT_ENDPOINT = f"{LM_STUDIO_URL}/v1/chat/completions"

async def test_streaming():
    """
    Test streaming with LM Studio.
    """
    print(f"Testing streaming with LM Studio at: {CHAT_ENDPOINT}")
    
    # Prepare the request payload
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Count from 1 to 10, with a brief pause between each number."}
        ],
        "temperature": 0.7,
        "max_tokens": 1500,
        "stream": True  # Enable streaming
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                CHAT_ENDPOINT,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=120.0
            ) as response:
                if response.status_code != 200:
                    print(f"Error: {response.status_code}")
                    print(await response.text())
                    return
                
                print("Streaming response:")
                print("-" * 50)
                
                # Process streaming response
                buffer = ""
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        # Parse the SSE data format
                        for line in chunk.strip().split('\n'):
                            if line.startswith('data: '):
                                data = line[6:]  # Remove 'data: ' prefix
                                if data.strip() == '[DONE]':
                                    print("\n[DONE]")
                                    break

                                try:
                                    chunk_data = json.loads(data)
                                    if (
                                        chunk_data.get("choices") and 
                                        chunk_data["choices"][0].get("delta") and 
                                        chunk_data["choices"][0]["delta"].get("content")
                                    ):
                                        text_chunk = chunk_data["choices"][0]["delta"]["content"]
                                        buffer += text_chunk
                                        print(text_chunk, end="", flush=True)
                                except Exception as e:
                                    print(f"\nError parsing chunk data: {str(e)}")
                                    print(f"Raw chunk: {data[:100]}")
                                    continue
                
                print("\n" + "-" * 50)
                print(f"Complete response: {buffer}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_streaming()) 
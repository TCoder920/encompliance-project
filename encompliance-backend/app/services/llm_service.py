import httpx
import json
from typing import List, Optional, Dict, Any
from app.core.config import get_settings

settings = get_settings()

async def get_llm_response(
    prompt: str,
    operation_type: str,
    message_history: List[Dict[str, str]] = None,
    pdf_ids: Optional[List[int]] = None,
    model: str = None
) -> str:
    """
    Get a response from an LLM based on the selected model.
    
    Args:
        prompt: The user's query
        operation_type: The type of operation (daycare, residential, etc.)
        message_history: Previous messages in the conversation
        pdf_ids: IDs of PDFs to reference (for future implementation)
        model: The LLM model to use (defaults to settings.DEFAULT_MODEL)
        
    Returns:
        The LLM's response as a string
    """
    if not model:
        model = settings.DEFAULT_MODEL
    
    # Check if we should use a local model
    if settings.USE_LOCAL_MODEL or model == settings.LOCAL_MODEL_NAME or model == "local-model":
        return await call_local_model_api(prompt, operation_type, message_history, model)
    
    # Otherwise, use OpenAI API
    if model.startswith("gpt"):
        return await call_openai_api(prompt, operation_type, message_history, model)
    else:
        # Fallback to demo response if model not supported or no API key
        return get_fallback_response(prompt, operation_type)

async def call_openai_api(
    prompt: str,
    operation_type: str,
    message_history: List[Dict[str, str]] = None,
    model: str = "gpt-4o-mini"
) -> str:
    """Call the OpenAI API to get a response."""
    if not settings.OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
    
    # Format the conversation history
    messages = []
    
    # Add system message with context
    system_message = f"You are a compliance assistant for {operation_type} operations. " \
                     f"Provide accurate, helpful information about compliance regulations and requirements."
    messages.append({"role": "system", "content": system_message})
    
    # Add conversation history if provided
    if message_history:
        # Ensure we're working with dictionaries
        for msg in message_history:
            if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                messages.append({"role": msg['role'], "content": msg['content']})
            elif hasattr(msg, 'role') and hasattr(msg, 'content'):
                # If it's an object with role and content attributes
                messages.append({"role": msg.role, "content": msg.content})
    
    # Add the current prompt
    messages.append({"role": "user", "content": prompt})
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            
            if response.status_code != 200:
                error_detail = response.json().get("error", {}).get("message", "Unknown error")
                raise Exception(f"OpenAI API error: {error_detail}")
                
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except httpx.RequestError as e:
        raise Exception(f"Error communicating with OpenAI API: {str(e)}")

async def call_local_model_api(
    prompt: str,
    operation_type: str,
    message_history: List[Dict[str, str]] = None,
    model: str = None
) -> str:
    """Call a local LLM API (LM Studio) to get a response."""
    if not model or model == "local-model":
        model = settings.LOCAL_MODEL_NAME
    
    # Format the conversation history
    messages = []
    
    # Add system message with context
    system_message = f"You are a compliance assistant for {operation_type} operations. " \
                     f"Provide accurate, helpful information about compliance regulations and requirements."
    messages.append({"role": "system", "content": system_message})
    
    # Add conversation history if provided
    if message_history:
        # Ensure we're working with dictionaries
        for msg in message_history:
            if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                messages.append({"role": msg['role'], "content": msg['content']})
            elif hasattr(msg, 'role') and hasattr(msg, 'content'):
                # If it's an object with role and content attributes
                messages.append({"role": msg.role, "content": msg.content})
    
    # Add the current prompt
    messages.append({"role": "user", "content": prompt})
    
    # First try calling the LM Studio API using OpenAI-compatible format
    try:
        return await call_lmstudio_api(messages, model)
    except Exception as e:
        print(f"LM Studio API call failed: {str(e)}")
        # Fallback to direct completion if chat API fails
        try:
            return await call_direct_completion_api(prompt, model)
        except Exception as direct_err:
            print(f"Direct completion API failed: {str(direct_err)}")
            # If all else fails, return fallback response
            return get_fallback_response(prompt, operation_type)

async def call_direct_completion_api(prompt: str, model: str) -> str:
    """Call the LM Studio completion API directly."""
    # Format the prompt with a simple prefix
    formatted_prompt = f"The following is a conversation with an AI compliance assistant. The assistant provides accurate, helpful information about compliance regulations and requirements.\n\nUser: {prompt}\n\nAssistant:"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.LOCAL_MODEL_URL}/completions",
                headers={
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "prompt": formatted_prompt,
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                response_text = response.text
                try:
                    error_detail = response.json().get("error", {}).get("message", "Unknown error")
                    raise Exception(f"LM Studio API error: {error_detail}")
                except json.JSONDecodeError:
                    raise Exception(f"LM Studio API non-JSON error: {response_text}")
                
            try:
                result = response.json()
                return result["choices"][0]["text"]
            except (KeyError, IndexError) as e:
                raise Exception(f"Unexpected response format: {str(e)}, Response: {response.text}")
    except httpx.RequestError as e:
        raise Exception(f"Error communicating with LM Studio API: {str(e)}")

async def call_lmstudio_api(messages: List[Dict[str, str]], model: str) -> str:
    """Call the LM Studio API with chat format."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.LOCAL_MODEL_URL}/chat/completions",
                headers={
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "stream": False
                }
            )
            
            # Log the raw response for debugging
            print(f"LM Studio API raw response: {response.status_code}")
            response_text = response.text
            print(f"Response text: {response_text[:500]}...")  # Print first 500 chars for debugging
            
            if response.status_code != 200:
                try:
                    error_detail = response.json().get("error", {}).get("message", "Unknown error")
                    raise Exception(f"LM Studio API error: {error_detail}")
                except json.JSONDecodeError:
                    raise Exception(f"LM Studio API non-JSON error: {response_text}")
            
            try:
                result = response.json()
                
                # Debug the response structure
                print(f"LM Studio response keys: {result.keys()}")
                
                # Try to handle different response formats
                if "choices" in result and len(result["choices"]) > 0:
                    if "message" in result["choices"][0]:
                        return result["choices"][0]["message"]["content"]
                    elif "text" in result["choices"][0]:
                        return result["choices"][0]["text"]
                    else:
                        print(f"Unknown choice format: {result['choices'][0].keys()}")
                elif "output" in result:
                    return result["output"]
                elif "text" in result:
                    return result["text"]
                elif "response" in result:
                    return result["response"]
                elif "generated_text" in result:
                    return result["generated_text"]
                elif "message" in result:
                    return result["message"]
                else:
                    print(f"Unknown response format: {result}")
                    raise Exception(f"Unknown response format from LM Studio: {list(result.keys())}")
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                raise Exception(f"Error parsing LM Studio response: {str(e)}, Response: {response_text[:200]}...")
    except httpx.RequestError as e:
        raise Exception(f"Error communicating with LM Studio API: {str(e)}")

def get_fallback_response(prompt: str, operation_type: str) -> str:
    """
    Provide a fallback response when API keys are not available or for demo mode.
    """
    prompt_lower = prompt.lower()
    
    if "ratio" in prompt_lower and operation_type == "daycare":
        return "Per § 746.1601 and § 746.1609, the child-to-caregiver ratio for 2-year-olds is 11:1 when children are grouped by age. This means one caregiver may supervise up to 11 two-year-old children. If you have more than 11 two-year-olds, you'll need additional caregivers to maintain this ratio."
    elif "background check" in prompt_lower:
        return "According to the standards, all employees, volunteers, and household members (for home-based operations) must undergo a background check before having contact with children in care. This includes a criminal history check, central registry check, and fingerprinting. These checks must be renewed periodically as specified in the minimum standards."
    elif "training" in prompt_lower or "hours" in prompt_lower:
        if operation_type == "daycare":
            return "Per § 746.1309, caregivers must complete a minimum of 24 clock hours of training annually. This training must include specific topics such as child development, guidance and discipline, age-appropriate activities, and health and safety."
        else:
            return "According to § 748.930, caregivers in GROs must complete a minimum of 30 clock hours of training annually, including topics specific to the needs of children in care."
    else:
        return "I'd be happy to help with your question. Could you provide more details about the specific compliance area you're inquiring about? I can provide information on ratios, background checks, training requirements, physical facilities, health practices, and other regulatory areas." 
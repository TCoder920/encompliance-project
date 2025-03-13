import httpx
import json
from typing import List, Optional, Dict, Any
from app.core.config import get_settings
from app.core.chat_utils import (
    enhance_system_message_with_pdf_context, 
    format_chat_history, 
    get_compliance_system_message
)
from app.services.pdf_service import get_pdf_context
from sqlalchemy.orm import Session

settings = get_settings()

async def get_llm_response(
    prompt: str,
    operation_type: str,
    message_history: List[Dict[str, str]] = None,
    pdf_ids: Optional[List[int]] = None,
    model: str = None,
    pdf_context: Optional[str] = None,
    db: Optional[Session] = None
) -> str:
    """
    Get a response from an LLM based on the selected model.
    
    Args:
        prompt: The user's query
        operation_type: The type of operation (daycare, residential, etc.)
        message_history: Previous messages in the conversation
        pdf_ids: IDs of PDFs to reference
        model: The LLM model to use (defaults to settings.DEFAULT_MODEL)
        pdf_context: Text extracted from PDFs (optional - will be retrieved if pdf_ids provided)
        db: Database session (required if pdf_ids provided)
        
    Returns:
        The LLM's response as a string
    """
    if not model:
        model = settings.DEFAULT_MODEL
    
    # Get PDF context if pdf_ids provided but no context yet
    if pdf_ids and not pdf_context and db:
        try:
            pdf_context = await get_pdf_context(pdf_ids, db)
            print(f"Retrieved {len(pdf_context)} characters of context from {len(pdf_ids)} PDFs")
            
            # Trim context if it's too long (to avoid token limits)
            max_context_length = 8000  # Adjust based on model's capabilities
            if len(pdf_context) > max_context_length:
                print(f"PDF context too long ({len(pdf_context)} chars), trimming to {max_context_length} chars")
                pdf_context = pdf_context[:max_context_length] + "...[additional content trimmed]"
        except Exception as e:
            print(f"Error getting PDF context: {str(e)}")
            import traceback
            print(traceback.format_exc())
            # Continue without PDF context
            pdf_context = None
    
    # Get base system message
    system_message = get_compliance_system_message(operation_type)
    
    # Enhance with PDF context if available
    if pdf_context:
        # Format PDF context to be more explicit
        pdf_section = "\n\nREFERENCE DOCUMENT CONTENT:\n\n" + pdf_context
        system_message = f"{system_message}{pdf_section}"
        print(f"Enhanced system message with {len(pdf_context)} characters of PDF context")
    elif pdf_ids and db:
        # Try to enhance system message with PDF context
        system_message = await enhance_system_message_with_pdf_context(system_message, pdf_ids, db)
    
    # Format message history
    formatted_history = format_chat_history(message_history or [], system_message)
    
    # Add the current prompt with explicit reference to PDF if context is provided
    if pdf_context:
        # Make the prompt explicitly reference the provided document
        enhanced_prompt = f"{prompt}\n\nPlease use the information from the provided document in your response."
        formatted_history.append({"role": "user", "content": enhanced_prompt})
    else:
        formatted_history.append({"role": "user", "content": prompt})
    
    print(f"Total message history entries: {len(formatted_history)}")
    print(f"System message length: {len(formatted_history[0]['content'])}")
    
    # Check if we should use a local model
    if settings.USE_LOCAL_MODEL or model == settings.LOCAL_MODEL_NAME or model == "local-model":
        try:
            return await call_local_model_api(formatted_history, model)
        except Exception as e:
            print(f"Error calling local model: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return get_fallback_response(prompt, operation_type)
    
    # Otherwise, use OpenAI API
    if model.startswith("gpt"):
        try:
            return await call_openai_api(formatted_history, model)
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return get_fallback_response(prompt, operation_type)
    else:
        # Fallback to demo response if model not supported or no API key
        return get_fallback_response(prompt, operation_type)

async def call_openai_api(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-mini"
) -> str:
    """
    Call the OpenAI API to get a response.
    
    Args:
        messages: Formatted message history including system, user, and assistant messages
        model: The OpenAI model to use
        
    Returns:
        The LLM's response as a string
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
    
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
    messages: List[Dict[str, str]],
    model: str = None
) -> str:
    """
    Call a local LLM API (LM Studio) to get a response.
    
    Args:
        messages: Formatted message history including system, user, and assistant messages
        model: The local model name to use
        
    Returns:
        The LLM's response as a string
    """
    if not model or model == "local-model":
        model = settings.LOCAL_MODEL_NAME
    
    # First try calling the LM Studio API using OpenAI-compatible format
    try:
        return await call_lmstudio_api(messages, model)
    except Exception as e:
        print(f"LM Studio API call failed: {str(e)}")
        # Fallback to direct completion if chat API fails
        try:
            # Extract the last user message for direct completion
            last_user_message = ""
            system_context = ""
            
            for msg in messages:
                if msg["role"] == "system":
                    system_context = msg["content"]
                elif msg["role"] == "user":
                    last_user_message = msg["content"]
            
            # Combine system context and last user message for direct completion
            if system_context and last_user_message:
                combined_prompt = f"{system_context}\n\nUser query: {last_user_message}"
                return await call_direct_completion_api(combined_prompt, model)
            else:
                return await call_direct_completion_api(last_user_message, model)
        except Exception as direct_err:
            print(f"Direct completion API failed: {str(direct_err)}")
            # If all else fails, return fallback response
            return get_fallback_response(last_user_message, "compliance")

async def call_lmstudio_api(messages: List[Dict[str, str]], model: str) -> str:
    """
    Call the LM Studio API with chat format.
    
    Args:
        messages: Formatted message history
        model: The model name to use
        
    Returns:
        The LLM's response as a string
    """
    try:
        # Use the LM Studio OpenAI-compatible chat endpoint
        # Note: LOCAL_MODEL_URL already includes /v1, so don't add it again
        endpoint_url = f"{settings.LOCAL_MODEL_URL}/chat/completions"
        print(f"Calling LM Studio API at: {endpoint_url}")
        print(f"Using model: {model}")
        print(f"Message count: {len(messages)}")
        
        # Print a preview of each message for debugging
        for i, msg in enumerate(messages):
            content_preview = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            print(f"Message {i} (role={msg['role']}): {content_preview}")
        
        async with httpx.AsyncClient(timeout=120.0) as client:  # Increased timeout for local models
            response = await client.post(
                endpoint_url,
                headers={"Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1500
                },
                timeout=120.0  # Explicitly set timeout here too
            )
            
            # Get the response text
            response_text = response.text
            print(f"LM Studio API response status: {response.status_code}")
            print(f"LM Studio API response preview: {response_text[:200]}...")
            
            if response.status_code != 200:
                raise Exception(f"LM Studio API error: {response_text}")
            
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

async def call_direct_completion_api(prompt: str, model: str) -> str:
    """
    Call the LM Studio API with direct completion.
    
    Args:
        prompt: The prompt to send
        model: The model name to use
        
    Returns:
        The LLM's response as a string
    """
    try:
        endpoint_url = f"{settings.LOCAL_MODEL_URL}/completions"
        print(f"Calling LM Studio completion API at: {endpoint_url}")
        print(f"Using model: {model}")
        print(f"Prompt length: {len(prompt)}")
        print(f"Prompt preview: {prompt[:200]}...")
        
        # Trim prompt if too long for model
        max_prompt_length = 12000  # Adjust based on model's token limit
        if len(prompt) > max_prompt_length:
            print(f"Prompt too long ({len(prompt)} chars), trimming to {max_prompt_length}")
            # Keep the beginning and the end, trim the middle
            beginning = prompt[:max_prompt_length//2]
            ending = prompt[-max_prompt_length//2:]
            prompt = beginning + "\n\n[...content trimmed...]\n\n" + ending
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                endpoint_url,
                headers={"Content-Type": "application/json"},
                json={
                    "model": model,
                    "prompt": prompt,
                    "temperature": 0.7,
                    "max_tokens": 1500,
                    "stop": ["User:", "Human:", "\n\nHuman:", "\n\nUser:"]
                },
                timeout=120.0
            )
            
            print(f"LM Studio completion API response status: {response.status_code}")
            print(f"LM Studio completion API response preview: {response.text[:200]}...")
            
            if response.status_code != 200:
                raise Exception(f"LM Studio completion API error: {response.text}")
                
            try:
                result = response.json()
                print(f"LM Studio completion response keys: {result.keys()}")
                
                # Try to handle different response formats
                if "choices" in result and len(result["choices"]) > 0:
                    if "text" in result["choices"][0]:
                        return result["choices"][0]["text"]
                    else:
                        print(f"Unknown choice format: {result['choices'][0].keys()}")
                elif "text" in result:
                    return result["text"]
                else:
                    raise Exception(f"Unknown response format from LM Studio: {list(result.keys())}")
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                raise Exception(f"Error parsing LM Studio completion response: {str(e)}")
    except httpx.RequestError as e:
        raise Exception(f"Error communicating with LM Studio completion API: {str(e)}")

def get_fallback_response(prompt: str, operation_type: str) -> str:
    """
    Get a fallback response when the LLM is unavailable.
    
    Args:
        prompt: The user's query
        operation_type: The type of operation (daycare, residential, etc.)
        
    Returns:
        A fallback response
    """
    # Check if prompt is asking about specific areas
    prompt_lower = prompt.lower()
    
    if "ratio" in prompt_lower or "staff" in prompt_lower or "child" in prompt_lower:
        return f"""For {operation_type} operations, the required staff-to-child ratio depends on the age of the children:
- For infants (0-17 months): 1:4 ratio
- For toddlers (18-35 months): 1:5 ratio
- For preschoolers (3-5 years): 1:10 ratio
- For school-age children (6+ years): 1:15 ratio

These ratios must be maintained at all times, including during nap time, meal time, and outdoor play."""
    
    elif "training" in prompt_lower or "certification" in prompt_lower:
        return f"""Staff in {operation_type} operations need the following training:
1. Pre-service orientation (24 clock hours before working with children)
2. Annual training (24 clock hours per year)
3. CPR and First Aid certification
4. Transportation safety (if applicable)
5. Child abuse and neglect prevention

All training must be documented and records kept for at least 3 years."""
    
    elif "safety" in prompt_lower or "emergency" in prompt_lower:
        return f"""Safety requirements for {operation_type} operations include:
- Monthly fire drills and quarterly shelter-in-place drills
- Emergency evacuation plans posted in each room
- First aid kits easily accessible to all caregivers
- Working smoke detectors and fire extinguishers
- Secured hazardous materials and medications
- Daily playground safety checks

All incidents and injuries must be documented and reported to parents."""
    
    else:
        return f"""I'm currently operating in fallback mode with limited information about {operation_type} operations. 

For the most accurate and up-to-date compliance information, please:
1. Check the official licensing regulations for your state
2. Consult with your licensing representative
3. Try again later when the full AI system is available

I apologize for the limited assistance at this time.""" 
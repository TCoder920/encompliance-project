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
    
    # Determine which API to use based on the model
    if model.startswith("gpt"):
        return await call_openai_api(prompt, operation_type, message_history, model)
    elif model.startswith("claude"):
        return await call_anthropic_api(prompt, operation_type, message_history, model)
    else:
        # Fallback to demo response if model not supported or no API key
        return get_fallback_response(prompt, operation_type)

async def call_openai_api(
    prompt: str,
    operation_type: str,
    message_history: List[Dict[str, str]] = None,
    model: str = "gpt-3.5-turbo"
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
        messages.extend(message_history)
    
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

async def call_anthropic_api(
    prompt: str,
    operation_type: str,
    message_history: List[Dict[str, str]] = None,
    model: str = "claude-3-sonnet-20240229"
) -> str:
    """Call the Anthropic API to get a response."""
    if not settings.ANTHROPIC_API_KEY:
        raise ValueError("Anthropic API key is not set. Please set the ANTHROPIC_API_KEY environment variable.")
    
    # Format the conversation history for Anthropic
    messages = []
    
    # Add conversation history if provided
    if message_history:
        for msg in message_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    # Add the current prompt
    messages.append({"role": "user", "content": prompt})
    
    # Prepare the system prompt
    system_prompt = f"You are a compliance assistant for {operation_type} operations. " \
                    f"Provide accurate, helpful information about compliance regulations and requirements."
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "system": system_prompt,
                    "messages": messages,
                    "max_tokens": 1000
                }
            )
            
            if response.status_code != 200:
                error_detail = response.json().get("error", {}).get("message", "Unknown error")
                raise Exception(f"Anthropic API error: {error_detail}")
                
            result = response.json()
            return result["content"][0]["text"]
    except httpx.RequestError as e:
        raise Exception(f"Error communicating with Anthropic API: {str(e)}")

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
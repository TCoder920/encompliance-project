import json
from typing import Dict, List, Optional, Union

import httpx
from fastapi import HTTPException
from loguru import logger
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


class AIService:
    """
    Service for interacting with AI models (Llama or OpenAI)
    """
    
    def __init__(self):
        self.model_type = settings.AI_MODEL_TYPE
        self.model_endpoint = settings.AI_MODEL_ENDPOINT
        
        if self.model_type == "openai" and settings.AI_MODEL_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=settings.AI_MODEL_API_KEY)
        
        # System prompts for different operation types
        self.system_prompts = {
            "daycare": """You are an expert AI assistant specializing in Texas Licensed and Registered Child-Care Homes (Chapter 746) compliance regulations. 
            
            Provide accurate, helpful information about compliance requirements, standards, and best practices.
            
            When answering questions:
            1. Cite specific sections of the minimum standards when applicable (e.g., "According to § 746.1601...")
            2. Be concise but thorough
            3. Focus on practical implementation of regulations
            4. If you're unsure about a specific regulation, acknowledge this and suggest where the user might find more information
            
            The Texas Health and Human Services Commission (HHSC) is the regulatory body for these operations.""",
            
            "gro": """You are an expert AI assistant specializing in Texas General Residential Operations (Chapter 748) compliance regulations. 
            
            Provide accurate, helpful information about compliance requirements, standards, and best practices.
            
            When answering questions:
            1. Cite specific sections of the minimum standards when applicable (e.g., "According to § 748.930...")
            2. Be concise but thorough
            3. Focus on practical implementation of regulations
            4. If you're unsure about a specific regulation, acknowledge this and suggest where the user might find more information
            
            The Texas Health and Human Services Commission (HHSC) is the regulatory body for these operations."""
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_ai_response(
        self,
        prompt: str,
        operation_type: str,
        message_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, str]:
        """
        Get a response from the AI model
        """
        if not message_history:
            message_history = []
        
        system_prompt = self.system_prompts.get(
            operation_type, self.system_prompts["daycare"]
        )
        
        try:
            if self.model_type == "openai":
                return await self._get_openai_response(prompt, system_prompt, message_history)
            else:
                return await self._get_llama_response(prompt, system_prompt, message_history)
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            return self._get_fallback_response(prompt, operation_type)
    
    async def _get_openai_response(
        self,
        prompt: str,
        system_prompt: str,
        message_history: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Get a response from OpenAI
        """
        if not hasattr(self, "openai_client"):
            raise ValueError("OpenAI client not initialized. API key may be missing.")
        
        messages = [
            {"role": "system", "content": system_prompt},
            *message_history,
            {"role": "user", "content": prompt}
        ]
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o",  # Can be configured in settings
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return {
            "text": response.choices[0].message.content or "I'm sorry, I couldn't generate a response."
        }
    
    async def _get_llama_response(
        self,
        prompt: str,
        system_prompt: str,
        message_history: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Get a response from Llama model via API endpoint
        """
        messages = [
            {"role": "system", "content": system_prompt},
            *message_history,
            {"role": "user", "content": prompt}
        ]
        
        payload = {
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.model_endpoint,
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                logger.error(f"Error from Llama API: {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error from AI model")
            
            result = response.json()
            return {
                "text": result.get("response", "I'm sorry, I couldn't generate a response.")
            }
    
    def _get_fallback_response(self, prompt: str, operation_type: str) -> Dict[str, str]:
        """
        Get a fallback response when AI is unavailable
        """
        prompt_lower = prompt.lower()
        
        if "ratio" in prompt_lower and operation_type == "daycare":
            return {
                "text": "Per § 746.1601 and § 746.1609, the child-to-caregiver ratio for 2-year-olds is 11:1 when children are grouped by age. This means one caregiver may supervise up to 11 two-year-old children. If you have more than 11 two-year-olds, you'll need additional caregivers to maintain this ratio."
            }
        elif "background check" in prompt_lower:
            return {
                "text": "According to the standards, all employees, volunteers, and household members (for home-based operations) must undergo a background check before having contact with children in care. This includes a criminal history check, central registry check, and fingerprinting. These checks must be renewed periodically as specified in the minimum standards."
            }
        elif "training" in prompt_lower or "hours" in prompt_lower:
            if operation_type == "daycare":
                return {
                    "text": "Per § 746.1309, caregivers must complete a minimum of 24 clock hours of training annually. This training must include specific topics such as child development, guidance and discipline, age-appropriate activities, and health and safety."
                }
            else:
                return {
                    "text": "According to § 748.930, caregivers in GROs must complete a minimum of 30 clock hours of training annually, including topics specific to the needs of children in care."
                }
        else:
            return {
                "text": "I'd be happy to help with your question. Could you provide more details about the specific compliance area you're inquiring about? I can provide information on ratios, background checks, training requirements, physical facilities, health practices, and other regulatory areas."
            }


# Create a singleton instance
ai_service = AIService()

import logging
import os
from typing import List, Optional

from app.core.config import settings
from app.schemas.chat import ChatMessage, ChatResponse

logger = logging.getLogger(__name__)

# Try to import llama_cpp for local model if available
try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    logger.warning("llama_cpp not available, using placeholder responses")
    LLAMA_AVAILABLE = False


class AIService:
    def __init__(self):
        self.model = None
        self.use_local_ai = settings.USE_LOCAL_AI
        
        # Initialize local model if configured
        if self.use_local_ai and LLAMA_AVAILABLE:
            try:
                model_path = settings.AI_MODEL_PATH
                if os.path.exists(model_path):
                    logger.info(f"Loading AI model from {model_path}")
                    self.model = Llama(
                        model_path=model_path,
                        n_ctx=4096,
                        n_threads=4
                    )
                    logger.info("AI model loaded successfully")
                else:
                    logger.warning(f"Model file not found at {model_path}, using placeholder responses")
            except Exception as e:
                logger.error(f"Error loading AI model: {e}")
                self.model = None
    
    def get_response(
        self, 
        prompt: str, 
        operation_type: Optional[str] = None,
        message_history: Optional[List[ChatMessage]] = None
    ) -> ChatResponse:
        """Get a response from the AI model or fallback to placeholder"""
        
        if message_history is None:
            message_history = []
        
        # If we have a local model and it's loaded, use it
        if self.use_local_ai and self.model:
            try:
                # Format the prompt with message history
                formatted_prompt = self._format_prompt(prompt, operation_type, message_history)
                
                # Generate response from model
                response = self.model(
                    formatted_prompt,
                    max_tokens=1024,
                    temperature=0.7,
                    top_p=0.95,
                    stop=["User:", "\n\n"]
                )
                
                # Extract the generated text
                generated_text = response["choices"][0]["text"].strip()
                return ChatResponse(text=generated_text)
            
            except Exception as e:
                logger.error(f"Error generating AI response: {e}")
                return ChatResponse(
                    text="I'm sorry, I encountered an error processing your request.",
                    error=str(e)
                )
        
        # Otherwise use placeholder responses
        return self._get_placeholder_response(prompt, operation_type)
    
    def _format_prompt(
        self, 
        prompt: str, 
        operation_type: Optional[str],
        message_history: List[ChatMessage]
    ) -> str:
        """Format the prompt with message history for the model"""
        
        # System instruction
        system_instruction = (
            "You are an AI assistant for Encompliance.io, a compliance platform for childcare operations. "
            "You help users understand regulatory requirements and compliance standards. "
        )
        
        if operation_type:
            system_instruction += f"The user operates a {operation_type} facility. "
        
        system_instruction += (
            "Provide accurate, helpful information about compliance requirements. "
            "If you're unsure about something, acknowledge it rather than providing incorrect information."
        )
        
        # Format the conversation history
        conversation = f"System: {system_instruction}\n\n"
        
        # Add message history
        for message in message_history:
            role = "Assistant" if message.role == "assistant" else "User"
            conversation += f"{role}: {message.content}\n\n"
        
        # Add the current prompt
        conversation += f"User: {prompt}\n\nAssistant:"
        
        return conversation
    
    def _get_placeholder_response(self, prompt: str, operation_type: Optional[str]) -> ChatResponse:
        """Generate a placeholder response when AI model is not available"""
        
        prompt_lower = prompt.lower()
        
        # Simple pattern matching for common questions
        if "ratio" in prompt_lower and operation_type == "daycare":
            return ChatResponse(
                text="Per § 746.1601 and § 746.1609, the child-to-caregiver ratio for 2-year-olds is 11:1 when children are grouped by age. This means one caregiver may supervise up to 11 two-year-old children. If you have more than 11 two-year-olds, you'll need additional caregivers to maintain this ratio."
            )
        elif "background check" in prompt_lower:
            return ChatResponse(
                text="According to the standards, all employees, volunteers, and household members (for home-based operations) must undergo a background check before having contact with children in care. This includes a criminal history check, central registry check, and fingerprinting. These checks must be renewed periodically as specified in the minimum standards."
            )
        elif "training" in prompt_lower or "hours" in prompt_lower:
            if operation_type == "daycare":
                return ChatResponse(
                    text="Per § 746.1309, caregivers must complete a minimum of 24 clock hours of training annually. This training must include specific topics such as child development, guidance and discipline, age-appropriate activities, and health and safety."
                )
            else:
                return ChatResponse(
                    text="According to § 748.930, caregivers in GROs must complete a minimum of 30 clock hours of training annually, including topics specific to the needs of children in care."
                )
        else:
            return ChatResponse(
                text="I'd be happy to help with your question. Could you provide more details about the specific compliance area you're inquiring about? I can provide information on ratios, background checks, training requirements, physical facilities, health practices, and other regulatory areas."
            )


# Create a singleton instance
ai_service = AIService() 
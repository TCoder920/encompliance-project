import api from './api';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface AIResponse {
  text: string;
  error?: string;
}

export async function getAIResponse(
  prompt: string, 
  operationType: string,
  messageHistory: ChatMessage[] = []
): Promise<AIResponse> {
  try {
    const response = await api.post('/chat', {
      prompt,
      operation_type: operationType,
      message_history: messageHistory
    });
    
    return response.data;
  } catch (error) {
    console.error('Error calling AI service:', error);
    
    // Fallback response if API call fails
    return getFallbackResponse(prompt, operationType);
  }
}

// Fallback function for when API is not available
export function getFallbackResponse(prompt: string, operationType: string): AIResponse {
  const lcPrompt = prompt.toLowerCase();
  
  if (lcPrompt.includes('ratio') && operationType === 'daycare') {
    return {
      text: "Per § 746.1601 and § 746.1609, the child-to-caregiver ratio for 2-year-olds is 11:1 when children are grouped by age. This means one caregiver may supervise up to 11 two-year-old children. If you have more than 11 two-year-olds, you'll need additional caregivers to maintain this ratio."
    };
  } else if (lcPrompt.includes('background check')) {
    return {
      text: "According to the standards, all employees, volunteers, and household members (for home-based operations) must undergo a background check before having contact with children in care. This includes a criminal history check, central registry check, and fingerprinting. These checks must be renewed periodically as specified in the minimum standards."
    };
  } else if (lcPrompt.includes('training') || lcPrompt.includes('hours')) {
    return {
      text: operationType === 'daycare' 
        ? "Per § 746.1309, caregivers must complete a minimum of 24 clock hours of training annually. This training must include specific topics such as child development, guidance and discipline, age-appropriate activities, and health and safety."
        : "According to § 748.930, caregivers in GROs must complete a minimum of 30 clock hours of training annually, including topics specific to the needs of children in care."
    };
  } else {
    return {
      text: "I'd be happy to help with your question. Could you provide more details about the specific compliance area you're inquiring about? I can provide information on ratios, background checks, training requirements, physical facilities, health practices, and other regulatory areas."
    };
  }
}
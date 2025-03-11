import api from './api';

export interface ChatMessage {
  role: string;
  content: string;
}

export interface AIResponse {
  text: string;
  error?: string;
}

export async function getAIResponse(
  prompt: string, 
  operationType: string,
  messageHistory: ChatMessage[] = [],
  selectedModel: string = 'local-model',
  pdfIds?: number[]
): Promise<AIResponse> {
  try {
    console.log(`Sending chat request to backend with model: ${selectedModel}`);
    
    // Call our backend API
    const response = await api.post('/chat', {
      prompt,
      operation_type: operationType,
      message_history: messageHistory,
      model: selectedModel,
      pdf_ids: pdfIds
    });
    
    console.log('Backend response received:', response.data);
    
    return response.data;
  } catch (error: any) {
    console.error('Error calling AI service:', error);
    
    let errorMessage = 'Failed to connect to the AI service';
    
    // Extract more detailed error information if available
    if (error.response) {
      // The request was made and the server responded with an error status
      console.error('Response error:', error.response.data);
      errorMessage = error.response.data?.error || `Server error: ${error.response.status}`;
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Request error:', error.request);
      errorMessage = 'No response from server. Please check your connection.';
    } else {
      // Something happened in setting up the request
      errorMessage = error.message || 'Unknown error occurred';
    }
    
    return {
      text: "I apologize, but I encountered an error processing your request. Please try again later.",
      error: errorMessage
    };
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
import api from './api';

export interface ChatMessage {
  role: string;
  content: string;
}

/**
 * Get a response from the AI.
 */
export const getAIResponse = async (
  prompt: string,
  operationType: string,
  messageHistory: any[] = [],
  model: string = 'gpt-4o-mini',
  documentIds?: number[]
): Promise<string> => {
  try {
    // Prepare the request payload
    const payload = {
      prompt,
      operation_type: operationType,
      message_history: messageHistory,
      model,
      document_ids: documentIds
    };
    
    // Send the request to the API
    const response = await api.post('/chat', payload);
    
    // Return the response text
    return response.data.response;
  } catch (error) {
    // Handle errors
    throw new Error(error instanceof Error ? error.message : 'Failed to get AI response');
  }
};

/**
 * Get a streaming response from the AI.
 * This function returns a callback that receives chunks of text as they arrive.
 */
export const getStreamingAIResponse = (
  prompt: string,
  operationType: string,
  messageHistory: any[] = [],
  model: string = 'local-model',
  onChunk: (chunk: string) => void,
  onError: (error: string) => void,
  onComplete: () => void,
  documentIds?: number[]
): (() => void) => {
  // Create an AbortController to allow cancelling the stream
  const controller = new AbortController();
  
  // Start the streaming process
  (async () => {
    try {
      // Prepare the request payload
      const payload = {
        prompt,
        operation_type: operationType,
        message_history: messageHistory,
        model,
        stream: true,
        document_ids: documentIds
      };
      
      // Make the request with the signal for aborting
      const response = await fetch(`${api.defaults.baseURL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(payload),
        signal: controller.signal
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }
      
      if (!response.body) {
        throw new Error('Response body is null');
      }
      
      // Set up the stream reader
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      // Process the stream
      while (true) {
        try {
          const { done, value } = await reader.read();
          
          if (done) {
            onComplete();
            break;
          }
          
          // Decode the chunk and pass it to the callback
          const chunk = decoder.decode(value, { stream: true });
          onChunk(chunk);
        } catch (error: any) {
          if (error.name === 'AbortError') {
            // This is an expected error when the user cancels
            break;
          }
          
          // Handle other stream reading errors
          onError('Error reading stream');
          break;
        }
      }
    } catch (error) {
      // Handle request errors
      onError(error instanceof Error ? error.message : 'Error in streaming request');
    }
  })().catch(error => {
    // Handle any uncaught errors in the async function
    onError(error instanceof Error ? error.message : 'Error setting up streaming');
  });
  
  // Return a function to abort the stream
  return () => controller.abort();
};

/**
 * Delete a query from the history.
 */
export const deleteQuery = async (queryId: number): Promise<{ success: boolean }> => {
  try {
    const response = await api.delete(`/query/${queryId}`);
    return response.data;
  } catch (error) {
    throw new Error('Failed to delete query');
  }
};

/**
 * Delete all queries for the current user.
 */
export const deleteAllQueries = async (): Promise<{ success: boolean; count: number }> => {
  try {
    const response = await api.delete('/queries/all');
    return response.data;
  } catch (error) {
    throw new Error('Failed to delete all queries');
  }
};
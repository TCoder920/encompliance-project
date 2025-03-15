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
  model: string = 'local-model',
  documentIds?: number[],
): Promise<string> => {
  console.log(`Sending AI request with model: ${model}`);
  console.log(`Document IDs included: ${documentIds ? documentIds.join(', ') : 'none'}`);
  
  try {
    // For local models, use streaming by default
    const useStreaming = model === 'local-model' || !model.startsWith('gpt-');
    
    const response = await api.post('/chat', {
      prompt,
      operation_type: operationType,
      message_history: messageHistory,
      model,
      document_ids: documentIds,
      stream: useStreaming // Enable streaming for local models
    });
    
    if (response.data.error) {
      throw new Error(response.data.error);
    }
    
    return response.data.text;
  } catch (error) {
    console.error('Error getting AI response:', error);
    throw error;
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
  documentIds?: number[],
): () => void => {
  console.log(`Sending streaming AI request with model: ${model}`);
  console.log(`Document IDs included: ${documentIds ? documentIds.join(', ') : 'none'}`);

  try {
    // Create the request
    const controller = new AbortController();
    const signal = controller.signal;

    // Make the API call
    fetch(`${api.defaults.baseURL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        prompt,
        operation_type: operationType,
        message_history: messageHistory,
        model,
        document_ids: documentIds,
        stream: true // Explicitly set stream to true
      }),
      signal
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }
      
      // Set up the streaming reader
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      // Process the stream
      const processStream = async () => {
        if (!reader) return;
        
        try {
          while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
              onComplete();
              break;
            }
            
            // Decode and process the chunk
            const chunk = decoder.decode(value, { stream: true });
            onChunk(chunk);
          }
        } catch (error) {
          console.error('Error reading stream:', error);
          onError(error instanceof Error ? error.message : 'Error reading response stream');
        }
      };
      
      processStream();
    })
    .catch(error => {
      console.error('Error in streaming request:', error);
      onError(error instanceof Error ? error.message : 'Unknown error in streaming request');
    });
    
    // Return an abort function
    return () => controller.abort();
  } catch (error) {
    console.error('Error setting up streaming:', error);
    onError(error instanceof Error ? error.message : 'Unknown error setting up streaming request');
    return () => {}; // Return empty function as fallback
  }
};

/**
 * Delete a query from the history.
 */
export const deleteQuery = async (queryId: number): Promise<{ message: string }> => {
  try {
    const response = await api.delete(`/query/${queryId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting query:', error);
    throw error;
  }
};

/**
 * Delete all queries for the current user.
 */
export const deleteAllQueries = async (): Promise<{ message: string, count: number }> => {
  try {
    const response = await api.delete('/queries/all');
    return response.data;
  } catch (error) {
    console.error('Error deleting all queries:', error);
    throw error;
  }
};
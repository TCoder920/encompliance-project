import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { getAIResponse, getStreamingAIResponse } from '../services/aiService';
import ErrorMessage from '../components/ErrorMessage';
import { useModel } from '../contexts/ModelContext';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { formatDateTime } from '../utils/dateUtils';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  isLoading?: boolean;
  isStreaming?: boolean;
}

interface AIChatProps {
  operationType: string;
  activePdfIds?: number[];
  conversationId?: number;
  initialQuery?: string;
  initialConversation?: any; // Conversation history
  showFullConversation?: boolean;
}

const AIChat: React.FC<AIChatProps> = ({ 
  operationType, 
  activePdfIds = [],
  conversationId,
  initialQuery = '',
  initialConversation = null,
  showFullConversation = false
}) => {
  const { selectedModel } = useModel();
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: `Welcome to the Encompliance.io AI Assistant. I'm here to help you with any questions about ${
        operationType === 'daycare' 
          ? 'Licensed and Registered Child-Care Homes' 
          : 'General Residential Operations'
      } compliance. How can I assist you today?`,
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  
  const [inputValue, setInputValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<(() => void) | null>(null);
  const [useTypingEffect, setUseTypingEffect] = useState(true);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const typewriterQueueRef = useRef<{text: string, messageId: number} | null>(null);
  const isTypingRef = useRef(false);
  const abortStreamingRef = useRef<(() => void) | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // Clean up any ongoing typing animations when unmounting
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current();
      }
    };
  }, []);
  
  useEffect(() => {
    const loadConversation = async () => {
      if (!conversationId) return;
      
      try {
        setIsProcessing(true);
        setError(null);
        
        // Fetch conversation from the API
        const response = await fetch(`/api/v1/conversations/${conversationId}`);
        
        if (!response.ok) {
          throw new Error(`Failed to load conversation: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Loaded conversation data:', data);
        
        if (data && data.messages && Array.isArray(data.messages)) {
          // Transform the API response to our message format
          const loadedMessages = data.messages.map((msg: any, index: number) => {
            // Ensure we have a valid timestamp
            let timestamp;
            try {
              timestamp = msg.timestamp ? new Date(msg.timestamp) : new Date();
              // Check if the date is valid
              if (isNaN(timestamp.getTime())) {
                console.warn('Invalid timestamp in message:', msg);
                timestamp = new Date(); // Fallback to current time
              }
            } catch (error) {
              console.error('Error parsing timestamp:', error);
              timestamp = new Date(); // Fallback to current time
            }
            
            return {
              id: index + 1,
              text: msg.summary ? msg.summary : msg.content, // Ensure summary text is used
              sender: msg.role === 'user' ? 'user' : 'ai',
              timestamp: timestamp,
              isLoading: false
            };
          });
          
          console.log('Transformed messages:', loadedMessages);
          // Replace the default welcome message with the loaded conversation
          setMessages(loadedMessages);
        }
      } catch (err) {
        console.error('Error loading conversation:', err);
        setError('Failed to load the conversation history. Starting a new conversation instead.');
      } finally {
        setIsProcessing(false);
      }
    };
    
    loadConversation();
  }, [conversationId]);

  // Load initial conversation if available
  useEffect(() => {
    console.log('AIChat initializing with:', { 
      initialConversation: initialConversation ? 'present' : 'not present', 
      initialQuery, 
      showFullConversation 
    });
    
    if (initialConversation && Array.isArray(initialConversation) && initialConversation.length > 0) {
      console.log('Loading initial conversation:', JSON.stringify(initialConversation));
      
      try {
        // Convert the conversation history to the correct format
        const formattedMessages = initialConversation
          .map((msg: any, index: number) => {
            if (!msg || (!msg.content && !msg.text)) {
              console.warn('Invalid message in conversation:', msg);
              return null;
            }
            
            // Ensure we have a valid timestamp
            let timestamp;
            try {
              timestamp = msg.timestamp ? new Date(msg.timestamp) : new Date();
              // Check if the date is valid
              if (isNaN(timestamp.getTime())) {
                console.warn('Invalid timestamp in message:', msg);
                timestamp = new Date(); // Fallback to current time
              }
            } catch (error) {
              console.error('Error parsing timestamp:', error);
              timestamp = new Date(); // Fallback to current time
            }
            
            return {
              id: index + 1,
              text: msg.text || msg.content || '',
              sender: (msg.sender === 'user' || msg.role === 'user') ? 'user' as 'user' : 'ai' as 'ai',
              timestamp: timestamp,
            };
          })
          .filter((msg): msg is Message => msg !== null);
        
        console.log('Formatted messages:', formattedMessages);
        
        if (formattedMessages.length > 0) {
          // Replace the default welcome message with the loaded conversation
          setMessages(formattedMessages);
          setTimeout(scrollToBottom, 100);
        } else {
          console.warn('No messages were formatted from the initial conversation');
          setError('Failed to load the conversation. Starting a new conversation instead.');
        }
      } catch (error) {
        console.error('Error formatting initial conversation:', error);
        setError('Failed to load the conversation. Starting a new conversation instead.');
      }
    } else if (initialQuery && initialQuery.trim() !== '') {
      // If we only have an initial query, set it as the input value
      console.log('Setting initial query:', initialQuery);
      setInputValue(initialQuery);
    }
  }, [initialConversation, initialQuery]);

  // Auto-send initial query for Continue Conversation
  useEffect(() => {
    if (initialQuery && initialQuery.trim() !== '' && !showFullConversation) {
      console.log('Auto-sending initial query for Continue Conversation');
      // We need to wait for the component to fully mount before sending the message
      const timer = setTimeout(() => {
        // We need to manually set the input value and then trigger the send
        setInputValue(initialQuery);
        // Use another timeout to ensure the input value is set before sending
        setTimeout(() => {
          handleSendMessage();
        }, 100);
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [initialQuery, showFullConversation]);

  // Process the typewriter queue
  const processTypewriterQueue = () => {
    if (isTypingRef.current || !typewriterQueueRef.current) return;
    
    const { text, messageId } = typewriterQueueRef.current;
    typewriterQueueRef.current = null;
    
    if (text) {
      startTypewriterEffect(text, messageId);
    }
  };
  
  // Typewriter effect 
  const startTypewriterEffect = (fullText: string, messageId: number) => {
    isTypingRef.current = true;
    let currentIndex = 0;
    const typingSpeed = 10; // milliseconds per character

    // Replace the loading message with an empty message that will be filled character by character
    setMessages(prevMessages => 
      prevMessages.map(msg => 
        msg.id === messageId
          ? {
              ...msg,
              text: "",
              isLoading: false,
              isStreaming: true
            }
          : msg
      )
    );

    const typeNextCharacter = () => {
      if (currentIndex < fullText.length) {
        setMessages(prevMessages => 
          prevMessages.map(msg => 
            msg.id === messageId
              ? {
                  ...msg,
                  text: fullText.substring(0, currentIndex + 1),
                  isStreaming: currentIndex < fullText.length - 1
                }
              : msg
          )
        );
        
        currentIndex++;
        typingTimeoutRef.current = setTimeout(typeNextCharacter, typingSpeed);
      } else {
        // Finished typing
        isTypingRef.current = false;
        processTypewriterQueue();
      }
    };

    // Start the typing effect
    typeNextCharacter();
  };
  
  // Save chat history to backend
  const saveChatHistory = async (userMessage: string, aiResponse: string) => {
    try {
      const response = await api.post('/chat/history', {
        user_message: userMessage,
        ai_response: aiResponse,
        operation_type: operationType,
        document_ids: activePdfIds
      });
      
      if (!response.data.success) {
        console.error('Failed to save chat history:', response.data.error);
        // Log error but don't show to user
      } else {
        console.log('Chat history saved successfully');
      }
    } catch (error) {
      console.error('Failed to save chat history:', error);
      // Log error but don't show to user
    }
  };

  const handleSendMessage = async () => {
    if (inputValue.trim() === '' || isProcessing) return;
    
    console.log('Sending message:', inputValue);
    console.log('Active PDF IDs:', activePdfIds);
    
    // Add user message to the chat
    const userMessageId = messages.length + 1;
    const userMessage = {
      id: userMessageId,
      text: inputValue,
      sender: 'user' as const,
      timestamp: new Date()
    };
    
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInputValue('');
    
    // Scroll to bottom after user message is added
    setTimeout(scrollToBottom, 100);
    
    // Add a loading message for the AI response
    const aiMessageId = userMessageId + 1;
    const loadingMessage = {
      id: aiMessageId,
      text: '',
      sender: 'ai' as const,
      isLoading: true,
      timestamp: new Date()
    };
    
    setMessages(prevMessages => [...prevMessages, loadingMessage]);
    setIsProcessing(true);
    
    try {
      // Ensure document IDs are valid numbers
      const validDocumentIds = activePdfIds && activePdfIds.length > 0 
        ? activePdfIds
            .map(id => {
              if (typeof id === 'string') {
                const parsedId = parseInt(id, 10);
                if (isNaN(parsedId)) {
                  console.warn(`Invalid document ID (not a number): ${id}`);
                  return null;
                }
                return parsedId;
              }
              return id;
            })
            .filter(id => id !== null && id !== undefined)
        : [];
      
      console.log('Valid document IDs:', validDocumentIds);
      
      // Check if we should use streaming
      const useStreaming = selectedModel === 'local-model' || !selectedModel.startsWith('gpt-');
      
      if (useStreaming) {
        // Use streaming for local models
        console.log('Using streaming response for local model');
        
        // Replace the loading message with a streaming message
        setMessages(prevMessages => 
          prevMessages.map(msg => 
            msg.id === aiMessageId
              ? {
                  ...msg,
                  text: '',
                  isLoading: false,
                  isStreaming: true
                }
              : msg
          )
        );
        
        let fullResponse = '';
        
        // Set up the streaming response handler
        const abortStreaming = getStreamingAIResponse(
          userMessage.text,
          operationType,
          [], // No message history for now
          selectedModel,
          (chunk) => {
            // Update the message with each chunk
            fullResponse += chunk;
            setMessages(prevMessages => 
              prevMessages.map(msg => 
                msg.id === aiMessageId
                  ? {
                      ...msg,
                      text: fullResponse,
                      isStreaming: true
                    }
                  : msg
              )
            );
            
            // Scroll to bottom as new content arrives
            scrollToBottom();
          },
          (error) => {
            // Handle errors
            console.error('Streaming error:', error);
            setError(error);
            setMessages(prevMessages => 
              prevMessages.map(msg => 
                msg.id === aiMessageId
                  ? {
                      ...msg,
                      text: `Error: ${error}`,
                      isStreaming: false
                    }
                  : msg
              )
            );
            setIsProcessing(false);
          },
          async () => {
            // Handle completion
            console.log('Streaming complete');
            setMessages(prevMessages => 
              prevMessages.map(msg => 
                msg.id === aiMessageId
                  ? {
                      ...msg,
                      isStreaming: false
                    }
                  : msg
              )
            );
            setIsProcessing(false);
            
            // Save the chat history
            await saveChatHistory(userMessage.text, fullResponse);
          },
          validDocumentIds
        );
        
        // Store the abort function to cancel streaming if needed
        abortStreamingRef.current = abortStreaming;
      } else {
        // Use regular response for non-local models
        console.log('Using regular response for non-local model');
        
        // Prepare the request payload
        const payload = {
          prompt: userMessage.text,
          operation_type: operationType,
          document_ids: validDocumentIds.length > 0 ? validDocumentIds : undefined
        };
        
        console.log('Sending API request with payload:', payload);
        
        // Send the query to the API using the api service
        console.log('Making API request to chat endpoint');
        const response = await getAIResponse(
          userMessage.text,
          operationType,
          [], // No message history for now
          selectedModel,
          validDocumentIds
        );
        
        console.log('Received API response:', response);
        
        // Queue the AI response for typewriter effect
        typewriterQueueRef.current = {
          text: response,
          messageId: aiMessageId
        };
        
        // Start processing the typewriter queue
        processTypewriterQueue();
        
        // Save the chat history
        await saveChatHistory(userMessage.text, response);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setError(error instanceof Error ? error.message : 'An unknown error occurred');
      
      // Update the loading message to show the error
      setMessages(prevMessages => 
        prevMessages.map(msg => 
          msg.id === aiMessageId
            ? {
                ...msg,
                text: `Error: ${error instanceof Error ? error.message : 'An unknown error occurred'}`,
                isLoading: false
              }
            : msg
        )
      );
      
      setIsProcessing(false);
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  // Clean up on unmount
  useEffect(() => {
    return () => {
      // Clear any pending typewriter timeouts
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      
      // Abort any ongoing streaming
      if (abortStreamingRef.current) {
        abortStreamingRef.current();
      }
    };
  }, []);

  return (
    <div className="flex flex-col h-full">
      {error && (
        <div className="px-4 pt-3">
          <ErrorMessage 
            message={error}
            type="error"
            onClose={() => setError(null)}
          />
        </div>
      )}
      
      {/* Debug button - only visible in development */}
      {process.env.NODE_ENV === 'development' && (
        <div className="px-4 pt-2 flex space-x-2">
          <button
            onClick={async () => {
              try {
                console.log("Checking available documents...");
                console.log("Active PDF IDs:", activePdfIds);
                
                // Check what documents are available
                const response = await api.get('/documents/debug');
                console.log("Available documents:", response.data);
                
                // Set a message with the document info
                const userDocs = response.data.user_documents || [];
                const allDocs = response.data.all_documents || [];
                
                // Format the document IDs that will be sent to the API
                const validDocumentIds = activePdfIds && activePdfIds.length > 0 
                  ? activePdfIds
                      .map(id => {
                        if (typeof id === 'string') {
                          const parsedId = parseInt(id, 10);
                          if (isNaN(parsedId)) {
                            return `${id} (invalid - not a number)`;
                          }
                          return parsedId;
                        }
                        return id;
                      })
                  : [];
                
                const message = `
DEBUG INFORMATION:

User ID: ${response.data.user_id}

Available documents:
- User documents (${userDocs.length}):
${userDocs.map((d: {id: number, filename: string, filepath: string}) => 
  `  ID: ${d.id}, Filename: ${d.filename}, Path: ${d.filepath}`
).join('\n')}

- All documents (${allDocs.length}):
${allDocs.map((d: {id: number, filename: string, filepath: string}) => 
  `  ID: ${d.id}, Filename: ${d.filename}, Path: ${d.filepath}`
).join('\n')}

- Active PDF IDs that will be sent to API: 
${validDocumentIds.length > 0 ? validDocumentIds.join(', ') : 'none'}
                `;
                
                // Add a message to the chat
                setMessages(prevMessages => [
                  ...prevMessages,
                  {
                    id: prevMessages.length + 1,
                    text: message,
                    sender: 'ai',
                    timestamp: new Date()
                  }
                ]);
              } catch (err) {
                console.error("Error checking documents:", err);
                setError("Failed to check available documents");
              }
            }}
            className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded mb-2"
          >
            Debug Documents
          </button>
          
          <button
            onClick={async () => {
              try {
                if (!activePdfIds || activePdfIds.length === 0) {
                  setError("No document IDs available to test");
                  return;
                }
                
                // Format the document IDs that will be sent to the API
                const validDocumentIds = activePdfIds
                  .map(id => typeof id === 'string' ? parseInt(id, 10) : id)
                  .filter(id => !isNaN(id));
                
                if (validDocumentIds.length === 0) {
                  setError("No valid document IDs to test");
                  return;
                }
                
                console.log("Testing document extraction for IDs:", validDocumentIds);
                
                // Add a loading message
                const messageId = messages.length + 1;
                setMessages(prevMessages => [
                  ...prevMessages,
                  {
                    id: messageId,
                    text: `Testing document extraction for IDs: ${validDocumentIds.join(', ')}...`,
                    sender: 'ai',
                    isLoading: true,
                    timestamp: new Date()
                  }
                ]);
                
                // Use the new test-extraction endpoint
                const response = await api.post('/documents/test-extraction', {
                  document_ids: validDocumentIds
                });
                
                console.log("Test document extraction response:", response.data);
                
                // Update the message with the result
                setMessages(prevMessages => 
                  prevMessages.map(msg => 
                    msg.id === messageId
                      ? {
                          ...msg,
                          text: `Document extraction test result:\n\n${
                            response.data.success 
                              ? `Successfully extracted ${response.data.text_length} characters of text.\n\nFirst 500 characters:\n${response.data.text.substring(0, 500)}...`
                              : `Error: ${response.data.error}\n\n${response.data.text}`
                          }`,
                          isLoading: false
                        }
                      : msg
                  )
                );
              } catch (err) {
                console.error("Error testing document extraction:", err);
                setError("Failed to test document extraction");
              }
            }}
            className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded mb-2"
          >
            Test Document Extraction
          </button>
        </div>
      )}
      
      <div className="flex-grow overflow-auto p-4">
        {messages.map((message) => (
          <div 
            key={message.id} 
            className={`mb-4 ${message.sender === 'user' ? 'text-right' : ''}`}
          >
            <div 
              className={`inline-block max-w-[85%] rounded-lg px-4 py-2 ${
                message.sender === 'user' 
                  ? 'bg-navy-blue text-white' 
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {message.isLoading ? (
                <div className="flex items-center justify-center py-2">
                  <Loader2 className="h-5 w-5 animate-spin text-gray-500" />
                </div>
              ) : (
                <p className="text-sm whitespace-pre-wrap">
                  {message.text}
                  {message.isStreaming && (
                    <span className="inline-block w-2 h-4 ml-1 bg-gray-500 animate-pulse"></span>
                  )}
                </p>
              )}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {formatDateTime(message.timestamp)}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="border-t border-gray-200 p-3">
        <div className="flex items-center">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a compliance question..."
            className="flex-grow border border-gray-300 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-navy-blue resize-none text-left"
            rows={2}
            disabled={isProcessing}
          />
          <button 
            onClick={handleSendMessage}
            disabled={inputValue.trim() === '' || isProcessing}
            className={`ml-2 p-2 rounded-full ${
              inputValue.trim() === '' || isProcessing
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
                : 'bg-navy-blue text-white hover:bg-blue-800'
            }`}
          >
            {isProcessing ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-500 flex justify-end">
          <span>
            Using: {selectedModel === 'local-model' ? 'Local LLM' : 'GPT-4o-mini'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default AIChat;
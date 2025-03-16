import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { getAIResponse, getStreamingAIResponse } from '../services/aiService';
import ErrorMessage from '../components/ErrorMessage';
import { useModel } from '../contexts/ModelContext';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { formatDateTime } from '../utils/dateUtils';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

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
  const [cursorPosition, setCursorPosition] = useState({ x: 0, y: 0 });
  const [showCursorCloud, setShowCursorCloud] = useState(false);

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
        
        if (data && data.messages && Array.isArray(data.messages)) {
          // Transform the API response to our message format
          const loadedMessages = data.messages.map((msg: any, index: number) => {
            // Ensure we have a valid timestamp
            let timestamp;
            try {
              timestamp = msg.timestamp ? new Date(msg.timestamp) : new Date();
              // Check if the date is valid
              if (isNaN(timestamp.getTime())) {
                timestamp = new Date(); // Fallback to current time
              }
            } catch (error) {
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
          
          // Replace the default welcome message with the loaded conversation
          setMessages(loadedMessages);
        }
      } catch (err) {
        setError('Failed to load the conversation history. Starting a new conversation instead.');
      } finally {
        setIsProcessing(false);
      }
    };
    
    loadConversation();
  }, [conversationId]);

  // Load initial conversation if available
  useEffect(() => {
    if (initialConversation && Array.isArray(initialConversation) && initialConversation.length > 0) {
      try {
        // Convert the conversation history to the correct format
        const formattedMessages = initialConversation
          .map((msg: any, index: number) => {
            if (!msg || (!msg.content && !msg.text)) {
              return null;
            }
            
            // Ensure we have a valid timestamp
            let timestamp;
            try {
              timestamp = msg.timestamp ? new Date(msg.timestamp) : new Date();
              // Check if the date is valid
              if (isNaN(timestamp.getTime())) {
                timestamp = new Date(); // Fallback to current time
              }
            } catch (error) {
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
        
        if (formattedMessages.length > 0) {
          // Replace the default welcome message with the loaded conversation
          setMessages(formattedMessages);
          setTimeout(scrollToBottom, 100);
        } else {
          setError('Failed to load the conversation. Starting a new conversation instead.');
        }
      } catch (error) {
        setError('Failed to load the conversation. Starting a new conversation instead.');
      }
    } else if (initialQuery && initialQuery.trim() !== '') {
      // If we only have an initial query, set it as the input value
      setInputValue(initialQuery);
    }
  }, [initialConversation, initialQuery]);

  // Auto-send initial query for Continue Conversation
  useEffect(() => {
    if (initialQuery && initialQuery.trim() !== '' && !showFullConversation) {
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
        // Log error but don't show to user
      } else {
        // Log success but don't show to user
      }
    } catch (error) {
      // Log error but don't show to user
    }
  };

  // Track mouse movement
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isProcessing && !isTypingRef.current) {
        setCursorPosition({ x: e.clientX, y: e.clientY });
      }
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [isProcessing]);

  const handleSendMessage = async () => {
    if (inputValue.trim() === '' || isProcessing) return;
    
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
    setShowCursorCloud(true);
    
    try {
      // Ensure document IDs are valid numbers
      const validDocumentIds = activePdfIds && activePdfIds.length > 0 
        ? activePdfIds
            .map(id => {
              if (typeof id === 'string') {
                const parsedId = parseInt(id, 10);
                if (isNaN(parsedId)) {
                  return null;
                }
                return parsedId;
              }
              return id;
            })
            .filter(id => id !== null && id !== undefined)
        : [];
      
      // Check if we should use streaming
      const useStreaming = selectedModel === 'local-model' || !selectedModel.startsWith('gpt-');
      
      if (useStreaming) {
        // Use streaming for local models
        
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
        
        // Hide the cursor cloud when streaming starts
        setShowCursorCloud(false);
        
        let fullResponse = '';
        let responseStarted = false;
        
        // Set up the streaming response handler
        const abortStreaming = getStreamingAIResponse(
          userMessage.text,
          operationType,
          [], // No message history for now
          selectedModel,
          (chunk) => {
            // Update the message with each chunk
            fullResponse += chunk;
            
            // If this is the first chunk with actual content, mark response as started
            if (!responseStarted && chunk.trim() !== '') {
              responseStarted = true;
              
              // Update the message to remove the streaming indicator only when we have content
              setMessages(prevMessages => 
                prevMessages.map(msg => 
                  msg.id === aiMessageId
                    ? {
                        ...msg,
                        text: fullResponse,
                        isStreaming: false
                      }
                    : msg
                )
              );
            } else if (responseStarted) {
              // Regular update without streaming indicator once we've started
              setMessages(prevMessages => 
                prevMessages.map(msg => 
                  msg.id === aiMessageId
                    ? {
                        ...msg,
                        text: fullResponse,
                        isStreaming: false
                      }
                    : msg
                )
              );
            } else {
              // Keep the streaming indicator until we get actual content
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
            }
            
            // Scroll to bottom as new content arrives
            scrollToBottom();
          },
          (error) => {
            // Handle errors
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
        
        // Prepare the request payload
        const payload = {
          prompt: userMessage.text,
          operation_type: operationType,
          document_ids: validDocumentIds.length > 0 ? validDocumentIds : undefined
        };
        
        // Send the query to the API using the api service
        const response = await getAIResponse(
          userMessage.text,
          operationType,
          [], // No message history for now
          selectedModel,
          validDocumentIds
        );
        
        // Hide the cursor cloud when response is received
        setShowCursorCloud(false);
        
        // Update the message with the response (no streaming indicator)
        setMessages(prevMessages => 
          prevMessages.map(msg => 
            msg.id === aiMessageId
              ? {
                  ...msg,
                  text: response,
                  isLoading: false,
                  isStreaming: false
                }
              : msg
          )
        );
        
        // Save the chat history
        await saveChatHistory(userMessage.text, response);
        
        // Mark processing as complete
        setIsProcessing(false);
      }
    } catch (error) {
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
      setShowCursorCloud(false);
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const handleStopResponse = () => {
    // Stop streaming if active
    if (abortStreamingRef.current) {
      abortStreamingRef.current();
      abortStreamingRef.current = null;
    }
    
    // Stop typewriter effect if active
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
      typingTimeoutRef.current = null;
      isTypingRef.current = false;
    }
    
    // Update all streaming messages to non-streaming
    setMessages(prevMessages => 
      prevMessages.map(msg => 
        msg.isStreaming 
          ? { ...msg, isStreaming: false }
          : msg
      )
    );
    
    // Reset processing state
    setIsProcessing(false);
    setShowCursorCloud(false);
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
      
      {/* Cursor-following morphing cloud */}
      {showCursorCloud && (
        <div 
          className="fixed pointer-events-none z-50 w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-500 dark:from-blue-500 dark:to-purple-600 animate-morphing-cloud animate-pulse-glow"
          style={{ 
            left: `${cursorPosition.x}px`, 
            top: `${cursorPosition.y}px`,
            transform: 'translate(-50%, -50%)'
          }}
        />
      )}
      
      <div className="flex-grow overflow-auto p-4 bg-gray-50 dark:bg-gray-800 transition-colors duration-300">
        {messages.map((message) => (
          <div 
            key={message.id} 
            className={`mb-4 ${message.sender === 'user' ? 'text-right' : ''}`}
          >
            <div 
              className={`inline-block max-w-[85%] rounded-lg px-4 py-2 ${
                message.sender === 'user' 
                  ? 'bg-navy-blue text-white dark:bg-blue-700' 
                  : 'bg-white dark:bg-dark-surface text-gray-800 dark:text-gray-200 shadow-sm'
              } transition-colors duration-300`}
            >
              {message.isLoading ? (
                <div className="flex items-center justify-center py-2">
                  <Loader2 className="h-5 w-5 animate-spin text-gray-500 dark:text-gray-400" />
                </div>
              ) : message.sender === 'ai' ? (
                <div className="text-sm markdown-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.text}
                  </ReactMarkdown>
                  {message.isStreaming && (
                    <span className="inline-flex ml-2 align-middle relative h-3 w-3">
                      <span className="absolute inset-0 w-3 h-3 bg-blue-500/40 dark:bg-blue-400/40 rounded-full animate-water-ripple"></span>
                      <span className="absolute inset-0 w-3 h-3 bg-blue-500/30 dark:bg-blue-400/30 rounded-full animate-water-ripple-delay"></span>
                      <span className="absolute inset-0 w-3 h-3 bg-blue-500/20 dark:bg-blue-400/20 rounded-full animate-water-ripple-delay2"></span>
                      <span className="absolute inset-0 w-3 h-3 bg-blue-500 dark:bg-blue-400 rounded-full animate-water-pulse"></span>
                    </span>
                  )}
                </div>
              ) : (
                <p className="text-sm whitespace-pre-wrap">
                  {message.text}
                  {message.isStreaming && (
                    <span className="inline-flex ml-2 align-middle relative h-3 w-3">
                      <span className="absolute inset-0 w-3 h-3 bg-blue-500/40 dark:bg-blue-400/40 rounded-full animate-water-ripple"></span>
                      <span className="absolute inset-0 w-3 h-3 bg-blue-500/30 dark:bg-blue-400/30 rounded-full animate-water-ripple-delay"></span>
                      <span className="absolute inset-0 w-3 h-3 bg-blue-500/20 dark:bg-blue-400/20 rounded-full animate-water-ripple-delay2"></span>
                      <span className="absolute inset-0 w-3 h-3 bg-blue-500 dark:bg-blue-400 rounded-full animate-water-pulse"></span>
                    </span>
                  )}
                </p>
              )}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 transition-colors duration-300">
              {formatDateTime(message.timestamp)}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="border-t border-gray-200 dark:border-gray-700 p-3 bg-white dark:bg-dark-surface transition-colors duration-300">
        <div className="flex items-center">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a compliance question..."
            className="flex-grow border border-gray-300 dark:border-gray-600 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-navy-blue dark:focus:ring-blue-500 resize-none text-left bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 transition-colors duration-300"
            rows={2}
            disabled={isProcessing}
          />
          {isProcessing ? (
            <button 
              onClick={handleStopResponse}
              className="ml-2 p-2 rounded-full bg-red-500 text-white hover:bg-red-600"
              title="Stop response"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="6" y="6" width="12" height="12" />
              </svg>
            </button>
          ) : (
            <button 
              onClick={handleSendMessage}
              disabled={inputValue.trim() === ''}
              className={`ml-2 p-2 rounded-full ${
                inputValue.trim() === ''
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
                  : 'bg-navy-blue text-white hover:bg-blue-800'
              }`}
            >
              <Send className="h-5 w-5" />
            </button>
          )}
        </div>
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 flex justify-end items-center transition-colors duration-300">
          <span>
            Using: {selectedModel === 'local-model' ? 'Local LLM' : 'GPT-4o-mini'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default AIChat;
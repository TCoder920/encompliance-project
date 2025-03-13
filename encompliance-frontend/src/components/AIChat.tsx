import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { getAIResponse } from '../services/aiService';
import ErrorMessage from '../components/ErrorMessage';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  isLoading?: boolean;
}

interface AIChatProps {
  operationType: string;
  selectedModel?: string;
  activePdfIds?: number[];
}

const AIChat: React.FC<AIChatProps> = ({ 
  operationType, 
  selectedModel = 'local-model',
  activePdfIds = []
}) => {
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
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const handleSendMessage = async () => {
    if (inputValue.trim() === '' || isProcessing) return;
    
    // Clear any previous errors
    setError(null);
    
    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };
    
    // Add temporary AI message with loading state
    const loadingMessage: Message = {
      id: messages.length + 2,
      text: '...',
      sender: 'ai',
      timestamp: new Date(),
      isLoading: true
    };
    
    setMessages([...messages, userMessage, loadingMessage]);
    setInputValue('');
    setIsProcessing(true);
    
    // Convert messages to the format expected by the API (plain objects, not class instances)
    const messageHistory = messages
      .filter(msg => !msg.isLoading) // Filter out any loading messages
      .map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.text
      }));
    
    console.log('Sending message history:', JSON.stringify(messageHistory));
    console.log('Active PDF IDs:', activePdfIds);
    
    try {
      // Get AI response
      const response = await getAIResponse(
        inputValue, 
        operationType, 
        messageHistory,
        selectedModel,
        activePdfIds.length > 0 ? activePdfIds : undefined
      );
      
      // Replace loading message with actual response
      setMessages(prevMessages => 
        prevMessages.map(msg => 
          msg.id === loadingMessage.id
            ? {
                ...msg,
                text: response.text,
                isLoading: false
              }
            : msg
        )
      );
      
      // Handle any error returned from the API
      if (response.error) {
        setError(`Error: ${response.error}`);
      }
    } catch (error) {
      console.error('Error getting AI response:', error);
      
      // Replace loading message with error
      setMessages(prevMessages => 
        prevMessages.map(msg => 
          msg.id === loadingMessage.id
            ? {
                ...msg,
                text: 'I apologize, but I encountered an error processing your request. Please try again later.',
                isLoading: false
              }
            : msg
        )
      );
      
      // Set more specific error message for the user
      if (error instanceof Error) {
        if (error.message.includes('network') || error.message.includes('connection')) {
          setError('Failed to connect to the AI service. Please check your network connection and try again.');
        } else if (error.message.includes('timeout')) {
          setError('The AI service took too long to respond. Please try again with a simpler query.');
        } else if (error.message.includes('unauthorized') || error.message.includes('authentication')) {
          setError('Authentication error. Please log out and log back in to refresh your session.');
        } else {
          setError(`Error: ${error.message}`);
        }
      } else {
        setError('An unexpected error occurred. Please try again later.');
      }
    } finally {
      setIsProcessing(false);
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
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
                <p className="text-sm whitespace-pre-wrap">{message.text}</p>
              )}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {formatTime(message.timestamp)}
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
            className="flex-grow border border-gray-300 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-navy-blue resize-none"
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
        <div className="mt-2 text-xs text-gray-500 text-right">
          Using: {selectedModel === 'local-model' ? 'Local LLM' : 'GPT-4o Mini'}
        </div>
      </div>
    </div>
  );
};

export default AIChat;
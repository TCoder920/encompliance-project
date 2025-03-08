import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { getAIResponse, getFallbackResponse } from '../services/aiService';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  isLoading?: boolean;
}

interface AIChatProps {
  operationType: string;
}

const AIChat: React.FC<AIChatProps> = ({ operationType }) => {
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
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const handleSendMessage = async () => {
    if (inputValue.trim() === '' || isProcessing) return;
    
    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };
    
    // Add placeholder for AI response
    const aiPlaceholder: Message = {
      id: messages.length + 2,
      text: '',
      sender: 'ai',
      timestamp: new Date(),
      isLoading: true
    };
    
    setMessages([...messages, userMessage, aiPlaceholder]);
    setInputValue('');
    setIsProcessing(true);
    
    try {
      // Prepare message history for context
      const messageHistory = messages
        .filter(msg => messages.indexOf(msg) > 0) // Skip the welcome message
        .map(msg => ({
          role: msg.sender === 'user' ? 'user' : 'assistant',
          content: msg.text
        }));
      
      // Get response from AI service
      const apiKey = import.meta.env.VITE_OPENAI_API_KEY;
      let response;
      
      if (apiKey) {
        // Use real AI if API key is available
        response = await getAIResponse(inputValue, operationType, messageHistory as any);
      } else {
        // Use fallback responses if no API key
        response = getFallbackResponse(inputValue, operationType);
      }
      
      // Update the placeholder with the actual response
      setMessages(prevMessages => 
        prevMessages.map(msg => 
          msg.id === aiPlaceholder.id 
            ? { ...msg, text: response.text, isLoading: false } 
            : msg
        )
      );
    } catch (error) {
      console.error('Error getting AI response:', error);
      
      // Update placeholder with error message
      setMessages(prevMessages => 
        prevMessages.map(msg => 
          msg.id === aiPlaceholder.id 
            ? { 
                ...msg, 
                text: "I'm sorry, I encountered an error processing your request. Please try again later.", 
                isLoading: false 
              } 
            : msg
        )
      );
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
          {import.meta.env.VITE_OPENAI_API_KEY ? 'Powered by GPT-4' : 'Demo Mode - Limited Responses'}
        </div>
      </div>
    </div>
  );
};

export default AIChat;
import React, { useState } from 'react';
import { Settings, Check, X } from 'lucide-react';
import { useModel } from '../contexts/ModelContext';

const UniversalModelSelector: React.FC = () => {
  const { selectedModel, setSelectedModel } = useModel();
  const [isOpen, setIsOpen] = useState(false);
  
  const models = [
    { id: 'local-model', name: 'Local LLM', description: 'Default local model for compliance questions (running on http://127.0.0.1:1234)' },
    { id: 'gpt-4o-mini', name: 'GPT-4o-mini', description: 'OpenAI model optimized for complex compliance questions (currently inactive)' }
  ];
  
  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };
  
  const handleModelChange = (modelId: string) => {
    setSelectedModel(modelId);
    setIsOpen(false);
  };
  
  return (
    <div className="relative">
      <button
        onClick={toggleMenu}
        className="flex items-center text-gray-600 hover:text-navy-blue focus:outline-none"
        title="AI Model Settings"
      >
        <Settings className="h-5 w-5" />
        <span className="ml-1 text-xs">AI Model</span>
      </button>
      
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg z-50 border border-gray-200">
          <div className="flex justify-between items-center p-3 border-b border-gray-200">
            <h3 className="font-medium text-gray-900">AI Model Settings</h3>
            <button 
              onClick={() => setIsOpen(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          
          <div className="p-3">
            <p className="text-xs text-gray-500 mb-2">
              Select the AI model to use across the application
            </p>
            
            <div className="space-y-2">
              {models.map((model) => (
                <div 
                  key={model.id}
                  className={`flex items-center p-2 rounded cursor-pointer ${
                    selectedModel === model.id ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => handleModelChange(model.id)}
                >
                  <div className={`w-4 h-4 rounded-full border mr-3 flex items-center justify-center ${
                    selectedModel === model.id ? 'border-navy-blue bg-navy-blue' : 'border-gray-400'
                  }`}>
                    {selectedModel === model.id && <Check className="h-3 w-3 text-white" />}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{model.name}</div>
                    <div className="text-xs text-gray-500">{model.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UniversalModelSelector; 
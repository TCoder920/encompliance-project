import React from 'react';
import { Check } from 'lucide-react';

interface AIModelSelectorProps {
  selectedModel: string;
  onModelChange: (model: string) => void;
}

const AIModelSelector: React.FC<AIModelSelectorProps> = ({ selectedModel, onModelChange }) => {
  // Only keeping local-model and gpt-4o-mini as requested
  const models = [
    { id: 'local-model', name: 'Local LLM', description: 'Use a locally hosted LLM for compliance questions' },
    { id: 'gpt-4o-mini', name: 'GPT-4o Mini', description: 'Efficient model for compliance questions' }
  ];

  return (
    <div className="p-4 border-b border-gray-200">
      <h3 className="font-bold text-navy-blue mb-2">AI Model</h3>
      <div className="space-y-2">
        {models.map((model) => (
          <div 
            key={model.id}
            className={`flex items-center p-2 rounded cursor-pointer ${
              selectedModel === model.id ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50'
            }`}
            onClick={() => onModelChange(model.id)}
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
      <div className="mt-3 text-xs text-gray-500">
        Note: 'Local LLM' requires a locally hosted model. 'GPT-4o Mini' requires an OpenAI API key.
      </div>
    </div>
  );
};

export default AIModelSelector;
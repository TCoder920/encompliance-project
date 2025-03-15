import React, { useState, useEffect } from 'react';
import { Settings, Check, X, Save } from 'lucide-react';
import { useModel } from '../contexts/ModelContext';
import api from '../services/api';

const UniversalModelSelector: React.FC = () => {
  const { selectedModel, setSelectedModel, modelSettings, updateModelSettings } = useModel();
  const [isOpen, setIsOpen] = useState(false);
  const [localSettings, setLocalSettings] = useState({
    localModelUrl: '',
    openaiApiKey: '',
    anthropicApiKey: '',
    customModelUrl: '',
    customApiKey: ''
  });
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState('');
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  // Load settings when component mounts
  useEffect(() => {
    if (modelSettings) {
      setLocalSettings({
        localModelUrl: modelSettings.localModelUrl || 'http://127.0.0.1:1234',
        openaiApiKey: modelSettings.openaiApiKey || '',
        anthropicApiKey: modelSettings.anthropicApiKey || '',
        customModelUrl: modelSettings.customModelUrl || '',
        customApiKey: modelSettings.customApiKey || ''
      });
    }
  }, [modelSettings]);
  
  const models = [
    { id: 'local-model', name: 'Local LLM', description: 'Default local model for compliance questions' },
    { id: 'gpt-4o-mini', name: 'GPT-4o-mini', description: 'OpenAI model optimized for complex compliance questions' },
    { id: 'claude-3-opus', name: 'Claude 3 Opus', description: 'Anthropic\'s most capable model for detailed analysis' },
    { id: 'custom-model', name: 'Custom Model', description: 'Use a custom model with your own API endpoint' }
  ];
  
  const toggleMenu = () => {
    setIsOpen(!isOpen);
    // Reset success/error messages when opening/closing
    setSaveSuccess(false);
    setSaveError('');
  };
  
  const handleModelChange = (modelId: string) => {
    setSelectedModel(modelId);
  };
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setLocalSettings(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Reset success/error messages when user makes changes
    setSaveSuccess(false);
    setSaveError('');
  };
  
  const saveSettings = async () => {
    try {
      setIsSaving(true);
      setSaveError('');
      setSaveSuccess(false);
      
      // Update settings in context
      updateModelSettings(localSettings);
      
      // Save settings to backend
      await api.post('/settings/model', {
        local_model_url: localSettings.localModelUrl,
        openai_api_key: localSettings.openaiApiKey,
        anthropic_api_key: localSettings.anthropicApiKey,
        custom_model_url: localSettings.customModelUrl,
        custom_api_key: localSettings.customApiKey
      });
      
      setSaveSuccess(true);
    } catch (error) {
      console.error('Error saving model settings:', error);
      setSaveError('Failed to save settings. Please try again.');
    } finally {
      setIsSaving(false);
    }
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
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg z-50 border border-gray-200">
          <div className="flex justify-between items-center p-3 border-b border-gray-200">
            <h3 className="font-medium text-gray-900">AI Model Settings</h3>
            <button 
              onClick={toggleMenu}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          
          <div className="p-3">
            <p className="text-xs text-gray-500 mb-2">
              Select the AI model to use across the application
            </p>
            
            <div className="space-y-2 mb-4">
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
            
            <div className="border-t border-gray-200 pt-3 mt-3">
              <h4 className="font-medium text-gray-900 mb-2">API Configuration</h4>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-gray-700 mb-1">Local Model URL</label>
                  <input
                    type="text"
                    name="localModelUrl"
                    value={localSettings.localModelUrl}
                    onChange={handleInputChange}
                    placeholder="http://127.0.0.1:1234"
                    className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                  />
                  <p className="text-xs text-gray-500 mt-1">URL for your local LLM server</p>
                </div>
                
                <div>
                  <label className="block text-xs text-gray-700 mb-1">OpenAI API Key</label>
                  <input
                    type="password"
                    name="openaiApiKey"
                    value={localSettings.openaiApiKey}
                    onChange={handleInputChange}
                    placeholder="sk-..."
                    className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                  />
                  <p className="text-xs text-gray-500 mt-1">Required for GPT models</p>
                </div>
                
                <div>
                  <label className="block text-xs text-gray-700 mb-1">Anthropic API Key</label>
                  <input
                    type="password"
                    name="anthropicApiKey"
                    value={localSettings.anthropicApiKey}
                    onChange={handleInputChange}
                    placeholder="sk-ant-..."
                    className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                  />
                  <p className="text-xs text-gray-500 mt-1">Required for Claude models</p>
                </div>
                
                <div>
                  <label className="block text-xs text-gray-700 mb-1">Custom Model URL</label>
                  <input
                    type="text"
                    name="customModelUrl"
                    value={localSettings.customModelUrl}
                    onChange={handleInputChange}
                    placeholder="https://api.example.com/v1/chat/completions"
                    className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                  />
                </div>
                
                <div>
                  <label className="block text-xs text-gray-700 mb-1">Custom API Key</label>
                  <input
                    type="password"
                    name="customApiKey"
                    value={localSettings.customApiKey}
                    onChange={handleInputChange}
                    placeholder="Your API key"
                    className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                  />
                </div>
                
                {saveError && (
                  <div className="text-xs text-red-600 mt-2">{saveError}</div>
                )}
                
                {saveSuccess && (
                  <div className="text-xs text-green-600 mt-2">Settings saved successfully!</div>
                )}
                
                <button
                  onClick={saveSettings}
                  disabled={isSaving}
                  className="w-full mt-2 flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-navy-blue hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-navy-blue disabled:opacity-50"
                >
                  {isSaving ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Save Settings
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UniversalModelSelector; 
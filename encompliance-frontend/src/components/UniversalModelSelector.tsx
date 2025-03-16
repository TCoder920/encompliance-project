import React, { useState, useEffect, useRef } from 'react';
import { Settings, Check, X, Save, Zap } from 'lucide-react';
import { useModel } from '../contexts/ModelContext';
import api from '../services/api';

const UniversalModelSelector: React.FC = () => {
  const { selectedModel, setSelectedModel, modelSettings, updateModelSettings } = useModel();
  const [isOpen, setIsOpen] = useState(false);
  const modalRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [localSettings, setLocalSettings] = useState({
    apiKey: '',
    provider: 'auto',
    otherApiUrl: '',
    localModelUrl: '',
    openaiApiKey: '',
    anthropicApiKey: '',
    customModelUrl: '',
    customApiKey: ''
  });
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState('');
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [testConnectionResult, setTestConnectionResult] = useState<{success: boolean, message: string} | null>(null);
  
  // Load settings when component mounts
  useEffect(() => {
    if (modelSettings) {
      setLocalSettings({
        apiKey: modelSettings.apiKey || '',
        provider: modelSettings.provider || 'auto',
        otherApiUrl: modelSettings.otherApiUrl || '',
        localModelUrl: modelSettings.localModelUrl || 'http://127.0.0.1:1234',
        openaiApiKey: modelSettings.openaiApiKey || '',
        anthropicApiKey: modelSettings.anthropicApiKey || '',
        customModelUrl: modelSettings.customModelUrl || '',
        customApiKey: modelSettings.customApiKey || ''
      });
    }
  }, [modelSettings]);
  
  // Add click outside listener to close modal
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (isOpen && 
          modalRef.current && 
          !modalRef.current.contains(event.target as Node) &&
          buttonRef.current && 
          !buttonRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSaveSuccess(false);
        setSaveError('');
        setTestConnectionResult(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);
  
  const models = [
    { id: 'local-model', name: 'Local LLM', description: 'Use a locally hosted language model' },
    { id: 'cloud-model', name: 'Cloud LLM', description: 'Use a cloud-based language model (OpenAI, Claude, Gemini)' }
  ];
  
  const providers = [
    { id: 'auto', name: 'Auto-Detect', description: 'Automatically detect the provider based on API key format' },
    { id: 'openai', name: 'OpenAI', description: 'Use OpenAI models (GPT-4, GPT-3.5, etc.)' },
    { id: 'anthropic', name: 'Anthropic', description: 'Use Anthropic models (Claude)' },
    { id: 'google', name: 'Google', description: 'Use Google models (Gemini)' },
    { id: 'other', name: 'Other', description: 'Use a custom API provider not listed above' }
  ];
  
  const toggleMenu = () => {
    setIsOpen(!isOpen);
    // Reset success/error messages when opening/closing
    setSaveSuccess(false);
    setSaveError('');
    setTestConnectionResult(null);
  };
  
  const handleModelChange = (modelId: string) => {
    setSelectedModel(modelId);
    // Reset test connection result when changing model
    setTestConnectionResult(null);
  };
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setLocalSettings(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Reset success/error messages when user makes changes
    setSaveSuccess(false);
    setSaveError('');
    setTestConnectionResult(null);
  };
  
  const testConnection = async () => {
    try {
      setIsTestingConnection(true);
      setTestConnectionResult(null);
      
      if (selectedModel === 'local-model') {
        // Test connection to local LLM using the backend API
        try {
          const response = await api.post('/chat/test-connection', {
            is_local: true,
            local_model_url: localSettings.localModelUrl
          });
          
          if (response.data.success) {
            setTestConnectionResult({
              success: true,
              message: `Successfully connected to local LLM at ${localSettings.localModelUrl}`
            });
          } else {
            setTestConnectionResult({
              success: false,
              message: response.data.error || 'Failed to connect to local LLM'
            });
          }
        } catch (error) {
          console.error('Error testing local connection:', error);
          setTestConnectionResult({
            success: false,
            message: 'Failed to connect to local LLM. Make sure the server is running and accessible.'
          });
        }
      } else {
        // Test connection to cloud LLM
        const response = await api.post('/chat/test-connection', {
          api_key: localSettings.apiKey,
          provider: localSettings.provider,
          other_api_url: localSettings.provider === 'other' ? localSettings.otherApiUrl : undefined
        });
        
        if (response.data.success) {
          setTestConnectionResult({
            success: true,
            message: `Successfully connected to ${response.data.provider} API!`
          });
        } else {
          setTestConnectionResult({
            success: false,
            message: response.data.error || 'Unknown error testing connection'
          });
        }
      }
    } catch (error) {
      console.error('Error testing connection:', error);
      setTestConnectionResult({
        success: false,
        message: 'Failed to test connection. Please check your settings and try again.'
      });
    } finally {
      setIsTestingConnection(false);
    }
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
        api_key: localSettings.apiKey,
        provider: localSettings.provider,
        other_api_url: localSettings.otherApiUrl,
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
        ref={buttonRef}
        onClick={toggleMenu}
        className="flex items-center text-gray-600 dark:text-gray-300 hover:text-navy-blue dark:hover:text-blue-400 focus:outline-none"
        title="AI Model Settings"
      >
        <Settings className="h-5 w-5" />
        <span className="ml-1 text-xs">AI Model</span>
      </button>
      
      {isOpen && (
        <div 
          ref={modalRef}
          className="absolute right-0 mt-2 w-80 bg-white dark:bg-dark-surface rounded-md shadow-lg z-50 border border-gray-200 dark:border-gray-700"
        >
          <div className="flex justify-between items-center p-3 border-b border-gray-200 dark:border-gray-700">
            <h3 className="font-medium text-gray-900 dark:text-white">AI Model Settings</h3>
            <button 
              onClick={toggleMenu}
              className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          
          <div className="p-3">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
              Select where to run the AI model
            </p>
            
            <div className="space-y-2 mb-4">
              {models.map((model) => (
                <div 
                  key={model.id}
                  className={`flex items-center p-2 rounded cursor-pointer ${
                    selectedModel === model.id || (model.id === 'cloud-model' && selectedModel !== 'local-model') 
                      ? 'bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700' 
                      : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                  }`}
                  onClick={() => handleModelChange(model.id)}
                >
                  <div className={`w-4 h-4 rounded-full border mr-3 flex items-center justify-center ${
                    selectedModel === model.id || (model.id === 'cloud-model' && selectedModel !== 'local-model')
                      ? 'border-navy-blue dark:border-blue-500 bg-navy-blue dark:bg-blue-600' 
                      : 'border-gray-400 dark:border-gray-600'
                  }`}>
                    {(selectedModel === model.id || (model.id === 'cloud-model' && selectedModel !== 'local-model')) && 
                      <Check className="h-3 w-3 text-white" />
                    }
                  </div>
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">{model.name}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">{model.description}</div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="border-t border-gray-200 dark:border-gray-700 pt-3 mt-3">
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">API Configuration</h4>
              
              <div className="space-y-3">
                {selectedModel !== 'local-model' && (
                  <>
                    <div>
                      <label className="block text-xs text-gray-700 dark:text-gray-300 mb-1">API Key</label>
                      <input
                        type="password"
                        name="apiKey"
                        value={localSettings.apiKey}
                        onChange={handleInputChange}
                        placeholder="Enter your API key"
                        className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded text-black dark:text-white dark:bg-gray-700"
                      />
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Your LLM provider API key (OpenAI, Claude, Gemini)</p>
                    </div>
                    
                    <div>
                      <label className="block text-xs text-gray-700 dark:text-gray-300 mb-1">Provider</label>
                      <select
                        name="provider"
                        value={localSettings.provider}
                        onChange={handleInputChange}
                        className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded text-black dark:text-white dark:bg-gray-700"
                      >
                        {providers.map(provider => (
                          <option key={provider.id} value={provider.id}>
                            {provider.name}
                          </option>
                        ))}
                      </select>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {providers.find(p => p.id === localSettings.provider)?.description || 'Select your LLM provider'}
                      </p>
                    </div>
                    
                    {localSettings.provider === 'other' && (
                      <div>
                        <label className="block text-xs text-gray-700 dark:text-gray-300 mb-1">Custom API URL</label>
                        <input
                          type="text"
                          name="otherApiUrl"
                          value={localSettings.otherApiUrl}
                          onChange={handleInputChange}
                          placeholder="https://api.example.com/v1"
                          className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded text-black dark:text-white dark:bg-gray-700"
                        />
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">URL for your custom API provider (OpenAI-compatible)</p>
                      </div>
                    )}
                  </>
                )}
                
                {selectedModel === 'local-model' && (
                  <div>
                    <label className="block text-xs text-gray-700 dark:text-gray-300 mb-1">Local Model URL</label>
                    <input
                      type="text"
                      name="localModelUrl"
                      value={localSettings.localModelUrl}
                      onChange={handleInputChange}
                      placeholder="http://127.0.0.1:1234"
                      className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded text-black dark:text-white dark:bg-gray-700"
                    />
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">URL for your local LLM server</p>
                  </div>
                )}
                
                <div>
                  <button
                    onClick={testConnection}
                    disabled={isTestingConnection || 
                      (selectedModel !== 'local-model' && (!localSettings.apiKey || (localSettings.provider === 'other' && !localSettings.otherApiUrl))) ||
                      (selectedModel === 'local-model' && !localSettings.localModelUrl)
                    }
                    className="w-full mt-1 flex justify-center items-center py-1 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 dark:bg-green-700 dark:hover:bg-green-600"
                  >
                    {isTestingConnection ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Testing...
                      </>
                    ) : (
                      <>
                        <Zap className="h-4 w-4 mr-2" />
                        Test Connection
                      </>
                    )}
                  </button>
                  
                  {testConnectionResult && (
                    <div className={`text-xs mt-2 ${testConnectionResult.success ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                      {testConnectionResult.message}
                    </div>
                  )}
                </div>
                
                {saveError && (
                  <div className="text-xs text-red-600 dark:text-red-400 mt-2">{saveError}</div>
                )}
                
                {saveSuccess && (
                  <div className="text-xs text-green-600 dark:text-green-400 mt-2">Settings saved successfully!</div>
                )}
                
                <button
                  onClick={saveSettings}
                  disabled={isSaving || (localSettings.provider === 'other' && !localSettings.otherApiUrl)}
                  className="w-full mt-2 flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-navy-blue dark:bg-blue-700 hover:bg-blue-800 dark:hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-navy-blue dark:focus:ring-blue-500 disabled:opacity-50"
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
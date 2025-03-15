import React, { createContext, useState, useContext, useEffect } from 'react';

interface ModelSettings {
  localModelUrl: string;
  openaiApiKey: string;
  anthropicApiKey: string;
  customModelUrl: string;
  customApiKey: string;
}

interface ModelContextType {
  selectedModel: string;
  setSelectedModel: (model: string) => void;
  modelSettings: ModelSettings;
  updateModelSettings: (settings: ModelSettings) => void;
}

const defaultSettings: ModelSettings = {
  localModelUrl: 'http://127.0.0.1:1234',
  openaiApiKey: '',
  anthropicApiKey: '',
  customModelUrl: '',
  customApiKey: ''
};

const ModelContext = createContext<ModelContextType | undefined>(undefined);

export const ModelProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  // Initialize with the stored model or default to local-model
  const [selectedModel, setSelectedModel] = useState<string>(() => {
    const storedModel = localStorage.getItem('selectedAIModel');
    return storedModel || 'local-model';
  });
  
  // Initialize with stored settings or defaults
  const [modelSettings, setModelSettings] = useState<ModelSettings>(() => {
    const storedSettings = localStorage.getItem('modelSettings');
    return storedSettings ? JSON.parse(storedSettings) : defaultSettings;
  });

  // Update localStorage when model changes
  useEffect(() => {
    localStorage.setItem('selectedAIModel', selectedModel);
  }, [selectedModel]);
  
  // Update localStorage when settings change
  useEffect(() => {
    localStorage.setItem('modelSettings', JSON.stringify(modelSettings));
  }, [modelSettings]);
  
  const updateModelSettings = (settings: ModelSettings) => {
    setModelSettings(settings);
  };

  return (
    <ModelContext.Provider value={{ 
      selectedModel, 
      setSelectedModel,
      modelSettings,
      updateModelSettings
    }}>
      {children}
    </ModelContext.Provider>
  );
};

export const useModel = () => {
  const context = useContext(ModelContext);
  if (context === undefined) {
    throw new Error('useModel must be used within a ModelProvider');
  }
  return context;
}; 
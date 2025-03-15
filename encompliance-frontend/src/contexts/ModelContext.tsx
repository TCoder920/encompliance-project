import React, { createContext, useState, useContext, useEffect } from 'react';

interface ModelContextType {
  selectedModel: string;
  setSelectedModel: (model: string) => void;
}

const ModelContext = createContext<ModelContextType | undefined>(undefined);

export const ModelProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  // Initialize with the stored model or default to local-model
  const [selectedModel, setSelectedModel] = useState<string>(() => {
    const storedModel = localStorage.getItem('selectedAIModel');
    return storedModel || 'local-model';
  });

  // Update localStorage when model changes
  useEffect(() => {
    localStorage.setItem('selectedAIModel', selectedModel);
  }, [selectedModel]);

  return (
    <ModelContext.Provider value={{ 
      selectedModel, 
      setSelectedModel 
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
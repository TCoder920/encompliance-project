import React from 'react';
import App from './App';

// Simple wrapper component to avoid direct imports in main.tsx
const EntryPoint: React.FC = () => {
  return <App />;
};

export default EntryPoint; 
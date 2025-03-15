import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import EntryPoint from './EntryPoint';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <EntryPoint />
  </StrictMode>
);

/**
 * Debug utilities for encompliance app
 * 
 * This file contains utilities to help diagnose and fix common issues:
 * 1. Authentication problems
 * 2. Navigation/nesting issues
 * 3. API connectivity issues
 */

// Check if token exists and is valid format
export const checkAuthToken = (): { exists: boolean; valid: boolean; token?: string } => {
  const token = localStorage.getItem('token');
  console.log('Auth token check:', token ? 'Found token' : 'No token found');
  
  if (!token) {
    return { exists: false, valid: false };
  }
  
  // Basic check if token looks like a JWT (3 parts separated by dots)
  const parts = token.split('.');
  const valid = parts.length === 3;
  
  return { 
    exists: true, 
    valid, 
    token: token.substring(0, 15) + '...' // Only show beginning for security
  };
};

// Reset token if needed (for resolving auth issues)
export const resetAuthToken = (): void => {
  localStorage.removeItem('token');
  console.log('Auth token has been reset');
};

// Check for and fix nested routing issues
export const checkAndFixRouting = (currentPage: string): string => {
  // If we detect a nested page pattern, fix it
  if (currentPage.includes('/')) {
    // Handle special cases that are expected to have a slash
    if (currentPage.startsWith('aiChat/') || currentPage === 'documentViewer') {
      return currentPage;
    }
    
    // For other nested patterns, extract the last segment
    const parts = currentPage.split('/');
    const fixedPage = parts[parts.length - 1];
    console.log(`Fixed nested routing: ${currentPage} → ${fixedPage}`);
    return fixedPage;
  }
  
  return currentPage;
};

// Log API request for debugging
export const logApiRequest = (url: string, method: string, hasToken: boolean): void => {
  console.log(`API ${method} request to ${url} ${hasToken ? 'with' : 'without'} token`);
};

// Check if we're in a nested component situation
export const checkForNestedComponents = (): void => {
  // Count instances of certain components that should only appear once
  const headers = document.querySelectorAll('header').length;
  const footers = document.querySelectorAll('footer').length;
  const dashboards = document.querySelectorAll('h1').length;
  
  console.log(`Component nesting check: Headers=${headers}, Footers=${footers}, H1s=${dashboards}`);
  
  if (headers > 1 || footers > 1) {
    console.warn('Possible component nesting detected! Multiple headers or footers found.');
  }
};

// Initialize debug tools
export const initDebugTools = (): void => {
  console.log('Encompliance Debug Tools Activated');
  
  // Add to window for console access
  (window as any).encDebug = {
    checkAuthToken,
    resetAuthToken,
    checkAndFixRouting,
    checkForNestedComponents,
  };
  
  console.log('Debug tools available in console via: window.encDebug');
}; 
import axios from 'axios';
import { logApiRequest } from '../debug';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Using Bearer token authentication instead of cookies
  timeout: 60000, // Increased timeout for PDF processing
});

// Add request interceptor to include auth token in all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      // Add token to both standard Authorization header and custom x-token header
      config.headers.Authorization = `Bearer ${token}`;
      config.headers['x-token'] = token;
    }
    
    // Debug log (remove in production)
    const url = config.url || '';
    const method = config.method?.toUpperCase() || 'UNKNOWN';
    logApiRequest(url, method, !!token);
    console.log(`Request headers:`, config.headers);
    
    return config;
  },
  (error) => {
    console.error('API Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => {
    // Debug log (remove in production)
    console.log(`API Response from ${response.config.url}: ${response.status}`);
    
    // Special handling for document list response
    if (response.config.url?.includes('/documents/list')) {
      console.log('Document list response received:', response.data);
      
      // Check if the documents array exists
      if (!response.data?.documents) {
        console.warn('Document list response missing documents array:', response.data);
      } else if (response.data.documents.length === 0) {
        console.warn('Document list returned empty array');
      }
    }
    
    return response;
  },
  async (error) => {
    // Debug log with full details for debugging purposes
    console.error(`API Error from ${error.config?.url}:`, error);
    console.error('Full error details:', {
      status: error.response?.status,
      data: error.response?.data,
      headers: error.response?.headers,
      config: error.config
    });
    
    // Special handling for document-related errors
    if (error.config?.url?.includes('/documents/')) {
      console.error('Document API error:', error.response?.data?.detail || error.message);
    }
    
    const originalRequest = error.config;
    
    // If error is 401 and not a retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Mark as retry
      originalRequest._retry = true;
      
      try {
        console.log('Attempting to refresh token...');
        // Try to refresh the token
        const refreshResponse = await axios.post(`${baseURL}/refresh-token`, {}, {
          withCredentials: false,
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'x-token': localStorage.getItem('token'),
          }
        });
        
        if (refreshResponse.data.access_token) {
          // Save the new token
          const newToken = refreshResponse.data.access_token;
          localStorage.setItem('token', newToken);
          console.log('Token refreshed successfully');
          
          // Update the Authorization header
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          originalRequest.headers['x-token'] = newToken;
          
          // Retry the original request
          return api(originalRequest);
        }
      } catch (refreshError) {
        // If refresh fails, clear the token and let the app handle redirection
        console.error('Token refresh failed:', refreshError);
        localStorage.removeItem('token');
        
        // Dispatch an event that auth components can listen for
        window.dispatchEvent(new CustomEvent('auth-token-expired'));
      }
    }
    
    // For CORS errors, provide a more helpful message
    if (error.message === 'Network Error') {
      console.error('CORS or network error detected');
      error.isCorsProblem = true;
    }
    
    return Promise.reject(error);
  }
);

// Create special versions of API methods for auth
export const authApi = {
  get: async (url: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${baseURL}${url}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'x-token': token || '',
        },
      });
      
      if (!response.ok) throw new Error(`HTTP error ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Auth API error:', error);
      throw error;
    }
  },
  
  // Special method for getting user info that tries multiple approaches
  getUserInfo: async () => {
    console.log('Attempting to fetch user info');
    const token = localStorage.getItem('token');
    
    // First try the user-info endpoint that has explicit CORS handling
    try {
      console.log('Trying /users/user-info endpoint');
      const response = await fetch(`${baseURL}/users/user-info`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'x-token': token || '',
        },
        mode: 'cors',
      });
      
      if (response.ok) {
        console.log('Successfully fetched user from /users/user-info');
        return await response.json();
      }
      console.log(`/users/user-info failed with status: ${response.status}`);
    } catch (error) {
      console.error('Error fetching from /users/user-info:', error);
    }
    
    // Fall back to the standard endpoint
    try {
      console.log('Trying /users/me endpoint');
      const response = await fetch(`${baseURL}/users/me`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'x-token': token || '',
        },
        mode: 'cors',
      });
      
      if (response.ok) {
        console.log('Successfully fetched user from /users/me');
        return await response.json();
      }
      console.log(`/users/me failed with status: ${response.status}`);
    } catch (error) {
      console.error('Error fetching from /users/me:', error);
    }
    
    // If all direct fetch attempts fail, try the axios instance
    try {
      console.log('Trying axios api instance');
      const response = await api.get('/users/me');
      console.log('Successfully fetched user with axios');
      return response.data;
    } catch (error) {
      console.error('All user info fetch attempts failed:', error);
      throw error;
    }
  }
};

export default api; 
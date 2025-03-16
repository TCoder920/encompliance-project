import axios from 'axios';

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
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => {
    // Special handling for document list response
    if (response.config.url?.includes('/documents/list')) {
      // Check if the documents array exists
      if (!response.data?.documents) {
        // If not, try to normalize the response
        if (Array.isArray(response.data)) {
          response.data = { documents: response.data };
        } else if (response.data && typeof response.data === 'object') {
          response.data = { documents: [] };
        }
      }
      
      // Ensure documents is at least an empty array
      if (!response.data.documents) {
        response.data.documents = [];
      }
    }
    
    return response;
  },
  async (error) => {
    // Special handling for document-related errors
    if (error.config?.url?.includes('/documents/')) {
      // Add a more user-friendly message
      error.userMessage = 'There was a problem with your document. Please try again.';
    }
    
    // Handle 401 Unauthorized errors (expired token)
    if (error.response?.status === 401) {
      // Only try to refresh if we have a token
      if (localStorage.getItem('token')) {
        // Store the original request to retry it
        const originalRequest = error.config;
        
        // Prevent infinite loops
        if (!originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            // Try to refresh the token
            const refreshResponse = await axios.post(`${baseURL}/refresh-token`, {}, {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'x-token': localStorage.getItem('token'),
              }
            });
            
            // If successful, update the token
            if (refreshResponse.status === 200) {
              const newToken = refreshResponse.data.access_token;
              localStorage.setItem('token', newToken);
              
              // Update the Authorization header
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              originalRequest.headers['x-token'] = newToken;
              
              // Retry the original request
              return axios(originalRequest);
            }
          } catch (refreshError) {
            // If refresh fails, clear the token and let the app handle redirection
            localStorage.removeItem('token');
          }
        }
      }
    }
    
    // For CORS errors, provide a more helpful message
    if (error.message === 'Network Error') {
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
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    // First try the user-info endpoint that has explicit CORS handling
    try {
      const response = await fetch(`${baseURL}/users/user-info`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'x-token': token,
        }
      });
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      // Continue to next method
    }
    
    // Fall back to the standard endpoint
    try {
      const response = await fetch(`${baseURL}/users/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'x-token': token,
        }
      });
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      // Continue to next method
    }
    
    // If all direct fetch attempts fail, try the axios instance
    try {
      const response = await api.get('/users/me');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get user info after multiple attempts');
    }
  }
};

export default api; 
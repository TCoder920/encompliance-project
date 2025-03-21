import React, { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '../services/authService';
import { userService, UserData } from '../services/userService';
import axios from 'axios';

interface AuthContextType {
  isAuthenticated: boolean;
  user: UserData | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (data: any) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkAuth = async () => {
      if (authService.isAuthenticated()) {
        setIsAuthenticated(true);
        try {
          const userData = await userService.getCurrentUser();
          setUser(userData);
        } catch (err) {
          handleError(err, 'Unable to load user profile. Please try logging in again.');
          authService.removeToken();
          setIsAuthenticated(false);
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const handleError = (err: unknown, defaultMessage: string) => {
    console.error('Auth error:', err);
    
    if (axios.isAxiosError(err)) {
      // Handle Axios errors
      if (err.response) {
        // Server responded with an error status
        if (err.response.status === 401) {
          setError('Your session has expired. Please login again.');
        } else if (err.response.status === 404) {
          setError('The requested resource was not found. Our team has been notified.');
        } else if (err.response.data && err.response.data.detail) {
          setError(err.response.data.detail);
        } else {
          setError(`Error ${err.response.status}: ${defaultMessage}`);
        }
      } else if (err.request) {
        // Request was made but no response received
        setError('Unable to connect to the server. Please check your internet connection and try again.');
      } else {
        setError(defaultMessage);
      }
    } else if (err instanceof Error) {
      setError(err.message);
    } else {
      setError(defaultMessage);
    }
  };

  const clearError = () => {
    setError(null);
  };

  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log("Attempting login with:", { email });
      const response = await authService.login({ email, password });
      
      if (response && response.access_token) {
        console.log("Received token, setting in localStorage");
        authService.setToken(response.access_token);
        
        // Set authenticated immediately to improve perceived performance
        setIsAuthenticated(true);
        
        // Get user data
        try {
          console.log("Attempting to fetch user data");
          const userData = await userService.getCurrentUser();
          setUser(userData);
          console.log("User data loaded successfully:", userData);
        } catch (userErr) {
          console.error('Error fetching user data:', userErr);
          // We're still authenticated even if user data fetch fails
          // Do not change isAuthenticated state
          
          // Create minimal user data
          setUser({
            id: 0,
            email: email,
            full_name: '',
            operation_name: '',
            subscription_status: 'active',
            is_active: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            last_login: new Date().toISOString()
          });
          
          console.log("Authentication successful, using minimal user data");
        }
      } else {
        setError('Login failed. Please check your credentials and try again.');
        setIsAuthenticated(false);
      }
    } catch (err) {
      console.error("Login error:", err);
      handleError(err, 'Login failed. Please check your credentials and try again.');
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const signup = async (data: any) => {
    try {
      setError(null);
      const response = await authService.signup(data);
      
      // Store the token and set authenticated state
      authService.setToken(response.access_token);
      setIsAuthenticated(true);
      
      // Add a small delay to ensure token is properly set before fetching user data
      await new Promise(resolve => setTimeout(resolve, 500));
      
      try {
        const userData = await userService.getCurrentUser();
        setUser(userData);
        console.log("User profile loaded successfully after signup");
      } catch (profileErr) {
        console.log('Profile fetch error, but signup was successful:', profileErr);
        // Create a minimal user object from the signup data
        setUser({
          id: 0, // Will be updated on next successful fetch
          email: data.email,
          full_name: data.full_name || '',
          operation_name: data.operation_name || '',
          operation_type: data.operation_type || '',
          state: data.state || '',
          phone_number: data.phone_number || '',
          subscription_status: 'active',
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          last_login: new Date().toISOString()
        });
        console.log("Using minimal user data after signup");
      }
    } catch (err) {
      handleError(err, 'Signup failed. Please try again or contact support.');
      throw err; // Re-throw to allow component to handle it
    }
  };

  const logout = () => {
    authService.removeToken();
    setIsAuthenticated(false);
    setUser(null);
    setError(null);
  };

  return (
    <AuthContext.Provider value={{ 
      isAuthenticated, 
      user, 
      loading, 
      error,
      login, 
      signup, 
      logout,
      clearError
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 
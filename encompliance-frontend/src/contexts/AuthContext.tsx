import React, { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '../services/authService';
import { userService, UserData } from '../services/userService';

interface AuthContextType {
  isAuthenticated: boolean;
  user: UserData | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (data: any) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const checkAuth = async () => {
      if (authService.isAuthenticated()) {
        setIsAuthenticated(true);
        try {
          const userData = await userService.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error('Error fetching user data:', error);
          authService.removeToken();
          setIsAuthenticated(false);
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authService.login({ email, password });
    authService.setToken(response.access_token);
    setIsAuthenticated(true);
    const userData = await userService.getCurrentUser();
    setUser(userData);
  };

  const signup = async (data: any) => {
    const response = await authService.signup(data);
    authService.setToken(response.access_token);
    setIsAuthenticated(true);
    const userData = await userService.getCurrentUser();
    setUser(userData);
  };

  const logout = () => {
    authService.removeToken();
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, loading, login, signup, logout }}>
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
import React, { useState, useEffect } from 'react';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import ErrorMessage from '../components/ErrorMessage';
import { themeClasses } from '../utils/themeUtils';

interface LoginPageProps {
  navigateTo: (page: string) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ navigateTo }) => {
  const { login, error: authError, clearError } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  
  // Clear errors when component unmounts
  useEffect(() => {
    return () => {
      clearError();
    };
  }, [clearError]);
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Clear errors when user starts typing
    if (localError) setLocalError(null);
    if (authError) clearError();
  };
  
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setIsSubmitting(true);
      setLocalError(null);
      
      await login(formData.email, formData.password);
      
      // Redirect to dashboard on successful login
      navigateTo('dashboard');
    } catch (err) {
      // If there's an error, we don't need to set local error
      // because the AuthContext will handle it
      console.error('Login error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const isFormValid = () => {
    return formData.email.trim() !== '' && formData.password.trim() !== '';
  };
  
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };
  
  return (
    <div className={`container mx-auto px-4 py-12 max-w-md ${themeClasses.layout.container}`}>
      <div className={`rounded-lg shadow-lg p-8 ${themeClasses.bg.primary} ${themeClasses.border.primary} border`}>
        <h1 className={`text-3xl font-bold mb-6 text-center font-times ${themeClasses.text.primary}`}>Login to Your Account</h1>
        
        {localError && (
          <ErrorMessage 
            message={localError}
            type="error"
            onClose={() => setLocalError(null)}
          />
        )}
        
        {authError && (
          <ErrorMessage 
            message={authError}
            type="error"
            onClose={clearError}
          />
        )}
        
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label htmlFor="email" className={`block text-sm font-medium mb-1 ${themeClasses.text.secondary}`}>Email Address</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Mail className={`h-5 w-5 ${themeClasses.text.muted}`} />
              </div>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className={`pl-10 block w-full rounded-md shadow-sm focus:ring-navy-blue focus:border-navy-blue border p-2 ${themeClasses.components.input}`}
                placeholder="john@example.com"
              />
            </div>
          </div>
          
          <div>
            <label htmlFor="password" className={`block text-sm font-medium mb-1 ${themeClasses.text.secondary}`}>Password</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className={`h-5 w-5 ${themeClasses.text.muted}`} />
              </div>
              <input
                type={showPassword ? "text" : "password"}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className={`pl-10 pr-10 block w-full rounded-md shadow-sm focus:ring-navy-blue focus:border-navy-blue border p-2 ${themeClasses.components.input}`}
                placeholder="••••••••"
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={togglePasswordVisibility}
              >
                {showPassword ? (
                  <EyeOff className={`h-5 w-5 ${themeClasses.text.muted}`} />
                ) : (
                  <Eye className={`h-5 w-5 ${themeClasses.text.muted}`} />
                )}
              </button>
            </div>
          </div>
          
          <button
            type="submit"
            disabled={!isFormValid() || isSubmitting}
            className={`w-full py-2 px-4 rounded transition duration-200 ${
              isFormValid() && !isSubmitting
                ? themeClasses.components.button.primary
                : 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
            }`}
          >
            {isSubmitting ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <div className="mt-6 text-center">
          <p className={themeClasses.text.secondary}>
            Don't have an account?{' '}
            <button
              onClick={() => navigateTo('signup')}
              className={themeClasses.text.link}
            >
              Sign up
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage; 
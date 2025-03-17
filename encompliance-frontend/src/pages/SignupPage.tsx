import React, { useState, useEffect } from 'react';
import { MapPin, User, Building, Mail, Phone, Lock, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { SignupData } from '../services/authService';
import ErrorMessage from '../components/ErrorMessage';
import { themeClasses } from '../utils/themeUtils';

interface SignupPageProps {
  onStateSelect?: (state: string) => void;
  navigateTo?: (page: string) => void;
}

const SignupPage: React.FC<SignupPageProps> = ({ onStateSelect, navigateTo }) => {
  const { signup, error: authError, clearError } = useAuth();
  const [step, setStep] = useState(1);
  const [selectedState, setSelectedState] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [formData, setFormData] = useState({
    fullName: '',
    operationName: '',
    email: '',
    password: '',
    phoneNumber: ''
  });
  
  // Clear errors when component unmounts
  useEffect(() => {
    return () => {
      clearError();
    };
  }, [clearError]);
  
  const states = [
    { name: 'Texas', available: true },
    { name: 'California', available: false },
    { name: 'New York', available: false },
    { name: 'Florida', available: false },
    { name: 'Illinois', available: false },
    { name: 'Pennsylvania', available: false },
    { name: 'Ohio', available: false },
    { name: 'Georgia', available: false },
    { name: 'North Carolina', available: false },
    { name: 'Michigan', available: false }
  ];
  
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
  
  const handleNextStep = () => {
    setStep(2);
    // Clear any errors when moving to next step
    setLocalError(null);
    if (authError) clearError();
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedState) {
      setLocalError('Please select a state to continue');
      return;
    }
    
    try {
      setIsSubmitting(true);
      clearError();
      setLocalError(null);
      
      const signupData: SignupData = {
        email: formData.email,
        password: formData.password,
        full_name: formData.fullName,
        operation_name: formData.operationName,
        phone_number: formData.phoneNumber,
        state: selectedState,
        operation_type: 'daycare' // Default to daycare, will be updated in next step
      };
      
      console.log('Submitting signup data:', JSON.stringify(signupData));
      
      await signup(signupData);
      
      // The signup function in AuthContext handles token storage
      // We'll check for authError before proceeding
      if (!authError) {
        console.log('Signup success, navigating to dashboard...');
        
        // Navigate to the dashboard
        if (navigateTo) {
          navigateTo('dashboard');
        }
      } else {
        console.error('Auth error after signup:', authError);
      }
    } catch (err) {
      console.error('Signup error:', err);
      
      if (err instanceof Error) {
        setLocalError(`Error: ${err.message}`);
      } else {
        setLocalError('An unexpected error occurred during signup. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const isFormValid = () => {
    return (
      formData.fullName.trim() !== '' &&
      formData.operationName.trim() !== '' &&
      formData.email.trim() !== '' &&
      formData.password.trim() !== '' &&
      formData.phoneNumber.trim() !== ''
    );
  };
  
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };
  
  return (
    <div className={`container mx-auto px-4 py-12 max-w-2xl ${themeClasses.layout.container}`}>
      <div className={themeClasses.components.card}>
        <h1 className={`text-3xl font-bold mb-6 text-center font-times ${themeClasses.text.primary}`}>Create Your Account</h1>
        
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
        
        {step === 1 ? (
          <>
            <div className="space-y-4 mb-6">
              <div>
                <label htmlFor="fullName" className={`block text-sm font-medium mb-1 ${themeClasses.text.secondary}`}>Full Name</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className={`h-5 w-5 ${themeClasses.text.muted}`} />
                  </div>
                  <input
                    type="text"
                    id="fullName"
                    name="fullName"
                    value={formData.fullName}
                    onChange={handleInputChange}
                    className={`pl-10 ${themeClasses.components.input}`}
                    placeholder="John Doe"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="operationName" className={`block text-sm font-medium mb-1 ${themeClasses.text.secondary}`}>Operation Name</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Building className={`h-5 w-5 ${themeClasses.text.muted}`} />
                  </div>
                  <input
                    type="text"
                    id="operationName"
                    name="operationName"
                    value={formData.operationName}
                    onChange={handleInputChange}
                    className={`pl-10 ${themeClasses.components.input}`}
                    placeholder="Sunshine Daycare"
                  />
                </div>
              </div>
              
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
                    className={`pl-10 ${themeClasses.components.input}`}
                    placeholder="john@example.com"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="phoneNumber" className={`block text-sm font-medium mb-1 ${themeClasses.text.secondary}`}>Phone Number</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Phone className={`h-5 w-5 ${themeClasses.text.muted}`} />
                  </div>
                  <input
                    type="tel"
                    id="phoneNumber"
                    name="phoneNumber"
                    value={formData.phoneNumber}
                    onChange={handleInputChange}
                    className={`pl-10 ${themeClasses.components.input}`}
                    placeholder="(123) 456-7890"
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
                    className={`pl-10 pr-10 ${themeClasses.components.input}`}
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
            </div>
            
            <button
              onClick={handleNextStep}
              disabled={!isFormValid()}
              className={`w-full py-2 px-4 rounded transition duration-200 ${
                isFormValid()
                  ? themeClasses.components.button.primary
                  : 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
              }`}
            >
              Next
            </button>
          </>
        ) : (
          <>
            <div className="mb-6">
              <h2 className={`text-xl font-semibold mb-4 ${themeClasses.text.primary}`}>Select Your State</h2>
              <div className="grid grid-cols-2 gap-4">
                {states.map((state) => (
                  <button
                    key={state.name}
                    onClick={() => setSelectedState(state.name)}
                    disabled={!state.available}
                    className={`p-4 border rounded-lg flex items-center justify-center ${
                      selectedState === state.name
                        ? 'border-navy-blue dark:border-blue-500 bg-blue-50 dark:bg-blue-900/30 text-navy-blue dark:text-blue-400'
                        : state.available
                        ? 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800/50'
                        : 'border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-500 cursor-not-allowed'
                    }`}
                  >
                    <MapPin className="h-5 w-5 mr-2" />
                    {state.name}
                    {!state.available && <span className="ml-2 text-xs">(Coming Soon)</span>}
                  </button>
                ))}
              </div>
            </div>
            
            <div className="flex space-x-4">
              <button
                onClick={() => setStep(1)}
                className={`flex-1 py-2 px-4 border rounded ${themeClasses.border.primary} ${themeClasses.text.secondary} hover:bg-gray-50 dark:hover:bg-gray-800 transition duration-200`}
              >
                Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={!selectedState || isSubmitting}
                className={`flex-1 py-2 px-4 rounded transition duration-200 ${
                  selectedState && !isSubmitting
                    ? themeClasses.components.button.primary
                    : 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                }`}
              >
                {isSubmitting ? 'Creating Account...' : 'Continue'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default SignupPage;
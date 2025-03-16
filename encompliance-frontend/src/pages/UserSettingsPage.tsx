import React, { useState, useEffect } from 'react';
import { User, Mail, Phone, Lock, Save, AlertCircle, Trash2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import ErrorMessage from '../components/ErrorMessage';
import api from '../services/api';
import { userService } from '../services/userService';

interface UserSettingsPageProps {
  navigateTo: (page: string) => void;
}

const UserSettingsPage: React.FC<UserSettingsPageProps> = ({ navigateTo }) => {
  const { user, error: authError, clearError, logout } = useAuth();
  const [localError, setLocalError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phoneNumber: '',
    operationName: ''
  });
  
  // Load user data when component mounts
  useEffect(() => {
    if (user) {
      setFormData({
        fullName: user.full_name || '',
        email: user.email || '',
        phoneNumber: user.phone_number || '',
        operationName: user.operation_name || ''
      });
    }
    
    return () => {
      if (authError) clearError();
    };
  }, [user, authError, clearError]);
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Clear messages when user starts typing
    if (localError) setLocalError(null);
    if (successMessage) setSuccessMessage(null);
    if (authError) clearError();
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setIsLoading(true);
      setLocalError(null);
      setSuccessMessage(null);
      
      // Prepare data for API
      const updateData = {
        full_name: formData.fullName,
        phone_number: formData.phoneNumber,
        operation_name: formData.operationName
      };
      
      // Call API to update user
      await api.put('/users/me', updateData);
      
      setSuccessMessage('Your profile has been updated successfully.');
    } catch (err) {
      console.error('Error updating profile:', err);
      setLocalError('Failed to update profile. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleDeleteAccount = async () => {
    if (!showDeleteConfirm) {
      setShowDeleteConfirm(true);
      return;
    }
    
    try {
      setIsDeleting(true);
      await userService.deleteAccount();
      logout();
      navigateTo('login');
    } catch (error) {
      console.error('Error deleting account:', error);
      setLocalError('Failed to delete account. Please try again later.');
      setShowDeleteConfirm(false);
    } finally {
      setIsDeleting(false);
    }
  };
  
  const cancelDelete = () => {
    setShowDeleteConfirm(false);
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-navy-blue dark:text-white mb-6 font-times">User Settings</h1>
      
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
      
      {successMessage && (
        <div className="bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 text-green-700 dark:text-green-200 px-4 py-3 rounded mb-6 flex items-start">
          <div className="flex-shrink-0 mr-2">
            <AlertCircle className="h-5 w-5 text-green-500 dark:text-green-400" />
          </div>
          <div className="flex-grow">
            <p>{successMessage}</p>
          </div>
          <button 
            onClick={() => setSuccessMessage(null)}
            className="flex-shrink-0 ml-2 text-green-500 dark:text-green-400 hover:text-green-700 dark:hover:text-green-300"
          >
            &times;
          </button>
        </div>
      )}
      
      <div className="bg-white dark:bg-dark-surface rounded-lg shadow-md p-6">
        <form onSubmit={handleSubmit}>
          <div className="space-y-6">
            <div>
              <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Full Name</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  id="fullName"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleInputChange}
                  className="pl-10 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:ring-navy-blue focus:border-navy-blue dark:focus:ring-blue-500 dark:focus:border-blue-500 border p-2 dark:bg-gray-700 dark:text-white"
                  placeholder="John Doe"
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email Address</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  disabled
                  className="pl-10 block w-full rounded-md border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 shadow-sm border p-2 cursor-not-allowed dark:text-gray-400"
                  placeholder="john@example.com"
                />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">Email cannot be changed</p>
              </div>
            </div>
            
            <div>
              <label htmlFor="operationName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Operation Name</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  id="operationName"
                  name="operationName"
                  value={formData.operationName}
                  onChange={handleInputChange}
                  className="pl-10 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:ring-navy-blue focus:border-navy-blue dark:focus:ring-blue-500 dark:focus:border-blue-500 border p-2 dark:bg-gray-700 dark:text-white"
                  placeholder="Sunshine Daycare"
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="phoneNumber" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Phone Number</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Phone className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="tel"
                  id="phoneNumber"
                  name="phoneNumber"
                  value={formData.phoneNumber}
                  onChange={handleInputChange}
                  className="pl-10 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:ring-navy-blue focus:border-navy-blue dark:focus:ring-blue-500 dark:focus:border-blue-500 border p-2 dark:bg-gray-700 dark:text-white"
                  placeholder="(123) 456-7890"
                />
              </div>
            </div>
            
            <div className="pt-2">
              <button
                type="button"
                onClick={() => navigateTo('changePassword')}
                className="inline-flex items-center text-navy-blue dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
              >
                <Lock className="h-4 w-4 mr-1" />
                Change Password
              </button>
            </div>
            
            <div className="pt-4">
              <button
                type="submit"
                disabled={isLoading}
                className={`w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-navy-blue dark:bg-blue-700 hover:bg-blue-800 dark:hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-navy-blue dark:focus:ring-blue-500 ${
                  isLoading ? 'opacity-70 cursor-not-allowed' : ''
                }`}
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </>
                )}
              </button>
            </div>
            
            <div className="pt-8 border-t border-gray-200 dark:border-gray-700 mt-8">
              <h3 className="text-lg font-medium text-red-600 dark:text-red-400">Danger Zone</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Once you delete your account, all of your data will be permanently removed.
                This action cannot be undone.
              </p>
              
              {!showDeleteConfirm ? (
                <button
                  type="button"
                  onClick={handleDeleteAccount}
                  className="mt-4 flex items-center justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Account
                </button>
              ) : (
                <div className="mt-4 p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-md">
                  <p className="text-sm text-red-700 dark:text-red-300 font-medium">
                    Are you sure you want to delete your account? This will remove all your data and cannot be undone.
                  </p>
                  <div className="mt-3 flex space-x-3">
                    <button
                      type="button"
                      onClick={handleDeleteAccount}
                      disabled={isDeleting}
                      className={`flex items-center justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 ${
                        isDeleting ? 'opacity-70 cursor-not-allowed' : ''
                      }`}
                    >
                      {isDeleting ? 'Deleting...' : 'Yes, Delete My Account'}
                    </button>
                    <button
                      type="button"
                      onClick={cancelDelete}
                      disabled={isDeleting}
                      className="flex items-center justify-center py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-navy-blue dark:focus:ring-blue-500"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UserSettingsPage; 
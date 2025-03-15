import React, { useEffect } from 'react';
import { Shield, Home, LogIn, User, Settings } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import UniversalModelSelector from './UniversalModelSelector';

interface HeaderProps {
  navigateTo: (page: string) => void;
  currentPage: string;
}

const Header: React.FC<HeaderProps> = ({ navigateTo, currentPage }) => {
  const { isAuthenticated, logout } = useAuth();
  
  // Add debug logging for authentication state
  useEffect(() => {
    console.log("Header - Authentication state:", isAuthenticated);
  }, [isAuthenticated]);

  return (
    <header className="bg-navy-blue text-white shadow-md">
      <div className="container mx-auto px-4 py-3">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2 cursor-pointer" onClick={() => navigateTo('home')}>
            <Shield className="h-8 w-8" />
            <span className="text-xl font-bold font-times">Encompliance.io</span>
          </div>
          
          <nav className="hidden md:flex items-center space-x-6">
            <button 
              onClick={() => navigateTo('home')}
              className={`flex items-center space-x-1 ${currentPage === 'home' ? 'text-blue-300' : 'hover:text-blue-300'}`}
            >
              <Home className="h-5 w-5" />
              <span>Home</span>
            </button>
            
            {isAuthenticated ? (
              <>
                <button 
                  onClick={() => navigateTo('dashboard')}
                  className={`flex items-center space-x-1 ${currentPage === 'dashboard' ? 'text-blue-300' : 'hover:text-blue-300'}`}
                >
                  <span>Dashboard</span>
                </button>
                <button 
                  onClick={() => navigateTo('userSettings')}
                  className={`flex items-center space-x-1 ${currentPage === 'userSettings' ? 'text-blue-300' : 'hover:text-blue-300'}`}
                >
                  <User className="h-5 w-5" />
                  <span>User Profile</span>
                </button>
                <div className="ml-2 border-l border-gray-600 pl-2">
                  <UniversalModelSelector />
                </div>
                <button 
                  onClick={() => {
                    logout();
                    navigateTo('home');
                  }}
                  className="bg-white text-navy-blue px-4 py-2 rounded font-bold hover:bg-blue-100 transition duration-200"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => navigateTo('login')}
                  className="flex items-center space-x-1 text-white hover:text-blue-300"
                >
                  <LogIn className="h-5 w-5" />
                  <span>Login</span>
                </button>
                <button
                  onClick={() => navigateTo('signup')}
                  className="bg-white text-navy-blue px-4 py-2 rounded font-bold hover:bg-blue-100 transition duration-200"
                >
                  Sign Up
                </button>
              </>
            )}
          </nav>
          
          <div className="md:hidden">
            {/* Mobile menu button would go here */}
            <button className="text-white">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
import React, { useState, useEffect } from 'react';
import { Shield, Building2, FileText, Search, ZoomIn, ZoomOut, ChevronLeft, ChevronRight, MessageSquare, Home, User } from 'lucide-react';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import SignupPage from './pages/SignupPage';
import OperationTypePage from './pages/OperationTypePage';
import DocumentViewerPage from './pages/DocumentViewerPage';
import ManualUploadPage from './pages/ManualUploadPage';
import Dashboard from './pages/Dashboard';
import { AuthProvider, useAuth } from './contexts/AuthContext';

function AppContent() {
  const { isAuthenticated, loading } = useAuth();
  const [currentPage, setCurrentPage] = useState('home');
  const [selectedState, setSelectedState] = useState('');
  const [operationType, setOperationType] = useState('');

  // Redirect to dashboard if authenticated
  useEffect(() => {
    if (isAuthenticated && currentPage === 'home') {
      setCurrentPage('dashboard');
    }
  }, [isAuthenticated, currentPage]);

  const navigateTo = (page: string) => {
    setCurrentPage(page);
  };

  const handleStateSelection = (state: string) => {
    setSelectedState(state);
    navigateTo('operationType');
  };

  const handleOperationTypeSelection = (type: string) => {
    setOperationType(type);
    navigateTo('manualUpload');
  };

  const handleManualUploadComplete = () => {
    navigateTo('documentViewer');
  };

  const handleManualUploadSkip = () => {
    navigateTo('documentViewer');
  };

  // Show loading indicator
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomePage navigateTo={navigateTo} />;
      case 'signup':
        return <SignupPage onStateSelect={handleStateSelection} />;
      case 'operationType':
        return <OperationTypePage onOperationTypeSelect={handleOperationTypeSelection} />;
      case 'manualUpload':
        return (
          <ManualUploadPage 
            operationType={operationType}
            onUploadComplete={handleManualUploadComplete}
            onSkip={handleManualUploadSkip}
            onBack={() => navigateTo('operationType')}
          />
        );
      case 'documentViewer':
        return <DocumentViewerPage operationType={operationType} navigateTo={navigateTo} />;
      case 'dashboard':
        return <Dashboard navigateTo={navigateTo} />;
      default:
        return <HomePage navigateTo={navigateTo} />;
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header navigateTo={navigateTo} currentPage={currentPage} />
      <main className="flex-grow">
        {renderPage()}
      </main>
      <Footer />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
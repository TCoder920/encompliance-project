import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import SignupPage from './pages/SignupPage';
import LoginPage from './pages/LoginPage';
import OperationTypePage from './pages/OperationTypePage';
import DocumentViewerPage from './pages/DocumentViewerPage';
import ManualUploadPage from './pages/ManualUploadPage';
import Dashboard from './pages/Dashboard';
import SearchRegulationsPage from './pages/SearchRegulationsPage';
import UserSettingsPage from './pages/UserSettingsPage';
import AllQueriesPage from './pages/AllQueriesPage';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ModelProvider } from './contexts/ModelContext';
import { checkAuthToken, initDebugTools } from './debug';
import './App.css';

function AppContent() {
  const [currentPage, setCurrentPage] = useState('home');
  const [selectedState, setSelectedState] = useState('');
  const [operationType, setOperationType] = useState('');
  const [userDocuments, setUserDocuments] = useState<any[]>([]);
  const { user, loading, logout } = useAuth();

  // Initialize debug tools
  useEffect(() => {
    initDebugTools();
  }, []);

  // Set operation type from user data if available
  useEffect(() => {
    if (user && user.operation_type) {
      setOperationType(user.operation_type);
    }
  }, [user]);

  useEffect(() => {
    console.log("App - Authentication state changed:", user);
    console.log("App - Current page:", currentPage);
    const tokenStatus = checkAuthToken();
    console.log("Token status:", tokenStatus);
  }, [user, currentPage]);

  const handleRefreshDocuments = async () => {
    try {
      console.log('[DEBUG] App: Refreshing documents before rendering dashboard');
      if (user) {
        // Clear any previous document cache
        localStorage.removeItem('cachedDocuments');
        
        // Pre-fetch documents to ensure they're loaded
        const documentService = (await import('./services/documentService')).default;
        const documents = await documentService.refreshDocumentCache();
        console.log(`[DEBUG] App: Pre-loaded ${documents.length} documents`, documents);
        setUserDocuments(documents);
      }
    } catch (err) {
      console.error('[DEBUG] App: Error refreshing documents:', err);
    }
  };

  useEffect(() => {
    if (currentPage === 'dashboard') {
      handleRefreshDocuments();
    }
  }, [currentPage, user]);

  const handleNavigate = (page: string) => {
    console.log(`App - Navigating to: ${page}`);
    
    // If we're going to the dashboard, refresh documents first
    if (page === 'dashboard') {
      handleRefreshDocuments().then(() => {
        setCurrentPage(page);
      });
    } else {
      setCurrentPage(page);
    }
  };

  const handleStateSelection = (state: string) => {
    setSelectedState(state);
    setCurrentPage('operationType');
  };

  const handleOperationTypeSelection = (type: string) => {
    setOperationType(type);
    setCurrentPage('dashboard');
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  const renderPage = () => {
    if (currentPage.startsWith('document/') || currentPage.startsWith('/document/')) {
      const parts = currentPage.split('/');
      // Extract the document ID from the path, handling both formats
      const documentId = parts[parts.length - 1];
      console.log(`[DEBUG] Navigating to document with ID: ${documentId}`);
      return <DocumentViewerPage documentId={documentId} navigateTo={handleNavigate} />;
    }
    
    if (currentPage.startsWith('fullConversation/')) {
      const parts = currentPage.split('/');
      const queryId = parts[1];
      return <SearchRegulationsPage navigateTo={handleNavigate} initialQueryId={parseInt(queryId, 10)} showFullConversation={true} />;
    }
    
    switch(currentPage) {
      case 'home':
        return <HomePage navigateTo={handleNavigate} />;
      case 'signup':
        return <SignupPage navigateTo={handleNavigate} />;
      case 'login':
        return <LoginPage navigateTo={handleNavigate} />;
      case 'operationType':
        return <OperationTypePage onOperationTypeSelect={handleOperationTypeSelection} />;
      case 'documentViewer':
      case 'document-viewer':
        return <DocumentViewerPage isMinimumStandards={true} navigateTo={handleNavigate} />;
      case 'dashboard':
        return <Dashboard navigateTo={handleNavigate} preloadedDocuments={userDocuments} />;
      case 'search':
        return <SearchRegulationsPage navigateTo={handleNavigate} />;
      case 'userSettings':
        return <UserSettingsPage navigateTo={handleNavigate} />;
      case 'allQueries':
        return <AllQueriesPage navigateTo={handleNavigate} />;
      case 'documentUpload':
        return (
          <ManualUploadPage 
            operationType={operationType} 
            onUploadComplete={() => handleNavigate('dashboard')} 
            onBack={() => handleNavigate('dashboard')} 
            onSkip={() => handleNavigate('dashboard')} 
            navigateTo={handleNavigate}
          />
        );
      default:
        return <HomePage navigateTo={handleNavigate} />;
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header navigateTo={handleNavigate} currentPage={currentPage} />
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
      <ModelProvider>
        <AppContent />
      </ModelProvider>
    </AuthProvider>
  );
}

export default App; 
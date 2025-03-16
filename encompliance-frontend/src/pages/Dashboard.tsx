import React, { useState, useEffect } from 'react';
import { Clock, Search, FileText, Upload, PlusCircle, Eye, Trash2, X, MessageSquare } from 'lucide-react';
import ErrorMessage from '../components/ErrorMessage';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import documentService from '../services/documentService';
import DocumentUploader from '../components/DocumentUploader';
import * as documentLogger from '../utils/documentLogger';
import { formatDate, formatRelativeTime, formatDateTime } from '../utils/dateUtils';
import { deleteQuery, deleteAllQueries } from '../services/aiService';
import { deduplicateQueryLogs, QueryLog } from '../utils/queryUtils';

interface DashboardProps {
  navigateTo: (page: string) => void;
  preloadedDocuments?: any[];
}

const Dashboard: React.FC<DashboardProps> = ({ navigateTo, preloadedDocuments = [] }) => {
  const { error: authError, clearError, user } = useAuth();
  const [localError, setLocalError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [queryLogs, setQueryLogs] = useState<QueryLog[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalLogs, setTotalLogs] = useState(0);
  const [logsPerPage, setLogsPerPage] = useState(5);
  const [accountDetails, setAccountDetails] = useState({
    operationType: '',
    state: '',
    status: '',
    lastLogin: '',
    operationName: ''
  });
  const [selectedQuery, setSelectedQuery] = useState<QueryLog | null>(null);
  const [showQuerySummary, setShowQuerySummary] = useState(false);
  const [documents, setDocuments] = useState<any[]>([]);
  const [showUploadPrompt, setShowUploadPrompt] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [showUploader, setShowUploader] = useState(false);
  
  useEffect(() => {
    // Load dashboard data
    setIsLoading(true);
    
    // Ensure document cache is up-to-date on every dashboard load
    const refreshAllDocuments = async () => {
      documentLogger.docLog('Dashboard: Initial document refresh on mount');
      try {
        // If we have preloaded documents, use them first
        if (preloadedDocuments && preloadedDocuments.length > 0) {
          setDocuments(preloadedDocuments);
          setShowUploadPrompt(preloadedDocuments.length === 0);
          return;
        }
        
        // Otherwise refresh from the API
        localStorage.removeItem('cachedDocuments'); // Clear any cache first
        const userDocuments = await documentService.refreshDocumentCache();
        setDocuments(userDocuments);
        setShowUploadPrompt(userDocuments.length === 0);
      } catch (err) {
        setDocuments([]);
        setShowUploadPrompt(true);
      }
    };
    
    // Fetch actual query logs from the backend
    const fetchQueryLogs = async () => {
      try {
        // Use the API service with the correct base URL
        const skip = (page - 1) * logsPerPage;
        const response = await api.get(`/query-logs?limit=${logsPerPage}&skip=${skip}`);
        
        // Set total logs and calculate total pages
        setTotalLogs(response.data.total || 0);
        setTotalPages(Math.ceil((response.data.total || 0) / logsPerPage));
        
        if (response.data && response.data.logs) {
          // Validate and transform the data if needed
          const validLogs = response.data.logs.map((log: any) => {
            // Ensure all required fields are present
            if (!log.query_text && log.query) {
              log.query_text = log.query;
            }
            if (!log.response_text && log.response) {
              log.response_text = log.response;
            }
            // Ensure created_at is present
            if (!log.created_at && log.timestamp) {
              log.created_at = log.timestamp;
            }
            
            return log;
          });
          
          // Use the utility function to deduplicate logs
          const deduplicatedLogs = deduplicateQueryLogs(validLogs);
          
          setQueryLogs(deduplicatedLogs || []);
        } else {
          setQueryLogs([]);
        }
      } catch (err) {
        // Don't set error on failed fetch - just show empty state
        setQueryLogs([]);
      } finally {
        setIsLoading(false);
      }
    };
    
    // Fetch user account details
    const fetchAccountDetails = async () => {
      try {
        if (user) {
          // Use user data from context or fetch additional details if needed
          setAccountDetails({
            operationType: user.operation_type || 'Not specified',
            state: user.state || 'Not specified',
            status: user.is_active ? 'Active' : 'Inactive',
            // Format the last login date using the dedicated last_login field
            lastLogin: formatDateTime(user.last_login || user.updated_at || new Date().toISOString()),
            operationName: user.operation_name || 'Not specified'
          });
        }
      } catch (err) {
        // Error handling
      }
    };
    
    // Call all the data loading functions
    const loadAllData = async () => {
      try {
        await fetchQueryLogs();
        await fetchAccountDetails();
        await refreshAllDocuments(); // Use our new refresh function
        documentLogger.docSuccess('Dashboard: All data loaded successfully');
      } catch (err) {
        documentLogger.docError('Dashboard: Error loading dashboard data', { error: err });
      } finally {
        setIsLoading(false);
      }
    };
    
    loadAllData();
    
    return () => {
      if (authError) clearError();
    };
  }, [authError, clearError, user, preloadedDocuments, page, logsPerPage]);
  
  const handleNavigation = (page: string) => {
    try {
      // If navigating to a document, ensure it has the right format
      if (page.startsWith('document/')) {
        const docId = page.split('/')[1];
      }
      navigateTo(page);
    } catch (err) {
      setLocalError('Unable to navigate to the requested page. Please try again.');
    }
  };
  
  const handleViewQuery = async (queryId: number) => {
    try {
      // Use the API service with the correct base URL
      const response = await api.get(`/query/${queryId}`);
      
      if (response.data) {
        // Transform the response to match our QueryLog interface
        const queryData: QueryLog = {
          id: response.data.id,
          query_text: response.data.query_text || response.data.query || '',
          response_text: response.data.response_text || response.data.response || '',
          created_at: response.data.created_at || response.data.timestamp || new Date().toISOString(),
          document_reference: response.data.document_reference || response.data.document || '',
          conversation_id: response.data.conversation_id,
          full_conversation: response.data.full_conversation
        };
        
        setSelectedQuery(queryData);
        setShowQuerySummary(true);
      } else {
        setLocalError('Failed to load query details. Empty response from server.');
      }
    } catch (err) {
      setLocalError('Failed to load query details. Please try again.');
    }
  };
  
  const handleDeleteQuery = async (queryId: number, event: React.MouseEvent) => {
    // Stop the click from propagating to the parent (which would open the query)
    event.stopPropagation();
    
    // Confirm deletion
    if (!window.confirm('Are you sure you want to delete this conversation?')) {
      return;
    }
    
    try {
      setIsLoading(true);
      await deleteQuery(queryId);
      
      // Remove the deleted query from the state
      setQueryLogs(prevLogs => prevLogs.filter(log => log.id !== queryId));
      
      // If the deleted query is currently selected, close the summary
      if (selectedQuery && selectedQuery.id === queryId) {
        setSelectedQuery(null);
        setShowQuerySummary(false);
      }
      
      setLocalError(null);
    } catch (error) {
      setLocalError('Failed to delete the conversation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleCloseQuerySummary = () => {
    setShowQuerySummary(false);
    setSelectedQuery(null);
  };
  
  const handleUploadComplete = async (file: File) => {
    const operation = documentLogger.docStart('dashboard.handleUploadComplete', { fileName: file.name }) || 'dashboard.handleUploadComplete';
    try {
      documentLogger.docLog('Dashboard: Starting document upload process', { fileName: file.name });
      setIsLoading(true); // Show loading state
      const uploadedDoc = await documentService.uploadDocument(file);
      setUploadSuccess(true);
      setShowUploadPrompt(false);
      documentLogger.docSuccess('Dashboard: Document upload successful', { fileName: file.name, id: uploadedDoc.id });
      
      // Refresh document list with error handling
      try {
        documentLogger.docLog('Dashboard: Refreshing document list after upload');
        
        // Force clear cache first
        localStorage.removeItem('cachedDocuments');
        
        // Direct API call to get fresh document list
        const api = (await import('../services/api')).default;
        const response = await api.get('/documents/list');
        
        if (response.data && Array.isArray(response.data.documents)) {
          const userDocuments = response.data.documents;
          setDocuments(userDocuments);
          documentLogger.docSuccess('Dashboard: Document list refreshed successfully', { 
            count: userDocuments.length,
            documents: userDocuments.map((d: any) => ({ id: d.id, filename: d.filename }))
          });
        } else {
          // Fallback to document service
          const userDocuments = await documentService.refreshDocumentCache();
          setDocuments(userDocuments);
        }
      } catch (refreshError) {
        documentLogger.docError('Dashboard: Error refreshing document list', { error: refreshError });
        setLocalError('Document uploaded but failed to refresh the list. Please try again.');
      }
    } catch (err) {
      documentLogger.docError('Dashboard: Error uploading document', { error: err });
      setLocalError('Failed to upload document. Please try again.');
    } finally {
      setIsLoading(false); // Hide loading state
      documentLogger.docEnd(operation);
    }
  };
  
  const handleViewStandards = () => {
    // Use the document service to open the minimum standards in a new tab
    documentService.openMinimumStandardsInNewTab();
  };
  
  const handleViewDocument = (documentId: number) => {
    // Make sure to use string conversion for documentId
    const docIdStr = documentId.toString();
    
    // Use the document service to open the document in a new tab
    documentService.openDocumentInNewTab(docIdStr);
  };
  
  const handleDeleteDocument = async (documentId: number) => {
    try {
      await documentService.deleteDocument(documentId);
      // Refresh document list
      const userDocuments = await documentService.listDocuments();
      setDocuments(userDocuments);
    } catch (err) {
      setLocalError('Failed to delete document. Please try again.');
    }
  };
  
  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
    }
  };
  
  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 flex justify-center items-center h-64">
        <div className="animate-pulse text-navy-blue dark:text-white">Loading dashboard...</div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-navy-blue dark:text-white mb-6 font-times">Owner Dashboard</h1>
      
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
      
      {showUploadPrompt && !uploadSuccess && (
        <div className="bg-blue-50 dark:bg-gray-700 border border-blue-200 dark:border-gray-600 rounded-lg p-6 mb-6">
          <div className="flex flex-col items-center text-center">
            <div className="flex-shrink-0 text-blue-500 dark:text-blue-400 mb-4">
              <FileText className="h-10 w-10" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-blue-800 dark:text-blue-300 mb-2">Upload Required Documents</h3>
              <div className="text-sm text-blue-700 dark:text-blue-200">
                <p>Please upload your required compliance documents to ensure your center meets all regulatory requirements.</p>
                <div className="mt-6 max-w-md mx-auto">
                  <DocumentUploader 
                    onUploadComplete={handleUploadComplete}
                    allowedFileTypes={['.pdf', '.docx', '.doc', '.txt']}
                    maxSizeMB={50}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {uploadSuccess && (
        <div className="bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <div className="flex-shrink-0 text-green-500 dark:text-green-400 mt-0.5">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-green-800 dark:text-green-300">Document Upload Successful</h3>
              <div className="mt-2 text-sm text-green-700 dark:text-green-200">
                <p>Your compliance document has been uploaded successfully.</p>
              </div>
              <div className="mt-2">
                <button
                  onClick={() => setUploadSuccess(false)}
                  className="text-sm text-green-700 dark:text-green-300 hover:text-green-900 dark:hover:text-green-100 font-medium underline"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white dark:bg-dark-surface p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold text-navy-blue dark:text-white mb-4">Quick Access</h2>
          <button 
            onClick={() => {
              // Navigate to the document viewer page for minimum standards
              handleViewStandards();
            }}
            className="w-full bg-navy-blue text-white dark:bg-blue-700 py-2 px-4 rounded mb-3 flex items-center justify-center hover:bg-blue-800 dark:hover:bg-blue-600 transition-colors duration-200"
          >
            <FileText className="mr-2 h-5 w-5" />
            View Minimum Standards
          </button>
          <button 
            onClick={() => handleNavigation('search')}
            className="w-full border border-navy-blue text-navy-blue dark:border-blue-500 dark:text-blue-400 py-2 px-4 rounded mb-3 flex items-center justify-center hover:bg-blue-50 dark:hover:bg-gray-800 transition-colors duration-200"
          >
            <Search className="mr-2 h-5 w-5" />
            Search Regulations
          </button>
          {!showUploadPrompt && (
            <button 
              onClick={() => navigateTo('documentUpload')}
              className="w-full border border-navy-blue text-navy-blue dark:border-blue-500 dark:text-blue-400 py-2 px-4 rounded flex items-center justify-center hover:bg-blue-50 dark:hover:bg-gray-800 transition-colors duration-200"
            >
              <Upload className="mr-2 h-5 w-5" />
              Upload Documents
            </button>
          )}
        </div>
        
        <div className="bg-white dark:bg-dark-surface p-6 rounded-lg shadow-md md:col-span-2">
          <h2 className="text-xl font-bold text-navy-blue dark:text-white mb-4">Account Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="border border-gray-200 dark:border-gray-700 rounded p-4 dark:bg-gray-800">
              <h3 className="font-bold text-gray-700 dark:text-gray-300 mb-2">Operation Name</h3>
              <p className="dark:text-white">{accountDetails.operationName}</p>
            </div>
            <div className="border border-gray-200 dark:border-gray-700 rounded p-4 dark:bg-gray-800">
              <h3 className="font-bold text-gray-700 dark:text-gray-300 mb-2">Operation Type</h3>
              <p className="dark:text-white">{accountDetails.operationType}</p>
            </div>
            <div className="border border-gray-200 dark:border-gray-700 rounded p-4 dark:bg-gray-800">
              <h3 className="font-bold text-gray-700 dark:text-gray-300 mb-2">State</h3>
              <p className="dark:text-white">{accountDetails.state}</p>
            </div>
            <div className="border border-gray-200 dark:border-gray-700 rounded p-4 dark:bg-gray-800">
              <h3 className="font-bold text-gray-700 dark:text-gray-300 mb-2">Account Status</h3>
              <p className={accountDetails.status === 'Active' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}>
                {accountDetails.status}
              </p>
            </div>
            <div className="border border-gray-200 dark:border-gray-700 rounded p-4 dark:bg-gray-800">
              <h3 className="font-bold text-gray-700 dark:text-gray-300 mb-2">Last Login</h3>
              <p className="dark:text-white">{accountDetails.lastLogin}</p>
            </div>
          </div>
        </div>
      </div>
      
      {showQuerySummary && selectedQuery ? (
        <div className="bg-white dark:bg-dark-surface p-6 rounded-lg shadow-md mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-navy-blue dark:text-white">Conversation Summary</h2>
            <div className="flex space-x-4">
              <button
                onClick={() => navigateTo(`fullConversation/${selectedQuery.id}`)}
                className="text-navy-blue dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
              >
                View Full Conversation
              </button>
              <button 
                onClick={handleCloseQuerySummary}
                className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
              >
                Close
              </button>
            </div>
          </div>
          
          <div className="border-b border-gray-200 dark:border-gray-700 pb-4 mb-4">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              <span className="flex items-center">
                <Clock className="h-4 w-4 mr-1" />
                {formatDateTime(selectedQuery.created_at || selectedQuery.timestamp || '')}
              </span>
            </div>
            <p className="font-medium mt-1 dark:text-white">{selectedQuery.query_text || selectedQuery.query}</p>
          </div>
          
          <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded">
            <h3 className="font-medium mb-2 dark:text-white">AI Response:</h3>
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{selectedQuery.response_text || selectedQuery.response}</p>
          </div>
          
          {selectedQuery.full_conversation && (
            <button
              onClick={() => navigateTo(`fullConversation/${selectedQuery.id}`)}
              className="mt-4 text-navy-blue dark:text-blue-400 hover:underline"
            >
              View Full Conversation
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white dark:bg-dark-surface p-6 rounded-lg shadow-md">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-navy-blue dark:text-white">Recent AI Queries</h2>
              <div className="flex items-center space-x-3">
                {queryLogs.length > 0 && (
                  <button
                    onClick={() => {
                      if (window.confirm('Are you sure you want to delete all your recent queries? This action cannot be undone.')) {
                        setIsLoading(true);
                        
                        // Use the new deleteAllQueries function
                        deleteAllQueries()
                          .then((result) => {
                            setQueryLogs([]);
                            setLocalError(null);
                          })
                          .catch(error => {
                            setLocalError('Failed to delete all conversations. Please try again.');
                          })
                          .finally(() => {
                            setIsLoading(false);
                          });
                      }
                    }}
                    className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 text-sm flex items-center"
                  >
                    <Trash2 className="h-3 w-3 mr-1" />
                    Delete All
                  </button>
                )}
                <button 
                  onClick={() => handleNavigation('allQueries')}
                  className="text-navy-blue dark:text-blue-400 hover:underline text-sm"
                >
                  View All
                </button>
              </div>
            </div>
            
            {queryLogs.length > 0 ? (
              <div className="space-y-4">
                {queryLogs.slice(0, 3).map((log, index) => (
                  <div key={index} className="border-b border-gray-200 dark:border-gray-700 pb-3 last:border-b-0 last:pb-0">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                        <Clock className="h-4 w-4 mr-1" />
                        <span>{formatRelativeTime(log.created_at || '')}</span>
                      </div>
                      <button
                        onClick={(e) => handleDeleteQuery(log.id, e)}
                        className="text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400"
                        title="Delete conversation"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    <p className="font-medium truncate dark:text-white">{log.query_text}</p>
                    <div className="mt-2 text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-800 p-2 rounded">
                      <p className="line-clamp-2">{log.response_text || 'Summary not available'}</p>
                    </div>
                    <button
                      onClick={() => handleViewQuery(log.id)}
                      className="text-sm text-navy-blue dark:text-blue-400 hover:underline mt-1"
                    >
                      View Details
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <p className="text-gray-500 dark:text-gray-400 mb-3">No recent queries</p>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Start a conversation with the AI assistant to see your query history here.</p>
                <button 
                  onClick={() => handleNavigation('search')}
                  className="bg-navy-blue dark:bg-blue-700 text-white py-2 px-4 rounded hover:bg-blue-800 dark:hover:bg-blue-600 transition-colors duration-200"
                >
                  <Search className="h-4 w-4 inline mr-2" />
                  Ask About Regulations
                </button>
              </div>
            )}
          </div>
          
          <div className="bg-white dark:bg-dark-surface p-6 rounded-lg shadow-md">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-navy-blue dark:text-white">Document Library</h2>
              {documents.length > 0 && (
                <button 
                  onClick={async () => {
                    try {
                      setIsLoading(true);
                      await documentService.refreshDocumentCache();
                      const userDocuments = await documentService.listDocuments();
                      setDocuments(userDocuments);
                    } catch (err) {
                      setLocalError('Failed to refresh documents. Please try again.');
                    } finally {
                      setIsLoading(false);
                    }
                  }}
                  className="text-sm text-navy-blue dark:text-blue-400 hover:underline flex items-center"
                >
                  <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Refresh
                </button>
              )}
            </div>
            
            {/* Improve document display with better containment */}
            <div className="grid grid-cols-1 gap-4 mt-4">
              {documents.map((doc) => (
                <div key={doc.id} className="bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
                  <div className="flex justify-between items-center">
                    <div className="flex-1 mr-4">
                      <h3 
                        className="text-md font-semibold truncate text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 cursor-pointer flex items-center"
                        onClick={() => handleViewDocument(doc.id)}
                      >
                        {doc.filename}
                      </h3>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Uploaded: {formatDateTime(doc.uploaded_at)}
                      </div>
                    </div>
                    <div className="flex space-x-2 flex-shrink-0">
                      <button 
                        onClick={() => handleViewDocument(doc.id)}
                        className="p-2 bg-blue-50 dark:bg-blue-900 text-blue-600 dark:text-blue-400 rounded-full hover:bg-blue-100 dark:hover:bg-blue-800"
                        title="View Document"
                      >
                        <Eye size={16} />
                      </button>
                      <button
                        onClick={() => handleDeleteDocument(doc.id)}
                        className="p-2 bg-red-50 dark:bg-red-900 text-red-600 dark:text-red-400 rounded-full hover:bg-red-100 dark:hover:bg-red-800"
                        title="Delete Document"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
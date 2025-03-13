import React, { useState, useEffect } from 'react';
import { Clock, Search, FileText } from 'lucide-react';
import ErrorMessage from '../components/ErrorMessage';
import { useAuth } from '../contexts/AuthContext';
import PDFViewer from '../components/PDFViewer';
import { PDF } from '../services/pdfService';
import api from '../services/api';

interface DashboardProps {
  navigateTo: (page: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ navigateTo }) => {
  const { error: authError, clearError, user } = useAuth();
  const [localError, setLocalError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [queryLogs, setQueryLogs] = useState<any[]>([]);
  const [accountDetails, setAccountDetails] = useState({
    operationType: '',
    state: '',
    status: '',
    lastLogin: ''
  });
  const [selectedQuery, setSelectedQuery] = useState<any | null>(null);
  const [showQuerySummary, setShowQuerySummary] = useState(false);
  
  const handlePDFSelect = (pdf: PDF) => {
    // You can implement PDF viewing functionality here
    console.log('Selected PDF:', pdf);
    // For example, you could navigate to a PDF viewer page with the PDF ID
    // navigateTo(`pdfViewer/${pdf.id}`);
  };
  
  useEffect(() => {
    // Simulate loading data
    setIsLoading(true);
    
    // Fetch actual query logs from the backend
    const fetchQueryLogs = async () => {
      try {
        // Use the API service with the correct base URL
        const response = await api.get('/query-logs');
        setQueryLogs(response.data.logs || []);
      } catch (err) {
        console.error('Error fetching query logs:', err);
        // Don't set error on failed fetch - just show empty state
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
            lastLogin: 'Last login data unavailable' // Simplified to avoid TypeScript errors
          });
        }
      } catch (err) {
        console.error('Error fetching account details:', err);
      }
    };
    
    fetchQueryLogs();
    fetchAccountDetails();
    
    return () => {
      if (authError) clearError();
    };
  }, [authError, clearError, user]);
  
  const handleNavigation = (page: string) => {
    try {
      navigateTo(page);
    } catch (err) {
      console.error('Navigation error:', err);
      setLocalError('Unable to navigate to the requested page. Please try again.');
    }
  };
  
  const handleViewQuery = async (queryId: number) => {
    try {
      // Use the API service with the correct base URL
      const response = await api.get(`/query/${queryId}`);
      setSelectedQuery(response.data);
      setShowQuerySummary(true);
    } catch (err) {
      console.error('Error fetching query details:', err);
      setLocalError('Failed to load query details. Please try again.');
    }
  };
  
  const handleCloseQuerySummary = () => {
    setShowQuerySummary(false);
    setSelectedQuery(null);
  };
  
  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 flex justify-center items-center h-64">
        <div className="animate-pulse text-navy-blue">Loading dashboard...</div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-navy-blue mb-6 font-times">Owner Dashboard</h1>
      
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
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold text-navy-blue mb-4">Quick Access</h2>
          <button 
            onClick={() => handleNavigation('documentViewer')}
            className="w-full bg-navy-blue text-white py-2 px-4 rounded mb-3 flex items-center justify-center"
          >
            <FileText className="mr-2 h-5 w-5" />
            View Minimum Standards
          </button>
          <button 
            onClick={() => handleNavigation('search')}
            className="w-full border border-navy-blue text-navy-blue py-2 px-4 rounded mb-3 flex items-center justify-center"
          >
            <Search className="mr-2 h-5 w-5" />
            Search Regulations
          </button>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md md:col-span-2">
          <h2 className="text-xl font-bold text-navy-blue mb-4">Account Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-gray-200 rounded p-4">
              <h3 className="font-bold text-gray-700 mb-2">Operation Type</h3>
              <p>{accountDetails.operationType}</p>
            </div>
            <div className="border border-gray-200 rounded p-4">
              <h3 className="font-bold text-gray-700 mb-2">State</h3>
              <p>{accountDetails.state}</p>
            </div>
            <div className="border border-gray-200 rounded p-4">
              <h3 className="font-bold text-gray-700 mb-2">Account Status</h3>
              <p className={accountDetails.status === 'Active' ? 'text-green-600' : 'text-red-600'}>
                {accountDetails.status}
              </p>
            </div>
            <div className="border border-gray-200 rounded p-4">
              <h3 className="font-bold text-gray-700 mb-2">Last Login</h3>
              <p>{accountDetails.lastLogin}</p>
            </div>
          </div>
        </div>
      </div>
      
      {showQuerySummary && selectedQuery ? (
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-navy-blue">Conversation Summary</h2>
            <button 
              onClick={handleCloseQuerySummary}
              className="text-gray-500 hover:text-gray-700"
            >
              Close
            </button>
          </div>
          
          <div className="border-b border-gray-200 pb-4 mb-4">
            <p className="text-sm text-gray-500">
              {new Date(selectedQuery.timestamp).toLocaleString()}
            </p>
            <p className="font-medium mt-1">{selectedQuery.query}</p>
          </div>
          
          <div className="bg-gray-50 p-4 rounded">
            <h3 className="font-medium mb-2">AI Response:</h3>
            <p className="text-gray-700 whitespace-pre-wrap">{selectedQuery.response}</p>
          </div>
          
          {selectedQuery.full_conversation && (
            <button
              onClick={() => navigateTo(`fullConversation/${selectedQuery.id}`)}
              className="mt-4 text-navy-blue hover:underline"
            >
              View Full Conversation
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-navy-blue">Recent AI Queries</h2>
              <button 
                onClick={() => handleNavigation('allQueries')}
                className="text-navy-blue hover:underline text-sm"
              >
                View All
              </button>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Query
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Time
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Document
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {queryLogs.length > 0 ? (
                    queryLogs.slice(0, 3).map((log) => (
                      <tr key={log.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {log.query}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 flex items-center">
                          <Clock className="h-4 w-4 mr-1" />
                          {log.timestamp}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {log.document}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-navy-blue">
                          <button 
                            onClick={() => handleViewQuery(log.id)}
                            className="hover:underline"
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                        No recent queries found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
          
          <div>
            <PDFViewer onPDFSelect={handlePDFSelect} />
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
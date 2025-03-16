import React, { useState, useEffect } from 'react';
import { Clock, MessageSquare, Trash2, ChevronLeft, ChevronRight } from 'lucide-react';
import api from '../services/api';
import ErrorMessage from '../components/ErrorMessage';
import { formatDateTime, formatRelativeTime } from '../utils/dateUtils';
import { deleteQuery, deleteAllQueries } from '../services/aiService';
import { deduplicateQueryLogs, QueryLog } from '../utils/queryUtils';

interface AllQueriesPageProps {
  navigateTo: (page: string) => void;
}

const AllQueriesPage: React.FC<AllQueriesPageProps> = ({ navigateTo }) => {
  const [queryLogs, setQueryLogs] = useState<QueryLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalLogs, setTotalLogs] = useState(0);
  const [logsPerPage, setLogsPerPage] = useState(10);
  const [manualPage, setManualPage] = useState('');

  useEffect(() => {
    async function getQueryLogs() {
      try {
        setLoading(true);
        console.log('Fetching query logs...');
        console.log(`Page: ${page}, Logs per page: ${logsPerPage}`);
        
        const skip = (page - 1) * logsPerPage;
        const response = await api.get(`/query-logs?limit=${logsPerPage}&skip=${skip}`);
        console.log('Query logs response:', response.data);
        
        // Set total logs and calculate total pages
        setTotalLogs(response.data.total || 0);
        setTotalPages(Math.ceil((response.data.total || 0) / logsPerPage));
        
        if (response.data && response.data.logs) {
          // Transform the data to ensure consistent field names
          const transformedLogs = response.data.logs.map((log: any) => ({
            id: log.id,
            query_text: log.query_text || log.query,
            response_text: log.response_text || log.response,
            created_at: log.created_at || log.timestamp,
            conversation_id: log.conversation_id,
            document_reference: log.document_reference,
            document_id: log.document_id
          }));
          
          console.log('Transformed logs:', transformedLogs);
          
          // Use the utility function to deduplicate logs
          const deduplicatedLogs = deduplicateQueryLogs(transformedLogs);
          
          console.log('Setting deduplicated logs:', deduplicatedLogs);
          setQueryLogs(deduplicatedLogs);
        } else {
          console.warn('No logs found in response:', response.data);
          setQueryLogs([]);
        }
      } catch (err) {
        console.error('Error fetching query logs:', err);
        setError('Failed to load query logs.');
      } finally {
        setLoading(false);
      }
    }
    getQueryLogs();
  }, [page, logsPerPage]);

  const handleDeleteQuery = async (queryId: number) => {
    // Confirm deletion
    if (!window.confirm('Are you sure you want to delete this conversation?')) {
      return;
    }
    
    try {
      setLoading(true);
      await deleteQuery(queryId);
      
      // Remove the deleted query from the state
      setQueryLogs(prevLogs => prevLogs.filter(log => log.id !== queryId));
      
      setError('');
    } catch (err) {
      console.error('Error deleting query:', err);
      setError('Failed to delete the conversation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAllQueries = async () => {
    // Confirm deletion
    if (!window.confirm('Are you sure you want to delete ALL conversations? This action cannot be undone.')) {
      return;
    }
    
    try {
      setLoading(true);
      
      // Use the new deleteAllQueries function
      const result = await deleteAllQueries();
      console.log(`Successfully deleted ${result.count} queries`);
      
      // Clear the logs from state
      setQueryLogs([]);
      setError('');
    } catch (err) {
      console.error('Error deleting all queries:', err);
      setError('Failed to delete all conversations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
    }
  };

  const handleManualPageChange = (e: React.FormEvent) => {
    e.preventDefault();
    const pageNum = parseInt(manualPage);
    if (!isNaN(pageNum) && pageNum >= 1 && pageNum <= totalPages) {
      setPage(pageNum);
      setManualPage('');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-navy-blue dark:text-white transition-colors duration-300">All Conversations</h1>
        
        <div className="flex space-x-4">
          <button
            onClick={handleDeleteAllQueries}
            disabled={loading || queryLogs.length === 0}
            className={`px-4 py-2 rounded flex items-center ${
              loading || queryLogs.length === 0
                ? 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                : 'bg-red-600 dark:bg-red-700 text-white hover:bg-red-700 dark:hover:bg-red-800'
            } transition-colors duration-300`}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Delete All
          </button>
        </div>
      </div>
      
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin h-8 w-8 border-4 border-navy-blue dark:border-blue-500 border-t-transparent rounded-full mx-auto mb-4 transition-colors duration-300"></div>
          <p className="text-gray-600 dark:text-gray-300 transition-colors duration-300">Loading conversations...</p>
        </div>
      ) : error ? (
        <ErrorMessage message={error} type="error" onClose={() => setError('')} />
      ) : (
        <>
          {queryLogs.length === 0 ? (
            <div className="text-center py-8 border border-dashed border-gray-300 dark:border-gray-600 rounded-lg transition-colors duration-300">
              <MessageSquare className="h-12 w-12 mx-auto text-gray-400 dark:text-gray-500 transition-colors duration-300 mb-3" />
              <p className="text-gray-600 dark:text-gray-300 transition-colors duration-300 mb-2">No conversations found</p>
            </div>
          ) : (
            <div className="bg-white dark:bg-dark-surface rounded-lg shadow-md p-6 transition-colors duration-300">
              <ul className="divide-y divide-gray-200 dark:divide-gray-700 transition-colors duration-300">
                {queryLogs.map((query) => (
                  <li key={query.id} className="py-4">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 transition-colors duration-300">
                        <Clock className="h-3 w-3 mr-1" />
                        <span>{formatRelativeTime(query.created_at || '')}</span>
                        {query.conversation_id && (
                          <span className="ml-2">• Conversation #{query.conversation_id.toString().substring(0, 8)}</span>
                        )}
                      </div>
                      <button
                        onClick={() => handleDeleteQuery(query.id)}
                        className="text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400 transition-colors duration-300"
                        title="Delete conversation"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    <p className="font-medium mb-2 text-gray-800 dark:text-gray-200 transition-colors duration-300">{query.query_text}</p>
                    {query.document_reference && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 transition-colors duration-300 mb-2">Document: {query.document_reference}</p>
                    )}
                    <div className="flex space-x-3">
                      <button
                        onClick={() => navigateTo(`fullConversation/${query.id}`)}
                        className="text-sm text-navy-blue dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 flex items-center transition-colors duration-300"
                      >
                        <MessageSquare className="h-4 w-4 mr-1" />
                        View Full Conversation
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex flex-col items-center mt-6 space-y-3">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handlePageChange(page - 1)}
                  disabled={page === 1}
                  className={`p-2 rounded transition-colors duration-300 ${
                    page === 1 
                      ? 'bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed' 
                      : 'bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-500'
                  }`}
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
                
                <div className="text-sm text-gray-700 dark:text-gray-300 transition-colors duration-300">
                  Page {page} of {totalPages}
                </div>
                
                <button
                  onClick={() => handlePageChange(page + 1)}
                  disabled={page === totalPages}
                  className={`p-2 rounded transition-colors duration-300 ${
                    page === totalPages 
                      ? 'bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed' 
                      : 'bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-500'
                  }`}
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              </div>
              
              {/* Manual page selection - only show if there are 3 or more pages */}
              {totalPages >= 3 && (
                <form onSubmit={handleManualPageChange} className="flex items-center space-x-2">
                  <label htmlFor="pageNumber" className="text-sm text-gray-600 dark:text-gray-400 transition-colors duration-300">Go to page:</label>
                  <input
                    id="pageNumber"
                    type="number"
                    min="1"
                    max={totalPages}
                    value={manualPage}
                    onChange={(e) => setManualPage(e.target.value)}
                    className="w-16 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 transition-colors duration-300"
                  />
                  <button
                    type="submit"
                    className="px-3 py-1 bg-navy-blue dark:bg-blue-600 text-white rounded text-sm hover:bg-blue-700 dark:hover:bg-blue-700 transition-colors duration-300"
                  >
                    Go
                  </button>
                </form>
              )}
            </div>
          )}
        </>
      )}
      
      <button
        onClick={() => navigateTo('dashboard')}
        className="mt-6 px-4 py-2 bg-navy-blue dark:bg-blue-600 text-white rounded hover:bg-blue-700 dark:hover:bg-blue-700 transition-colors duration-300"
      >
        Back to Dashboard
      </button>
    </div>
  );
};

export default AllQueriesPage; 
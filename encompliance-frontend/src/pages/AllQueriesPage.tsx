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
      
      // Force refresh the page to ensure all queries are removed from view
      window.location.reload();
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
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold text-navy-blue mb-6">All Conversations</h1>
      
      <div className="flex justify-between items-center mb-4">
        <div>
          {queryLogs.length > 0 && (
            <button
              onClick={handleDeleteAllQueries}
              className="px-3 py-1 bg-red-100 text-red-600 rounded hover:bg-red-200 flex items-center"
            >
              <Trash2 className="h-4 w-4 mr-1" />
              Delete All Conversations
            </button>
          )}
        </div>
        <div className="text-sm text-gray-600">
          Showing {queryLogs.length} of {totalLogs} logs
        </div>
      </div>
      
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin h-8 w-8 border-4 border-navy-blue border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading conversations...</p>
        </div>
      ) : error ? (
        <ErrorMessage message={error} type="error" onClose={() => setError('')} />
      ) : (
        <>
          {queryLogs.length === 0 ? (
            <div className="text-center py-8 border border-dashed border-gray-300 rounded-lg">
              <MessageSquare className="h-12 w-12 mx-auto text-gray-400 mb-3" />
              <p className="text-gray-600 mb-2">No conversations found</p>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-6">
              <ul className="divide-y divide-gray-200">
                {queryLogs.map((query) => (
                  <li key={query.id} className="py-4">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center text-xs text-gray-500">
                        <Clock className="h-3 w-3 mr-1" />
                        <span>{formatRelativeTime(query.created_at || '')}</span>
                        {query.conversation_id && (
                          <span className="ml-2">• Conversation #{query.conversation_id.toString().substring(0, 8)}</span>
                        )}
                      </div>
                      <button
                        onClick={() => handleDeleteQuery(query.id)}
                        className="text-gray-400 hover:text-red-500"
                        title="Delete conversation"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    <p className="font-medium mb-2">{query.query_text}</p>
                    {query.document_reference && (
                      <p className="text-xs text-gray-500 mb-2">Document: {query.document_reference}</p>
                    )}
                    <div className="flex space-x-3">
                      <button
                        onClick={() => navigateTo(`fullConversation/${query.id}`)}
                        className="text-sm text-navy-blue hover:text-blue-700 flex items-center"
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
                  className={`p-2 rounded ${
                    page === 1 
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
                
                <div className="text-sm">
                  Page {page} of {totalPages}
                </div>
                
                <button
                  onClick={() => handlePageChange(page + 1)}
                  disabled={page === totalPages}
                  className={`p-2 rounded ${
                    page === totalPages 
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              </div>
              
              {/* Manual page selection - only show if there are 3 or more pages */}
              {totalPages >= 3 && (
                <form onSubmit={handleManualPageChange} className="flex items-center space-x-2">
                  <label htmlFor="pageNumber" className="text-sm text-gray-600">Go to page:</label>
                  <input
                    id="pageNumber"
                    type="number"
                    min="1"
                    max={totalPages}
                    value={manualPage}
                    onChange={(e) => setManualPage(e.target.value)}
                    className="w-16 px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                  <button
                    type="submit"
                    className="px-3 py-1 bg-navy-blue text-white rounded text-sm hover:bg-blue-700"
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
        className="mt-6 px-4 py-2 bg-navy-blue text-white rounded hover:bg-blue-700"
      >
        Back to Dashboard
      </button>
    </div>
  );
};

export default AllQueriesPage; 
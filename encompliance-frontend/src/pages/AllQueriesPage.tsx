import React, { useState, useEffect } from 'react';
import { Clock, MessageSquare } from 'lucide-react';
import api from '../services/api';
import ErrorMessage from '../components/ErrorMessage';
import { formatDateTime } from '../utils/dateUtils';

interface QueryLog {
  id: number;
  query_text?: string;
  response_text?: string;
  created_at?: string;
  query?: string;
  response?: string;
  timestamp?: string;
  conversation_id?: number;
}

interface AllQueriesPageProps {
  navigateTo: (page: string) => void;
}

const AllQueriesPage: React.FC<AllQueriesPageProps> = ({ navigateTo }) => {
  const [queryLogs, setQueryLogs] = useState<QueryLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function getQueryLogs() {
      try {
        console.log('Fetching all query logs...');
        const response = await api.get('/query-logs');
        console.log('Query logs response:', response.data);
        
        if (response.data && response.data.logs) {
          // Transform the data to ensure consistent field names
          const transformedLogs = response.data.logs.map((log: any) => ({
            id: log.id,
            query_text: log.query_text || log.query,
            response_text: log.response_text || log.response,
            created_at: log.created_at || log.timestamp,
            conversation_id: log.conversation_id
          }));
          
          console.log('Transformed logs:', transformedLogs);
          setQueryLogs(transformedLogs);
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
  }, []);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold text-navy-blue mb-6">All Conversations</h1>
      
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin h-8 w-8 border-4 border-navy-blue border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading conversations...</p>
        </div>
      ) : error ? (
        <ErrorMessage message={error} type="error" onClose={() => setError('')} />
      ) : queryLogs.length === 0 ? (
        <div className="text-center py-8 border border-dashed border-gray-300 rounded-lg">
          <MessageSquare className="h-12 w-12 mx-auto text-gray-400 mb-3" />
          <p className="text-gray-600 mb-2">No conversations found</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md p-6">
          <ul className="divide-y divide-gray-200">
            {queryLogs.map((query) => (
              <li key={query.id} className="py-4">
                <div className="flex items-center text-xs text-gray-500 mb-1">
                  <Clock className="h-3 w-3 mr-1" />
                  <span>{formatDateTime(query.created_at || query.timestamp)}</span>
                </div>
                <p className="font-medium mb-2">{query.query_text || query.query}</p>
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
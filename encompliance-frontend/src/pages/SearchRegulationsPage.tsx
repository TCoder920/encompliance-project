import React, { useState, useEffect } from 'react';
import { FileText } from 'lucide-react';
import pdfService, { PDF } from '../services/pdfService';
import AIChat from '../components/AIChat';
import ErrorMessage from '../components/ErrorMessage';
import documentService from '../services/documentService';
import api from '../services/api';

interface SearchRegulationsPageProps {
  navigateTo: (page: string) => void;
  initialQueryId?: number;
  showFullConversation?: boolean;
}

const SearchRegulationsPage: React.FC<SearchRegulationsPageProps> = ({ 
  navigateTo, 
  initialQueryId,
  showFullConversation = false
}) => {
  const [pdfs, setPdfs] = useState<PDF[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPDFs, setSelectedPDFs] = useState<number[]>([]);
  const [selectedPDF, setSelectedPDF] = useState<PDF | null>(null);
  const [showPDFViewer, setShowPDFViewer] = useState(false);
  const [userDocuments, setUserDocuments] = useState<any[]>([]);
  const [allDocumentIds, setAllDocumentIds] = useState<number[]>([]);
  const [initialQueryData, setInitialQueryData] = useState<any>(null);

  // Load initial query data if needed
  useEffect(() => {
    if (initialQueryId) {
      const fetchQueryData = async () => {
        try {
          console.log(`Fetching initial query data for ID: ${initialQueryId}, showFullConversation: ${showFullConversation}`);
          
          // Use the api service instead of direct fetch
          console.log(`Making API request to: /query/${initialQueryId}`);
          const response = await api.get(`/query/${initialQueryId}`);
          
          if (!response.data) {
            console.error('Failed to fetch query details: No data in response');
            setError('Failed to load the conversation data.');
            
            // Create a fallback query data object
            const fallbackData = {
              id: initialQueryId,
              query_text: '',
              response_text: '',
              created_at: new Date().toISOString(),
              document_reference: '',
              conversation_id: null,
              full_conversation: false,
              documentIds: []
            };
            
            console.log('Using fallback query data:', fallbackData);
            setInitialQueryData(fallbackData);
            return;
          }
          
          const data = response.data;
          console.log('Received query data:', JSON.stringify(data));
          
          // If we have document IDs in the response, select them
          if (data.documentIds && Array.isArray(data.documentIds)) {
            console.log('Setting selected PDFs from documentIds:', data.documentIds);
            setSelectedPDFs(data.documentIds);
          }
          
          // For both full conversation and continue conversation, we need to create a proper conversation object
          let conversationData = null;
          
          if (showFullConversation && data.query_text && data.response_text) {
            // For full conversation view, create a conversation with user query and AI response
            console.log('Creating full conversation data');
            conversationData = [
              {
                role: 'user',
                content: data.query_text,
                timestamp: data.created_at
              },
              {
                role: 'assistant',
                content: data.response_text,
                timestamp: data.created_at
              }
            ];
            console.log('Created conversation data:', JSON.stringify(conversationData));
          }
          
          // Transform the data to ensure it has the correct format
          const transformedData = {
            ...data,
            query: data.query_text || data.query,
            response: data.response_text || data.response,
            timestamp: data.created_at || data.timestamp,
            conversation: conversationData
          };
          
          console.log('Transformed query data:', JSON.stringify(transformedData));
          setInitialQueryData(transformedData);
          
        } catch (err) {
          console.error('Error fetching initial query data:', err);
          setError('An error occurred while loading the conversation.');
        }
      };
      
      fetchQueryData();
    }
  }, [initialQueryId, showFullConversation]);

  useEffect(() => {
    // Load PDFs when component mounts
    const loadPDFs = async () => {
      try {
        setIsLoading(true);
        const pdfList = await pdfService.listPDFs();
        setPdfs(pdfList);
        
        // By default, select all PDFs
        const pdfIds = pdfList.map(pdf => pdf.id);
        setSelectedPDFs(pdfIds);
        
        // Load user documents
        const documents = await documentService.listDocuments();
        setUserDocuments(documents);
        console.log("Loaded user documents:", documents.length);
        console.log("User documents:", documents);
        
        // Combine all document IDs for AI context
        const allIds = [...pdfIds, ...documents.map(doc => doc.id)];
        
        // Filter out any undefined, null, or NaN values
        const uniqueIds = Array.from(new Set(allIds))
          .filter(id => id !== undefined && id !== null && !isNaN(id));
          
        console.log("Combined document IDs for AI context:", uniqueIds);
        setAllDocumentIds(uniqueIds);
        
      } catch (err) {
        console.error('Error loading PDFs:', err);
        setError('Failed to load PDFs. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadPDFs();
  }, []);
  
  const handlePDFClick = (pdf: PDF) => {
    setSelectedPDF(pdf);
    setShowPDFViewer(true);
  };
  
  const handleBackToSearch = () => {
    setShowPDFViewer(false);
    setSelectedPDF(null);
  };
  
  // Ensure the Childcare 746 PDF is listed first
  const sortedPDFs = [...pdfs].sort((a, b) => {
    if (a.filename.toLowerCase().includes('746') || a.filename.toLowerCase().includes('childcare')) {
      return -1;
    }
    if (b.filename.toLowerCase().includes('746') || b.filename.toLowerCase().includes('childcare')) {
      return 1;
    }
    return 0;
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-navy-blue dark:text-white mb-6 font-times transition-colors duration-300">Regulations Chat</h1>
      
      {error && (
        <ErrorMessage 
          message={error}
          type="error"
          onClose={() => setError(null)}
        />
      )}
      
      {showPDFViewer && selectedPDF ? (
        <div>
          <button 
            onClick={handleBackToSearch}
            className="bg-navy-blue text-white dark:bg-blue-600 py-2 px-4 rounded mb-4 hover:bg-blue-800 dark:hover:bg-blue-700 transition duration-300"
          >
            ← Back to Chat
          </button>
          <div className="bg-white dark:bg-dark-surface p-6 rounded-lg shadow-md transition-colors duration-300">
            <h2 className="text-xl font-bold text-navy-blue dark:text-white mb-4 transition-colors duration-300">{selectedPDF.filename}</h2>
            <div className="bg-gray-50 dark:bg-gray-800 p-2 rounded-lg transition-colors duration-300">
              <iframe 
                src={`${selectedPDF.filepath}#toolbar=0&navpanes=0`}
                className="w-full h-[800px] border-0 rounded"
                title={selectedPDF.filename}
              />
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1">
            <div className="bg-white dark:bg-dark-surface p-6 rounded-lg shadow-md transition-colors duration-300">
              <h2 className="text-xl font-bold text-navy-blue dark:text-white mb-4 transition-colors duration-300">Reference Documents</h2>
              
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin h-8 w-8 border-4 border-navy-blue dark:border-blue-400 border-t-transparent rounded-full mx-auto mb-4 transition-colors duration-300"></div>
                  <p className="text-gray-600 dark:text-gray-300 transition-colors duration-300">Loading documents...</p>
                </div>
              ) : sortedPDFs.length === 0 ? (
                <div className="text-center py-8 border border-dashed border-gray-300 dark:border-gray-600 rounded-lg transition-colors duration-300">
                  <FileText className="h-12 w-12 mx-auto text-gray-400 dark:text-gray-500 mb-3 transition-colors duration-300" />
                  <p className="text-gray-600 dark:text-gray-300 mb-2 transition-colors duration-300">No documents found</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
                  {sortedPDFs.map((pdf) => (
                    <div 
                      key={pdf.id} 
                      className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors duration-300"
                      onClick={() => handlePDFClick(pdf)}
                    >
                      <div className="flex items-center">
                        <FileText className="h-6 w-6 text-navy-blue dark:text-blue-400 mr-3 transition-colors duration-300" />
                        <div>
                          <p className="font-medium text-gray-800 dark:text-gray-200 transition-colors duration-300">{pdf.filename}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400 transition-colors duration-300">
                            Click to view
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          
          <div className="md:col-span-2">
            <div className="bg-white dark:bg-dark-surface p-6 rounded-lg shadow-md h-full transition-colors duration-300">
              <h2 className="text-xl font-bold text-navy-blue dark:text-white mb-4 transition-colors duration-300">
                {initialQueryId ? 'Full Conversation' : 'Chat Area'}
              </h2>
              <div className="h-[600px] rounded-lg overflow-hidden transition-colors duration-300 border border-gray-200 dark:border-gray-700">
                {initialQueryData && (
                  <div className="text-sm text-gray-500 dark:text-gray-400 p-3 bg-blue-50 dark:bg-blue-900/20 border-b border-gray-200 dark:border-gray-700 transition-colors duration-300">
                    Viewing full conversation for query: "{initialQueryData.query_text || 'Unknown query'}"
                  </div>
                )}
                <AIChat 
                  operationType="daycare" 
                  activePdfIds={allDocumentIds}
                  initialQuery={initialQueryData?.query_text || initialQueryData?.query || ''}
                  initialConversation={showFullConversation && initialQueryData?.conversation ? initialQueryData.conversation : undefined}
                  showFullConversation={showFullConversation}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchRegulationsPage; 
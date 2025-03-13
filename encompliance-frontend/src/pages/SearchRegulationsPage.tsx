import React, { useState, useEffect } from 'react';
import { FileText } from 'lucide-react';
import pdfService, { PDF } from '../services/pdfService';
import AIChat from '../components/AIChat';
import ErrorMessage from '../components/ErrorMessage';

interface SearchRegulationsPageProps {
  navigateTo: (page: string) => void;
}

const SearchRegulationsPage: React.FC<SearchRegulationsPageProps> = ({ navigateTo }) => {
  const [pdfs, setPdfs] = useState<PDF[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPDFs, setSelectedPDFs] = useState<number[]>([]);
  const [selectedPDF, setSelectedPDF] = useState<PDF | null>(null);
  const [showPDFViewer, setShowPDFViewer] = useState(false);

  useEffect(() => {
    // Load PDFs when component mounts
    const loadPDFs = async () => {
      try {
        setIsLoading(true);
        const pdfList = await pdfService.listPDFs();
        setPdfs(pdfList);
        
        // By default, select all PDFs
        setSelectedPDFs(pdfList.map(pdf => pdf.id));
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
      <h1 className="text-3xl font-bold text-navy-blue mb-6 font-times">Search Regulations</h1>
      
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
            className="bg-navy-blue text-white py-2 px-4 rounded mb-4"
          >
            ← Back to Search
          </button>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold text-navy-blue mb-4">{selectedPDF.filename}</h2>
            <iframe 
              src={`${selectedPDF.filepath}#toolbar=0&navpanes=0`}
              className="w-full h-[800px] border-0"
              title={selectedPDF.filename}
            />
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-bold text-navy-blue mb-4">Available Documents</h2>
              
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin h-8 w-8 border-4 border-navy-blue border-t-transparent rounded-full mx-auto mb-4"></div>
                  <p className="text-gray-600">Loading documents...</p>
                </div>
              ) : sortedPDFs.length === 0 ? (
                <div className="text-center py-8 border border-dashed border-gray-300 rounded-lg">
                  <FileText className="h-12 w-12 mx-auto text-gray-400 mb-3" />
                  <p className="text-gray-600 mb-2">No documents found</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {sortedPDFs.map((pdf) => (
                    <div 
                      key={pdf.id} 
                      className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                      onClick={() => handlePDFClick(pdf)}
                    >
                      <div className="flex items-center">
                        <FileText className="h-6 w-6 text-navy-blue mr-3" />
                        <div>
                          <p className="font-medium">{pdf.filename}</p>
                          <p className="text-sm text-gray-500">
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
            <div className="bg-white p-6 rounded-lg shadow-md h-full">
              <h2 className="text-xl font-bold text-navy-blue mb-4">Ask About Regulations</h2>
              <div className="h-[600px]">
                <AIChat 
                  operationType="daycare" 
                  activePdfIds={selectedPDFs}
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
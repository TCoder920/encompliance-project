import React, { useState, useEffect } from 'react';
import { FileText, Download, Trash2, Upload, AlertCircle } from 'lucide-react';
import pdfService, { PDF } from '../services/pdfService';

interface PDFViewerProps {
  onPDFSelect?: (pdf: PDF) => void;
}

const PDFViewer: React.FC<PDFViewerProps> = ({ onPDFSelect }) => {
  const [pdfs, setPdfs] = useState<PDF[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const loadPDFs = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const pdfList = await pdfService.listPDFs();
      setPdfs(pdfList);
    } catch (err) {
      console.error('Error loading PDFs:', err);
      setError('Failed to load PDFs. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPDFs();
  }, []);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      
      // Validate file type
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setError('Only PDF files are allowed.');
        return;
      }
      
      try {
        setIsUploading(true);
        setError(null);
        await pdfService.uploadPDF(file);
        await loadPDFs(); // Reload the PDF list
      } catch (err) {
        console.error('Upload error:', err);
        setError('Failed to upload PDF. Please try again.');
      } finally {
        setIsUploading(false);
        // Reset the file input
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleDownload = async (pdf: PDF) => {
    try {
      const filePath = await pdfService.downloadPDF(pdf.id);
      
      // Create a link to download the file
      const link = document.createElement('a');
      link.href = filePath;
      link.download = pdf.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Download error:', err);
      setError('Failed to download PDF. Please try again.');
    }
  };

  const handleDelete = async (pdf: PDF) => {
    if (window.confirm(`Are you sure you want to delete ${pdf.filename}?`)) {
      try {
        await pdfService.deletePDF(pdf.id);
        await loadPDFs(); // Reload the PDF list
      } catch (err) {
        console.error('Delete error:', err);
        setError('Failed to delete PDF. Please try again.');
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-navy-blue">PDF Documents</h2>
        <div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf"
            className="hidden"
          />
          <button
            onClick={handleUploadClick}
            disabled={isUploading}
            className="flex items-center bg-navy-blue text-white px-4 py-2 rounded hover:bg-blue-800 transition duration-200"
          >
            <Upload className="h-4 w-4 mr-2" />
            {isUploading ? 'Uploading...' : 'Upload PDF'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 flex items-start">
          <AlertCircle className="h-5 w-5 text-red-600 mr-2 mt-0.5" />
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-8">
          <div className="animate-spin h-8 w-8 border-4 border-navy-blue border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading documents...</p>
        </div>
      ) : pdfs.length === 0 ? (
        <div className="text-center py-8 border border-dashed border-gray-300 rounded-lg">
          <FileText className="h-12 w-12 mx-auto text-gray-400 mb-3" />
          <p className="text-gray-600 mb-2">No PDF documents found</p>
          <p className="text-sm text-gray-500">Upload a PDF to get started</p>
        </div>
      ) : (
        <div className="space-y-3">
          {pdfs.map((pdf) => (
            <div 
              key={pdf.id} 
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <div className="flex items-center cursor-pointer" onClick={() => onPDFSelect && onPDFSelect(pdf)}>
                <FileText className="h-6 w-6 text-navy-blue mr-3" />
                <div>
                  <p className="font-medium">{pdf.filename}</p>
                  <p className="text-sm text-gray-500">
                    Uploaded: {new Date(pdf.uploaded_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleDownload(pdf)}
                  className="p-2 text-gray-600 hover:text-navy-blue"
                  title="Download"
                >
                  <Download className="h-5 w-5" />
                </button>
                <button
                  onClick={() => handleDelete(pdf)}
                  className="p-2 text-gray-600 hover:text-red-600"
                  title="Delete"
                >
                  <Trash2 className="h-5 w-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PDFViewer; 
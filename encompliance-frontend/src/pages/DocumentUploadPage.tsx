import React, { useState, useEffect } from 'react';
import { ArrowLeft } from 'lucide-react';
import DocumentUploader from '../components/DocumentUploader';
import ErrorMessage from '../components/ErrorMessage';
import documentService from '../services/documentService';
import * as documentLogger from '../utils/documentLogger';

interface DocumentUploadPageProps {
  navigateTo: (page: string) => void;
}

const DocumentUploadPage: React.FC<DocumentUploadPageProps> = ({ navigateTo }) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedDocumentId, setUploadedDocumentId] = useState<number | null>(null);
  
  // Clear any errors when the component unmounts or when a new upload starts
  useEffect(() => {
    return () => {
      setError(null);
    };
  }, []);

  const handleUploadComplete = async (file: File) => {
    const operation = documentLogger.docStart('documentUpload.handleUploadComplete', { fileName: file.name }) || 'documentUpload';
    documentLogger.docLog('Starting document upload process', { fileName: file.name, fileSize: file.size });
    
    setIsUploading(true);
    setError(null);
    setUploadedFile(file);
    
    try {
      documentLogger.docLog('Calling document service to upload file', { fileName: file.name });
      console.log(`[DEBUG] DocumentUploadPage: Uploading file ${file.name} (${file.size} bytes)`);
      
      const uploadedDoc = await documentService.uploadDocument(file);
      console.log(`[DEBUG] DocumentUploadPage: Upload successful:`, uploadedDoc);
      
      documentLogger.docSuccess('Document uploaded successfully', { documentId: uploadedDoc.id, fileName: file.name });
      
      setUploadedDocumentId(uploadedDoc.id);
      
      // Ensure we clear any cached documents first
      localStorage.removeItem('cachedDocuments');
      console.log(`[DEBUG] DocumentUploadPage: Cleared document cache`);
      
      // Refresh the document list in the background with cache clearing
      try {
        documentLogger.docLog('Forcefully refreshing document cache after upload');
        const refreshedDocs = await documentService.refreshDocumentCache();
        console.log(`[DEBUG] DocumentUploadPage: Cache refresh successful, found ${refreshedDocs.length} documents:`, refreshedDocs);
        documentLogger.docSuccess('Document cache refreshed successfully', { 
          count: refreshedDocs.length,
          documents: refreshedDocs.map(d => ({ id: d.id, filename: d.filename }))
        });
      } catch (refreshError) {
        console.error(`[DEBUG] DocumentUploadPage: Cache refresh error:`, refreshError);
        documentLogger.docWarn('Failed to refresh document cache, but upload was successful', { error: refreshError });
        
        // Try a regular list as fallback
        try {
          documentLogger.docLog('Trying regular document list refresh as fallback');
          const listedDocs = await documentService.listDocuments();
          console.log(`[DEBUG] DocumentUploadPage: List fallback successful, found ${listedDocs.length} documents`);
        } catch (listError) {
          console.error(`[DEBUG] DocumentUploadPage: List fallback error:`, listError);
          documentLogger.docWarn('Regular list refresh also failed', { error: listError });
        }
      }
    } catch (err) {
      console.error(`[DEBUG] DocumentUploadPage: Upload failed:`, err);
      documentLogger.docError('Document upload failed', err);
      setError('Failed to upload the document. Please try again.');
      setUploadedFile(null);
    } finally {
      setIsUploading(false);
      documentLogger.docEnd(operation);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <button 
          onClick={() => {
            documentLogger.docLog('Navigating back to dashboard', { uploadedDocumentId });
            navigateTo('dashboard');
          }} 
          className="flex items-center text-navy-blue hover:text-navy-blue-dark mb-6"
        >
          <ArrowLeft className="h-5 w-5 mr-1" />
          Back to Dashboard
        </button>
        
        <h1 className="text-2xl font-bold text-navy-blue mb-6">Upload Documents</h1>
        
        {error && (
          <ErrorMessage 
            message={error}
            type="error"
            onClose={() => setError(null)}
          />
        )}
        
        {!isUploading && !uploadedFile && (
          <>
            <div className="bg-white shadow-md rounded-lg p-6 mb-8">
              <h2 className="text-xl font-bold text-navy-blue mb-4">Upload a Document</h2>
              <DocumentUploader 
                onUploadComplete={handleUploadComplete}
                allowedFileTypes={['.pdf', '.docx', '.doc', '.txt']}
                maxSizeMB={50}
              />
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-blue-800 mb-3">Document Guidelines</h3>
              <ul className="list-disc pl-5 text-blue-700 space-y-2">
                <li>Upload documents in PDF, Word, or text format</li>
                <li>Maximum file size: 50MB</li>
                <li>For best results, ensure documents are clearly legible</li>
                <li>Documents will be processed to enable search and compliance analysis</li>
              </ul>
            </div>
          </>
        )}
        
        {isUploading && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <div className="animate-pulse text-blue-700 mb-2">Uploading document...</div>
            <div className="text-sm text-blue-600">Please wait while we process your file.</div>
          </div>
        )}
        
        {!isUploading && uploadedFile && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-center text-green-700 mb-2">
              <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="font-medium">Document uploaded successfully!</span>
            </div>
            <p className="text-green-600 mb-2">
              <strong>File:</strong> {uploadedFile.name} ({Math.round(uploadedFile.size / 1024)} KB)
            </p>
            <p className="text-sm text-green-600 mb-4">
              Your document has been uploaded and is now being processed. It will be available in your document library.
            </p>
            <div className="flex space-x-3">
              <button 
                onClick={() => {
                  documentLogger.docLog('Starting new upload after successful upload');
                  setUploadedFile(null);
                  setUploadedDocumentId(null);
                }}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Upload Another Document
              </button>
              <button 
                onClick={() => {
                  documentLogger.docLog('Navigating to dashboard after successful upload', { documentId: uploadedDocumentId });
                  navigateTo('dashboard');
                }}
                className="px-4 py-2 border border-green-600 text-green-600 rounded hover:bg-green-50"
              >
                Return to Dashboard
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default DocumentUploadPage;
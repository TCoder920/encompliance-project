import React, { useState } from 'react';
import { FileText, ArrowLeft } from 'lucide-react';
import DocumentUploader from '../components/DocumentUploader';
import ErrorMessage from '../components/ErrorMessage';

interface DocumentUploadPageProps {
  navigateTo: (page: string) => void;
}

const DocumentUploadPage: React.FC<DocumentUploadPageProps> = ({ navigateTo }) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  
  const handleUploadComplete = (file: File) => {
    try {
      setUploadedFile(file);
      setError(null);
      setIsUploading(false);
      // In a real application, you would process the file here
    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to process the uploaded file. Please try again.');
      setIsUploading(false);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <button 
        onClick={() => navigateTo('dashboard')}
        className="flex items-center text-navy-blue hover:underline mb-6"
      >
        <ArrowLeft className="h-4 w-4 mr-1" />
        Back to Dashboard
      </button>
      
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-navy-blue mb-2 font-times">Document Upload</h1>
        <p className="text-gray-600 mb-8">Upload compliance documents, regulations, or operation manuals for AI analysis and reference.</p>
        
        {error && (
          <div className="mb-4">
            <ErrorMessage 
              message={error}
              type="error"
              onClose={() => setError(null)}
            />
          </div>
        )}
        
        <div className="mb-8">
          <DocumentUploader 
            onUploadComplete={handleUploadComplete}
            allowedFileTypes={['.pdf', '.docx', '.doc', '.txt']}
            maxSizeMB={50}
          />
        </div>
        
        {uploadedFile && (
          <div className="mt-8">
            <h2 className="text-xl font-bold text-navy-blue mb-4">Upload Successful</h2>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start">
                <FileText className="h-6 w-6 text-green-600 mr-3 mt-1" />
                <div>
                  <p className="font-medium">Your document has been uploaded successfully</p>
                  <p className="text-sm text-gray-600 mt-1">
                    File: {uploadedFile.name} ({(uploadedFile.size / 1024 / 1024).toFixed(2)} MB)
                  </p>
                  <p className="text-sm text-gray-600 mt-3">
                    Your document is now being processed. This may take a few minutes depending on the file size.
                    Once processing is complete, the document will be available for reference and AI analysis.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="mt-6 flex justify-end">
              <button
                onClick={() => navigateTo('dashboard')}
                className="bg-navy-blue text-white px-6 py-2 rounded hover:bg-blue-800 transition duration-200"
              >
                Return to Dashboard
              </button>
            </div>
          </div>
        )}
        
        <div className="mt-8 border-t border-gray-200 pt-6">
          <h3 className="font-bold text-navy-blue mb-3">Document Guidelines</h3>
          <ul className="list-disc pl-5 space-y-2 text-gray-700">
            <li>Maximum file size: 50MB</li>
            <li>Supported formats: PDF, Word documents (.docx, .doc), and text files (.txt)</li>
            <li>For best results, ensure documents are properly formatted and contain searchable text</li>
            <li>Scanned documents should be OCR-processed for text recognition</li>
            <li>Confidential information will be securely stored and processed</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default DocumentUploadPage;
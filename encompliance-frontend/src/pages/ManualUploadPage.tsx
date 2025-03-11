import React, { useState } from 'react';
import { FileText, ArrowRight } from 'lucide-react';
import DocumentUploader from '../components/DocumentUploader';
import ErrorMessage from '../components/ErrorMessage';

interface ManualUploadPageProps {
  operationType: string;
  onUploadComplete: () => void;
  onBack: () => void;
  onSkip: () => void;
}

const ManualUploadPage: React.FC<ManualUploadPageProps> = ({ operationType, onUploadComplete, onBack, onSkip }) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUploadComplete = (file: File) => {
    try {
      setUploadedFile(file);
      setIsProcessing(true);
      setError(null);
      
      // Simulate file processing
      setTimeout(() => {
        setIsProcessing(false);
      }, 2000);
    } catch (err) {
      console.error('Upload processing error:', err);
      setError('Failed to process the uploaded file. Please try again.');
      setIsProcessing(false);
    }
  };

  const handleContinue = () => {
    try {
      onUploadComplete();
    } catch (err) {
      console.error('Navigation error:', err);
      setError('Failed to proceed to the next step. Please try again.');
    }
  };

  const handleSkip = () => {
    try {
      onSkip();
    } catch (err) {
      console.error('Skip error:', err);
      setError('Failed to skip this step. Please try again.');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-navy-blue mb-2 font-times">Upload Your Operations Policy</h1>
        <p className="text-gray-600 mb-8">
          Before accessing the regulations, please upload your operation's operational policy for AI-powered analysis and personalized compliance recommendations.
        </p>

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
                  <p className="font-medium">Your operational policy has been uploaded successfully</p>
                  <p className="text-sm text-gray-600 mt-1">
                    File: {uploadedFile.name} ({(uploadedFile.size / 1024 / 1024).toFixed(2)} MB)
                  </p>
                  <p className="text-sm text-gray-600 mt-3">
                    {isProcessing 
                      ? "Your operational policy is being processed..."
                      : "Processing complete! You can now access the compliance tools."}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="mt-6 flex justify-center">
              <button
                onClick={handleContinue}
                disabled={isProcessing}
                className={`${
                  isProcessing 
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-navy-blue hover:bg-blue-800'
                } text-white px-8 py-3 rounded-lg font-semibold flex items-center transition duration-200`}
              >
                {isProcessing ? 'Processing...' : 'Access Compliance Tools'}
                <ArrowRight className="ml-2 h-5 w-5" />
              </button>
            </div>
          </div>
        )}

        <div className="mt-8 border-t border-gray-200 pt-6">
          <h3 className="font-bold text-navy-blue mb-3">Why Upload Your Operational Policy?</h3>
          <ul className="list-disc pl-5 space-y-2 text-gray-700">
            <li>Get personalized compliance recommendations</li>
            <li>Identify potential gaps between your operational policies and current regulations</li>
            <li>Receive AI-powered insights specific to your operation</li>
            <li>Streamline your compliance review process</li>
            <li>Keep your operational policies up-to-date with the latest requirements</li>
          </ul>
        </div>

        <div className="mt-8 pt-6 flex justify-center">
          <button
            onClick={handleSkip}
            className="text-gray-600 hover:text-navy-blue transition duration-200"
          >
            Upload Later
          </button>
        </div>
      </div>
    </div>
  );
};

export default ManualUploadPage;
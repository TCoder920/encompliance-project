import React, { useState, useRef } from 'react';
import { Upload, FileText, X, Check, AlertCircle } from 'lucide-react';
import * as documentLogger from '../utils/documentLogger';
import pdfService from '../services/pdfService';

interface DocumentUploaderProps {
  onUploadComplete?: (file: File) => void;
  allowedFileTypes?: string[];
  maxSizeMB?: number;
}

const DocumentUploader: React.FC<DocumentUploaderProps> = ({
  onUploadComplete,
  allowedFileTypes = ['.pdf', '.docx', '.doc', '.txt'],
  maxSizeMB = 50
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
      documentLogger.docLog('Document drag started', { type: e.type });
    } else if (e.type === 'dragleave') {
      setDragActive(false);
      documentLogger.docLog('Document drag cancelled');
    }
  };

  const validateFile = (file: File): { valid: boolean; error?: string } => {
    documentLogger.docLog('Validating file', { 
      name: file.name, 
      size: file.size, 
      type: file.type 
    });
    
    // Validate file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowedFileTypes.includes(fileExtension)) {
      const error = `File type not allowed. Please upload ${allowedFileTypes.join(', ')} files.`;
      documentLogger.docError('File validation failed: invalid file type', null, { 
        fileExtension, 
        allowedTypes: allowedFileTypes 
      });
      return { valid: false, error };
    }
    
    // Validate file size
    const fileSize = file.size / 1024 / 1024; // Convert to MB
    if (fileSize > maxSizeMB) {
      const error = `File size exceeds ${maxSizeMB}MB limit.`;
      documentLogger.docError('File validation failed: file too large', null, { 
        fileSize: `${fileSize.toFixed(2)}MB`, 
        maxSize: `${maxSizeMB}MB` 
      });
      return { valid: false, error };
    }
    
    documentLogger.docSuccess('File validation passed', { name: file.name });
    return { valid: true };
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    documentLogger.docLog('File dropped on uploader');
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      documentLogger.docLog('Processing dropped file', { fileName: file.name });
      handleFile(file);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      documentLogger.docLog('File selected from file picker', { fileName: file.name });
      handleFile(file);
    }
  };

  const handleFile = async (file: File) => {
    const validation = validateFile(file);
    
    if (!validation.valid) {
      documentLogger.docError('File validation failed in handleFile', null, { error: validation.error });
      setError(validation.error || 'File validation failed');
      return;
    }
    
    setError(null);
    setFile(file);
    setUploading(true);
    
    try {
      // Upload the file using pdfService
      await pdfService.uploadPDF(file);
      documentLogger.docLog('File ready for upload, calling onUploadComplete', { fileName: file.name });
      if (onUploadComplete) {
        onUploadComplete(file);
      }
      // Force refresh of document list after upload
      await pdfService.listPDFs();
      setUploadComplete(true);
    } catch (error) {
      documentLogger.docError('Error in onUploadComplete callback', error);
      setError('An error occurred while processing the file.');
    } finally {
      setUploading(false);
    }
  };

  const handleButtonClick = () => {
    inputRef.current?.click();
  };

  const resetUpload = () => {
    setFile(null);
    setError(null);
    setUploading(false);
    setUploadComplete(false);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' bytes';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  };

  return (
    <div className="w-full">
      {!file ? (
        <div 
          className={`border-2 border-dashed rounded-lg p-6 text-center ${
            dragActive ? 'border-navy-blue bg-blue-50' : 'border-gray-300'
          }`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={inputRef}
            type="file"
            className="hidden"
            onChange={handleChange}
            accept={allowedFileTypes.join(',')}
          />
          
          <Upload className="h-12 w-12 mx-auto text-navy-blue mb-4" />
          
          <h3 className="text-lg font-bold text-navy-blue mb-2">Upload Document</h3>
          
          <p className="text-gray-600 mb-4">
            Drag and drop your file here, or click to browse
          </p>
          
          <button
            onClick={handleButtonClick}
            className="bg-navy-blue text-white px-4 py-2 rounded hover:bg-blue-800 transition duration-200"
          >
            Select File
          </button>
          
          <p className="text-sm text-gray-500 mt-4">
            Supported formats: {allowedFileTypes.join(', ')} (Max size: {maxSizeMB}MB)
          </p>
        </div>
      ) : (
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-navy-blue mr-3" />
              <div>
                <p className="font-medium text-navy-blue">{file.name}</p>
                <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
              </div>
            </div>
            
            {!uploading && !uploadComplete && (
              <button 
                onClick={resetUpload}
                className="text-gray-500 hover:text-red-500"
              >
                <X className="h-5 w-5" />
              </button>
            )}
            
            {uploadComplete && (
              <div className="flex items-center text-green-600">
                <Check className="h-5 w-5 mr-1" />
                <span className="text-sm">Upload complete</span>
              </div>
            )}
          </div>
          
          {uploading && (
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div className="bg-navy-blue h-2.5 rounded-full animate-pulse w-full"></div>
            </div>
          )}
        </div>
      )}
      
      {error && (
        <div className="mt-3 text-red-500 flex items-center">
          <AlertCircle className="h-4 w-4 mr-1" />
          <span className="text-sm">{error}</span>
        </div>
      )}
    </div>
  );
};

export default DocumentUploader;
import React, { useState, useRef } from 'react';
import { Upload, FileText, X, Check, AlertCircle } from 'lucide-react';

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

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateFile = (file: File): boolean => {
    // Check file size
    if (file.size > maxSizeMB * 1024 * 1024) {
      setError(`File size exceeds the ${maxSizeMB}MB limit.`);
      return false;
    }

    // Check file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowedFileTypes.includes(fileExtension)) {
      setError(`File type not supported. Please upload ${allowedFileTypes.join(', ')} files.`);
      return false;
    }

    return true;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    setError(null);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFile(droppedFile)) {
        handleFile(droppedFile);
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    setError(null);
    
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        handleFile(selectedFile);
      }
    }
  };

  const handleFile = (file: File) => {
    setFile(file);
    simulateUpload(file);
  };

  const simulateUpload = (file: File) => {
    setUploading(true);
    
    // Simulate upload process
    setTimeout(() => {
      setUploading(false);
      setUploadComplete(true);
      if (onUploadComplete) {
        onUploadComplete(file);
      }
    }, 2000);
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
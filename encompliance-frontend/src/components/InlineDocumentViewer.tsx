import React, { useState, useEffect } from 'react';

interface InlineDocumentViewerProps {
  documentUrl: string;
  title: string;
  className?: string;
  onError?: () => void;
}

/**
 * A component that displays a document in an iframe
 */
const InlineDocumentViewer: React.FC<InlineDocumentViewerProps> = ({
  documentUrl,
  title,
  className = '',
  onError
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleViewDocument = () => {
    window.open(documentUrl, "_blank"); // Opens in a new tab
  };

  return (
    <div className={`flex flex-col ${className}`}>
      <button 
        onClick={handleViewDocument} 
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition duration-200"
      >
        View Document
      </button>
    </div>
  );
};

export default InlineDocumentViewer; 
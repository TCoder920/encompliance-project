import React, { useState, useEffect } from 'react';
import { Search, ZoomIn, ZoomOut, ChevronLeft, ChevronRight, MessageSquare, X, Upload, Settings } from 'lucide-react';
import AIChat from '../components/AIChat';
import DocumentUploader from '../components/DocumentUploader';
import AIModelSelector from '../components/AIModelSelector';
import ErrorMessage from '../components/ErrorMessage';

interface DocumentViewerPageProps {
  operationType: string;
  navigateTo: (page: string) => void;
}

const DocumentViewerPage: React.FC<DocumentViewerPageProps> = ({ operationType, navigateTo }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [zoomLevel, setZoomLevel] = useState(100);
  const [searchQuery, setSearchQuery] = useState('');
  const [isChatOpen, setIsChatOpen] = useState(true); // Set to true by default
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [selectedAIModel, setSelectedAIModel] = useState('local-model');
  const [showAISettings, setShowAISettings] = useState(false);
  const [activePdfIds, setActivePdfIds] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const totalPages = 150; // Placeholder value
  
  const documentTitle = operationType === 'daycare' 
    ? 'Minimum Standards for Licensed and Registered Child-Care Homes (Chapter 746)' 
    : 'Minimum Standards for General Residential Operations (Chapter 748)';
  
  // Simulate document loading
  useEffect(() => {
    setIsLoading(true);
    setError(null);
    
    // In a real application, this would be a fetch request to load the document
    const timer = setTimeout(() => {
      setIsLoading(false);
      // Uncomment to test error handling:
      // setError('Failed to load document. Please try again later.');
    }, 1500);
    
    return () => clearTimeout(timer);
  }, [operationType]);
  
  const handleZoomIn = () => {
    if (zoomLevel < 200) {
      setZoomLevel(zoomLevel + 10);
    }
  };
  
  const handleZoomOut = () => {
    if (zoomLevel > 50) {
      setZoomLevel(zoomLevel - 10);
    }
  };
  
  const handlePreviousPage = () => {
    try {
      if (currentPage > 1) {
        setCurrentPage(currentPage - 1);
      }
    } catch (err) {
      console.error('Navigation error:', err);
      setError('Could not navigate to the previous page. Please try again.');
    }
  };
  
  const handleNextPage = () => {
    try {
      if (currentPage < totalPages) {
        setCurrentPage(currentPage + 1);
      }
    } catch (err) {
      console.error('Navigation error:', err);
      setError('Could not navigate to the next page. Please try again.');
    }
  };
  
  const handlePageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    try {
      const page = parseInt(e.target.value);
      if (!isNaN(page) && page >= 1 && page <= totalPages) {
        setCurrentPage(page);
      }
    } catch (err) {
      console.error('Page input error:', err);
      setError('Invalid page number. Please enter a valid page number.');
    }
  };
  
  const handleSearch = () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search term');
      return;
    }
    
    setError(null);
    // In a real application, this would trigger a search request
    console.log('Searching for:', searchQuery);
    // Simulate search failure (uncomment to test)
    // setError('No results found for your search query');
  };
  
  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  const toggleUploadModal = () => {
    setIsUploadModalOpen(!isUploadModalOpen);
  };

  const handleUploadComplete = (file: File) => {
    try {
      setUploadedFile(file);
      setError(null);
      // In a real application, you would process the file here
      // For example, sending it to a server or parsing its contents
    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to process the uploaded file. Please try again.');
    }
  };

  const toggleAISettings = () => {
    setShowAISettings(!showAISettings);
  };
  
  // Show loading state
  if (isLoading) {
    return (
      <div className="flex flex-col h-[calc(100vh-64px-72px)] justify-center items-center">
        <div className="animate-pulse text-navy-blue text-xl">Loading document...</div>
      </div>
    );
  }
  
  return (
    <div className="flex flex-col h-[calc(100vh-64px-72px)]">
      {/* Toolbar */}
      <div className="bg-gray-200 p-3 flex items-center justify-between border-b border-gray-300">
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 h-4 w-4" />
            <input
              type="text"
              placeholder="Search document..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-navy-blue focus:border-transparent"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <button 
            onClick={handleSearch}
            className="bg-navy-blue text-white px-3 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Search
          </button>
        </div>
        
        <div className="text-navy-blue font-semibold truncate max-w-md mx-2">
          {documentTitle}
        </div>
        
        <div className="flex items-center space-x-3">
          <button 
            onClick={handleZoomOut}
            className="p-1 hover:bg-gray-300 rounded"
            title="Zoom out"
          >
            <ZoomOut className="h-5 w-5" />
          </button>
          
          <span className="text-sm">{zoomLevel}%</span>
          
          <button 
            onClick={handleZoomIn}
            className="p-1 hover:bg-gray-300 rounded"
            title="Zoom in"
          >
            <ZoomIn className="h-5 w-5" />
          </button>
          
          <div className="flex items-center space-x-1 ml-4">
            <button 
              onClick={handlePreviousPage}
              className="p-1 hover:bg-gray-300 rounded"
              disabled={currentPage === 1}
              title="Previous page"
            >
              <ChevronLeft className={`h-5 w-5 ${currentPage === 1 ? 'text-gray-400' : ''}`} />
            </button>
            
            <div className="flex items-center">
              <input
                type="number"
                min="1"
                max={totalPages}
                value={currentPage}
                onChange={handlePageChange}
                className="w-12 text-center border border-gray-300 rounded-md p-1"
              />
              <span className="mx-1 text-sm">/ {totalPages}</span>
            </div>
            
            <button 
              onClick={handleNextPage}
              className="p-1 hover:bg-gray-300 rounded"
              disabled={currentPage === totalPages}
              title="Next page"
            >
              <ChevronRight className={`h-5 w-5 ${currentPage === totalPages ? 'text-gray-400' : ''}`} />
            </button>
          </div>
          
          <button 
            onClick={toggleUploadModal}
            className="p-1 hover:bg-gray-300 rounded ml-2"
            title="Upload Document"
          >
            <Upload className="h-5 w-5" />
          </button>
          
          <button 
            onClick={toggleChat}
            className={`ml-2 p-2 rounded-full ${isChatOpen ? 'bg-navy-blue text-white' : 'bg-gray-300 hover:bg-gray-400'}`}
            title="AI Compliance Assistant"
          >
            <MessageSquare className="h-5 w-5" />
          </button>
        </div>
      </div>
      
      {error && (
        <div className="mx-4 mt-4">
          <ErrorMessage 
            message={error}
            type="error"
            onClose={() => setError(null)}
          />
        </div>
      )}
      
      {/* Main content area */}
      <div className="flex flex-grow overflow-hidden">
        {/* Document viewer */}
        <div className={`flex-grow overflow-auto bg-gray-100 ${isChatOpen ? 'md:w-2/3' : 'w-full'}`}>
          <div 
            className="mx-auto my-6 bg-white shadow-md p-8 transition-all duration-200"
            style={{ 
              width: `${zoomLevel}%`, 
              maxWidth: '1000px',
              minHeight: '1200px'
            }}
          >
            {operationType === 'daycare' ? (
              /* Daycare document content */
              <div className="mb-8">
                <div className="text-center mb-10 border-b pb-6">
                  <h1 className="text-3xl font-bold mb-4 font-times text-navy-blue">
                    Minimum Standards for Licensed and Registered Child-Care Homes
                  </h1>
                  <p className="text-xl mb-2">Child Care Regulation</p>
                  <p className="text-xl mb-2">Texas Health and Human Services Commission</p>
                  <p className="text-lg mb-2">September 2024</p>
                  <p className="text-sm text-gray-500">Revised: 12/2024</p>
                </div>
                
                <h2 className="text-2xl font-bold mb-6 font-times text-navy-blue border-b pb-2">Table of Contents</h2>
                
                <div className="grid grid-cols-1 gap-4">
                  <div className="mb-2">
                    <p className="text-lg font-semibold text-navy-blue">Table of Contents <span className="text-gray-400 float-right">2</span></p>
                    <p className="text-lg font-semibold text-navy-blue">Introduction <span className="text-gray-400 float-right">5</span></p>
                    <div className="pl-6 mt-1">
                      <p className="flex justify-between"><span>Minimum Standards</span> <span className="text-gray-400">5</span></p>
                      <p className="flex justify-between"><span>Deficiencies</span> <span className="text-gray-400">5</span></p>
                      <p className="flex justify-between"><span>Weights</span> <span className="text-gray-400">5</span></p>
                      <p className="flex justify-between"><span>Maintaining Compliance</span> <span className="text-gray-400">6</span></p>
                      <p className="flex justify-between"><span>The Inspection</span> <span className="text-gray-400">6</span></p>
                      <p className="flex justify-between"><span>Technical Assistance</span> <span className="text-gray-400">6</span></p>
                      <p className="flex justify-between"><span>Investigations</span> <span className="text-gray-400">7</span></p>
                      <p className="flex justify-between"><span>Your Rights and Entitlements</span> <span className="text-gray-400">7</span></p>
                      <p className="flex justify-between"><span>For Further Information</span> <span className="text-gray-400">7</span></p>
                    </div>
                  </div>
                  
                  <div className="mb-2">
                    <p className="text-lg font-semibold text-navy-blue">Subchapter A, Purpose, Scope, and Definitions <span className="text-gray-400 float-right">8</span></p>
                    <div className="pl-6 mt-1">
                      <p className="flex justify-between"><span>Division 1, Purpose</span> <span className="text-gray-400">8</span></p>
                      <p className="flex justify-between"><span>Division 2, Scope</span> <span className="text-gray-400">8</span></p>
                      <p className="flex justify-between"><span>Division 3, Definitions</span> <span className="text-gray-400">11</span></p>
                    </div>
                  </div>
                  
                  <div className="mb-2">
                    <p className="text-lg font-semibold text-navy-blue">Subchapter B, Administration and Communication <span className="text-gray-400 float-right">22</span></p>
                    <div className="pl-6 mt-1">
                      <p className="flex justify-between"><span>Division 1, Primary Caregiver Responsibilities</span> <span className="text-gray-400">22</span></p>
                      <p className="flex justify-between"><span>Division 2, Required Notifications</span> <span className="text-gray-400">27</span></p>
                      <p className="flex justify-between"><span>Division 3, Required Postings</span> <span className="text-gray-400">34</span></p>
                      <p className="flex justify-between"><span>Division 4, Operational Policies</span> <span className="text-gray-400">36</span></p>
                      <p className="flex justify-between"><span>Division 5, Parent Rights</span> <span className="text-gray-400">40</span></p>
                    </div>
                  </div>
                  
                  <div className="mb-2">
                    <p className="text-lg font-semibold text-navy-blue">Subchapter C, Record Keeping <span className="text-gray-400 float-right">42</span></p>
                    <div className="pl-6 mt-1">
                      <p className="flex justify-between"><span>Division 1, Records of Children</span> <span className="text-gray-400">42</span></p>
                      <p className="flex justify-between"><span>Division 2, Records of Accidents and Incidents</span> <span className="text-gray-400">55</span></p>
                      <p className="flex justify-between"><span>Division 3, Records that Must be Kept on File at the Child-Care Home</span> <span className="text-gray-400">58</span></p>
                      <p className="flex justify-between"><span>Division 4, Records on Caregivers and Household Members</span> <span className="text-gray-400">61</span></p>
                    </div>
                  </div>
                  
                  <div className="mb-2">
                    <p className="text-lg font-semibold text-navy-blue">Subchapter D, Personnel <span className="text-gray-400 float-right">65</span></p>
                    <div className="pl-6 mt-1">
                      <p className="flex justify-between">
                        <span>Division 1, Primary Caregiver Qualifications for a Registered Child-Care Home</span> 
                        <span className="text-gray-400">65</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 2, Primary Caregiver Qualifications for a Licensed Child-Care Home</span> 
                        <span className="text-gray-400">69</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 3, Assistant and Substitute Caregivers</span> 
                        <span className="text-gray-400">82</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 4, Professional Development</span> 
                        <span className="text-gray-400">86</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 5, Household Members, Volunteers, and People who Offer Contracted Services</span> 
                        <span className="text-gray-400">107</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 6, General Responsibilities for Caregivers and Household Members</span> 
                        <span className="text-gray-400">110</span>
                      </p>
                    </div>
                  </div>
                  
                  <div className="mb-2">
                    <p className="text-lg font-semibold text-navy-blue">Subchapter E, Child/Caregiver Ratios and Group Sizes <span className="text-gray-400 float-right">114</span></p>
                    <div className="pl-6 mt-1">
                      <p className="flex justify-between">
                        <span>Division 1, Determining Child/Caregiver Ratios and Group Sizes</span> 
                        <span className="text-gray-400">114</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 2, Regular Ratios and Group Sizes in the Registered Child-Care Home</span> 
                        <span className="text-gray-400">117</span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              /* GRO document content */
              <div className="mb-8">
                <div className="text-center mb-10 border-b pb-6">
                  <h1 className="text-3xl font-bold mb-4 font-times text-navy-blue">
                    Minimum Standards for General Residential Operations
                  </h1>
                  <p className="text-xl mb-2">Child Care Regulation</p>
                  <p className="text-xl mb-2">Texas Health and Human Services Commission</p>
                  <p className="text-lg mb-2">August 2024</p>
                  <p className="text-sm text-gray-500">Revised: 09/2024</p>
                </div>
                
                <h2 className="text-2xl font-bold mb-6 font-times text-navy-blue border-b pb-2">Table of Contents</h2>
                
                <div className="grid grid-cols-1 gap-4">
                  <div className="mb-2">
                    <p className="text-lg font-semibold text-navy-blue">Table of Contents <span className="text-gray-400 float-right">2</span></p>
                    <p className="text-lg font-semibold text-navy-blue">Introduction <span className="text-gray-400 float-right">6</span></p>
                    <div className="pl-6 mt-1">
                      <p className="flex justify-between"><span>Minimum Standards</span> <span className="text-gray-400">6</span></p>
                      <p className="flex justify-between"><span>Deficiencies</span> <span className="text-gray-400">6</span></p>
                      <p className="flex justify-between"><span>Weights</span> <span className="text-gray-400">6</span></p>
                      <p className="flex justify-between"><span>Maintaining Compliance</span> <span className="text-gray-400">7</span></p>
                      <p className="flex justify-between"><span>The Inspection</span> <span className="text-gray-400">7</span></p>
                      <p className="flex justify-between"><span>Technical Assistance</span> <span className="text-gray-400">7</span></p>
                      <p className="flex justify-between"><span>Investigations</span> <span className="text-gray-400">8</span></p>
                      <p className="flex justify-between"><span>Your Rights and Entitlements</span> <span className="text-gray-400">8</span></p>
                      <p className="flex justify-between"><span>For Further Information</span> <span className="text-gray-400">8</span></p>
                    </div>
                  </div>
                  
                  <div className="mb-2">
                    <p className="text-lg font-semibold text-navy-blue">Subchapter A, Purpose and Scope <span className="text-gray-400 float-right">9</span></p>
                  </div>
                  
                  <div className="mb-2">
                    <p className="text-lg font-semibold text-navy-blue">Subchapter B, Definitions and Services <span className="text-gray-400 float-right">13</span></p>
                    <div className="pl-6 mt-1">
                      <p className="flex justify-between"><span>Division 1, Definitions</span> <span className="text-gray-400">13</span></p>
                      <p className="flex justify-between"><span>Division 2, Services</span> <span className="text-gray-400">26</span></p>
                      <p className="flex justify-between"><span>Division 3, Care of Unlawfully Present Individuals</span> <span className="text-gray-400">32</span></p>
                    </div>
                  </div>
                  
                  <div className="mb-2">
                    <p className="text-lg font-semibold text-navy-blue">Subchapter C, Organization and Administration <span className="text-gray-400 float-right">35</span></p>
                    <div className="pl-6 mt-1">
                      <p className="flex justify-between">
                        <span>Division 1, Required Plans and Policies, Including During the Application Process</span> 
                        <span className="text-gray-400">35</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 2, Operational Responsibilities and Notifications</span> 
                        <span className="text-gray-400">60</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 3, General Fiscal Requirements</span> 
                        <span className="text-gray-400">66</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 4, Required Postings</span> 
                        <span className="text-gray-400">66</span>
                      </p>
                    </div>
                  </div>
                  
                  <div className="mb-2">
                    <p className="text-lg font-semibold text-navy-blue">Subchapter D, Reports and Record Keeping <span className="text-gray-400 float-right">67</span></p>
                    <div className="pl-6 mt-1">
                      <p className="flex justify-between">
                        <span>Division 1, Reporting Serious Incidents and Other Occurrences</span> 
                        <span className="text-gray-400">67</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 2, Operation Records</span> 
                        <span className="text-gray-400">86</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 3, Personnel Records</span> 
                        <span className="text-gray-400">88</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 4, Child Records</span> 
                        <span className="text-gray-400">91</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 5, Record Retention</span> 
                        <span className="text-gray-400">93</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 6, Unauthorized Absences</span> 
                        <span className="text-gray-400">93</span>
                      </p>
                    </div>
                  </div>
                  
                  <div className="mb-2">
                    <p className="text-lg font-semibold text-navy-blue">Subchapter E, Personnel <span className="text-gray-400 float-right">99</span></p>
                    <div className="pl-6 mt-1">
                      <p className="flex justify-between">
                        <span>Division 1, General Requirements</span> 
                        <span className="text-gray-400">99</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 2, Child-Care Administrator</span> 
                        <span className="text-gray-400">102</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 3, Professional Level Service Providers</span> 
                        <span className="text-gray-400">106</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 4, Treatment Director</span> 
                        <span className="text-gray-400">113</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 5, Caregivers</span> 
                        <span className="text-gray-400">115</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 6, Normalcy</span> 
                        <span className="text-gray-400">118</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 7, Contract Staff and Volunteers</span> 
                        <span className="text-gray-400">121</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 8, Pre-Employment Screening</span> 
                        <span className="text-gray-400">124</span>
                      </p>
                    </div>
                  </div>
                  
                  <div className="mb-2">
                    <p className="text-lg font-semibold text-navy-blue">Subchapter F, Training and Professional Development <span className="text-gray-400 float-right">129</span></p>
                    <div className="pl-6 mt-1">
                      <p className="flex justify-between">
                        <span>Division 1, Definitions</span> 
                        <span className="text-gray-400">129</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 2, Overview of Training and Experience Requirements</span> 
                        <span className="text-gray-400">130</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Division 3, Orientation</span> 
                        <span className="text-gray-400">132</span>
                      </p>
                    </div>
                  </div>
                  
                  <div className="mb-2">
                    <p className="text-lg font-semibold text-navy-blue">Subchapter G, Child/Caregiver Ratios <span className="text-gray-400 float-right">162</span></p>
                  </div>
                  
                  <div className="mb-2">
                    <p className="text-lg font-semibold text-navy-blue">Subchapter H, Child Rights <span className="text-gray-400 float-right">128</span></p>
                  </div>
                </div>
                
                <div className="mt-8 bg-blue-50 p-6 rounded-lg border border-blue-100">
                  <h2 className="text-xl font-bold mb-4 font-times text-navy-blue">Introduction</h2>
                  
                  <h3 className="text-lg font-semibold mb-2 text-navy-blue">Minimum Standards</h3>
                  <p className="mb-4">
                    These minimum standards are developed by the Texas Health and Human Services Commission (HHSC) with the assistance of child-care operations, parents, lawyers, doctors, and other experts in a variety of fields. The standards are also reviewed by the HHSC Council of Families and Advocates and the State Advisory Committee on Child-Care Facilities.
                  </p>
                  
                  <h3 className="text-lg font-semibold mb-2 text-navy-blue">Deficiencies</h3>
                  <p className="mb-4">
                    A deficiency is any failure to comply with a standard, rule, law, specific term of your permit, or condition of your evaluation, corrective action, or probation. During any inspection or investigation, if a deficiency is found, the HHSC inspector will cite the deficiency. You will be notified of the deficiency in writing.
                  </p>
                  
                  <h3 className="text-lg font-semibold mb-2 text-navy-blue">Weights</h3>
                  <p className="mb-4">
                    The minimum standards for general residential operations (GROs) are weighted based on risk to children. The weights are: high, medium-high, medium, medium-low, and low. The higher the weight, the more serious the risk to a child's health or safety if that standard is not met.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* AI Chat panel - Always visible by default */}
        {isChatOpen && (
          <div className="fixed right-0 top-16 bottom-0 w-96 flex flex-col border-l border-gray-200 bg-white z-10">
            {/* AI Settings Toggle */}
            <div className="flex justify-between items-center p-3 border-b border-gray-200">
              <h3 className="font-bold text-navy-blue">AI Assistant</h3>
              <div className="flex items-center space-x-2">
                <button 
                  onClick={toggleAISettings}
                  className="p-1 rounded-full hover:bg-gray-100"
                  aria-label="AI Settings"
                >
                  <Settings size={16} />
                </button>
                <button 
                  onClick={toggleChat}
                  className="p-1 rounded-full hover:bg-gray-100"
                  aria-label="Close chat"
                >
                  <X size={16} />
                </button>
              </div>
            </div>
            
            {/* AI Settings Pane (conditionally shown) */}
            {showAISettings && (
              <AIModelSelector
                selectedModel={selectedAIModel}
                onModelChange={setSelectedAIModel}
              />
            )}
            
            {/* Chat Interface */}
            <AIChat 
              operationType={operationType} 
              selectedModel={selectedAIModel}
              activePdfIds={activePdfIds}
            />
          </div>
        )}
      </div>

      {/* Upload Document Modal */}
      {isUploadModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-navy-blue font-times">Upload Document</h2>
                <button 
                  onClick={toggleUploadModal}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              {!uploadedFile ? (
                <>
                  <p className="text-gray-600 mb-6">
                    Upload your compliance documents, regulations, or operation manuals for AI analysis and reference.
                  </p>
                  
                  <DocumentUploader 
                    onUploadComplete={handleUploadComplete}
                    allowedFileTypes={['.pdf', '.docx', '.doc', '.txt']}
                    maxSizeMB={50}
                  />
                </>
              ) : (
                <div>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                    <div className="flex items-start">
                      <div className="flex-shrink-0 text-green-500 mt-0.5">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <h3 className="text-sm font-medium text-green-800">Upload Successful</h3>
                        <div className="mt-2 text-sm text-green-700">
                          <p>Your document has been uploaded successfully.</p>
                          <p className="mt-1">
                            File: {uploadedFile.name} ({(uploadedFile.size / 1024 / 1024).toFixed(2)} MB)
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <p className="text-gray-600 mb-6">
                    Your document is now being processed. This may take a few minutes depending on the file size.
                    Once processing is complete, the document will be available for reference and AI analysis.
                  </p>
                </div>
              )}
              
              <div className="mt-8 pt-6 border-t border-gray-200">
                <div className="flex justify-end">
                  <button
                    onClick={toggleUploadModal}
                    className="bg-navy-blue text-white px-6 py-2 rounded hover:bg-blue-800 transition duration-200"
                  >
                    {uploadedFile ? "Done" : "Cancel"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentViewerPage;
import React from 'react';
import { Building2, Home } from 'lucide-react';

interface OperationTypePageProps {
  onOperationTypeSelect: (type: string) => void;
}

const OperationTypePage: React.FC<OperationTypePageProps> = ({ onOperationTypeSelect }) => {
  return (
    <div className="container mx-auto px-4 py-12 max-w-2xl">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-navy-blue mb-6 text-center font-times">Select Your Operation Type</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <button
            className="flex flex-col items-center p-6 border border-gray-300 rounded-lg hover:border-navy-blue hover:shadow-md transition duration-200"
            onClick={() => onOperationTypeSelect('daycare')}
          >
            <Home className="h-16 w-16 text-navy-blue mb-4" />
            <h2 className="text-xl font-bold text-navy-blue mb-2">Daycare</h2>
            <p className="text-gray-600 text-center">Minimum Standards for Licensed and Registered Child-Care Homes</p>
            <div className="mt-4 h-16">
              <img 
                src="https://www.hhs.texas.gov/sites/default/files/styles/media_image/public/2022-01/texas-hhs-logo-color.png" 
                alt="Texas Health and Human Services" 
                className="h-full object-contain"
              />
            </div>
          </button>
          
          <button
            className="flex flex-col items-center p-6 border border-gray-300 rounded-lg hover:border-navy-blue hover:shadow-md transition duration-200"
            onClick={() => onOperationTypeSelect('gro')}
          >
            <Building2 className="h-16 w-16 text-navy-blue mb-4" />
            <h2 className="text-xl font-bold text-navy-blue mb-2">GRO/RTC</h2>
            <p className="text-gray-600 text-center">Minimum Standards for General Residential Operations</p>
            <div className="mt-4 h-16">
              <img 
                src="https://www.hhs.texas.gov/sites/default/files/styles/media_image/public/2022-01/texas-hhs-logo-color.png" 
                alt="Texas Health and Human Services" 
                className="h-full object-contain"
              />
            </div>
          </button>
        </div>
        
        <div className="text-center text-gray-600">
          <p>Select the type of operation you manage to access the relevant compliance resources.</p>
        </div>
      </div>
    </div>
  );
};

export default OperationTypePage;
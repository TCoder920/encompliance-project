import React from 'react';
import { Shield } from 'lucide-react';

interface FooterProps {
  navigateTo?: (page: string) => void;
}

const Footer: React.FC<FooterProps> = ({ navigateTo }) => {
  const handleNavigation = (page: string, e: React.MouseEvent) => {
    e.preventDefault();
    if (navigateTo) {
      navigateTo(page);
    }
  };

  return (
    <footer className="bg-navy-blue dark:bg-dark-surface text-white py-6 transition-colors duration-1000">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center mb-4 md:mb-0">
            <Shield className="h-6 w-6 mr-2" />
            <span className="text-lg font-bold font-times">Encompliance.io</span>
          </div>
          
          <div className="text-sm text-gray-300">
            &copy; {new Date().getFullYear()} Encompliance.io. All rights reserved.
          </div>
          
          <div className="mt-4 md:mt-0">
            <ul className="flex space-x-4">
              <li>
                <a 
                  href="#" 
                  onClick={(e) => handleNavigation('terms', e)} 
                  className="hover:text-blue-300"
                >
                  Terms
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  onClick={(e) => handleNavigation('privacy', e)} 
                  className="hover:text-blue-300"
                >
                  Privacy
                </a>
              </li>
              <li>
                <a 
                  href="#" 
                  onClick={(e) => handleNavigation('contact', e)} 
                  className="hover:text-blue-300"
                >
                  Contact
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
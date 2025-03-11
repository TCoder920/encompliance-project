import React, { useState, useEffect } from 'react';
import { Shield, CheckCircle, AlertTriangle, Users, FileCheck, Clock, CheckSquare, AlertCircle, ExternalLink } from 'lucide-react';
import ErrorMessage from '../components/ErrorMessage';

interface HomePageProps {
  navigateTo: (page: string) => void;
}

const HomePage: React.FC<HomePageProps> = ({ navigateTo }) => {
  const [metrics, setMetrics] = useState({
    activeUsers: 2142,
    documentsAnalyzed: 8212,
    complianceQueries: 75565,
    enforcementActions: 56,
    inspectionsPassed: 656
  });

  const [tickerPosition, setTickerPosition] = useState(0);
  const [showTicker, setShowTicker] = useState(true);
  const [startAnimation, setStartAnimation] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initial pause before animation starts
  useEffect(() => {
    const animationTimer = setTimeout(() => {
      setStartAnimation(true);
      setIsLoading(false);
    }, 5000); // 5 second pause

    return () => clearTimeout(animationTimer);
  }, []);

  // Continuous metrics update
  useEffect(() => {
    if (!startAnimation) return;

    try {
      const updateInterval = setInterval(() => {
        setMetrics(prev => ({
          activeUsers: prev.activeUsers + Math.floor(Math.random() * 3), // 0-2 new users
          documentsAnalyzed: prev.documentsAnalyzed + Math.floor(Math.random() * 2), // 0-1 new documents
          complianceQueries: prev.complianceQueries + Math.floor(Math.random() * 5), // 0-4 new queries
          enforcementActions: prev.enforcementActions, // Keep static as it's from official data
          inspectionsPassed: prev.inspectionsPassed // Keep static as it's less frequent
        }));
      }, 3000); // Update every 3 seconds

      return () => clearInterval(updateInterval);
    } catch (err) {
      console.error('Error updating metrics:', err);
      setError('Unable to update metrics data. Please refresh the page.');
    }
  }, [startAnimation]);

  // Ticker animation
  useEffect(() => {
    if (!startAnimation) return;

    try {
      const tickerWidth = 200; // Width of each metric item
      const totalWidth = tickerWidth * 6; // Total width of all metrics (now 6 items with HHS link)
      
      const animate = () => {
        setTickerPosition(prev => {
          const newPosition = prev - 1;
          return newPosition <= -totalWidth ? 0 : newPosition;
        });
      };

      const animation = setInterval(animate, 25);
      return () => clearInterval(animation);
    } catch (err) {
      console.error('Error in ticker animation:', err);
      setError('Display issue detected. Please refresh the page.');
      setShowTicker(false);
    }
  }, [startAnimation]);

  const handleNavigation = (page: string) => {
    try {
      navigateTo(page);
    } catch (err) {
      console.error('Navigation error:', err);
      setError(`Unable to navigate to ${page}. Please try again.`);
    }
  };

  return (
    <div className="flex flex-col items-center">
      {error && (
        <div className="w-full max-w-3xl mx-auto mt-4 px-4">
          <ErrorMessage 
            message={error}
            type="error"
            onClose={() => setError(null)}
          />
        </div>
      )}
      
      {/* Metrics Banner */}
      {showTicker && (
        <div className="w-full bg-red-600 text-white overflow-hidden">
          <div className="py-3 relative">
            {isLoading ? (
              <div className="flex justify-center items-center py-2">
                <span className="animate-pulse">Loading metrics...</span>
              </div>
            ) : (
              <div 
                className="flex whitespace-nowrap transition-transform duration-150"
                style={{ transform: `translateX(${tickerPosition}px)` }}
              >
                <div className="inline-flex items-center px-8">
                  <Users className="h-6 w-6 mr-2" />
                  <span className="text-xl font-bold">{metrics.activeUsers.toLocaleString()}</span>
                  <span className="ml-2">Active Users</span>
                </div>
                
                <div className="inline-flex items-center px-8">
                  <FileCheck className="h-6 w-6 mr-2" />
                  <span className="text-xl font-bold">{metrics.documentsAnalyzed.toLocaleString()}</span>
                  <span className="ml-2">Documents Analyzed</span>
                </div>
                
                <div className="inline-flex items-center px-8">
                  <Clock className="h-6 w-6 mr-2" />
                  <span className="text-xl font-bold">{metrics.complianceQueries.toLocaleString()}</span>
                  <span className="ml-2">Compliance Queries Answered</span>
                </div>

                <div className="inline-flex items-center px-8">
                  <AlertCircle className="h-6 w-6 mr-2" />
                  <span className="text-xl font-bold">{metrics.enforcementActions.toLocaleString()}</span>
                  <span className="ml-2">Enforcement Actions (Past 30 Days)</span>
                </div>

                <div className="inline-flex items-center px-8">
                  <CheckSquare className="h-6 w-6 mr-2" />
                  <span className="text-xl font-bold">{metrics.inspectionsPassed.toLocaleString()}</span>
                  <span className="ml-2">Inspections Passed</span>
                </div>

                <a 
                  href="https://www.hhs.texas.gov/providers/protective-services-providers/child-care-regulation" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-8 hover:text-blue-200"
                >
                  <img 
                    src="https://www.hhs.texas.gov/sites/default/files/styles/media_image/public/2022-01/texas-hhs-logo-color.png" 
                    alt="Texas HHS" 
                    className="h-6 w-auto mr-2 bg-white rounded"
                  />
                  <span className="mr-1">Visit Texas HHS</span>
                  <ExternalLink className="h-4 w-4" />
                </a>

                {/* Duplicate items for seamless scrolling */}
                <div className="inline-flex items-center px-8">
                  <Users className="h-6 w-6 mr-2" />
                  <span className="text-xl font-bold">{metrics.activeUsers.toLocaleString()}</span>
                  <span className="ml-2">Active Users</span>
                </div>
                
                <div className="inline-flex items-center px-8">
                  <FileCheck className="h-6 w-6 mr-2" />
                  <span className="text-xl font-bold">{metrics.documentsAnalyzed.toLocaleString()}</span>
                  <span className="ml-2">Documents Analyzed</span>
                </div>
                
                <div className="inline-flex items-center px-8">
                  <Clock className="h-6 w-6 mr-2" />
                  <span className="text-xl font-bold">{metrics.complianceQueries.toLocaleString()}</span>
                  <span className="ml-2">Compliance Queries Answered</span>
                </div>

                <div className="inline-flex items-center px-8">
                  <AlertCircle className="h-6 w-6 mr-2" />
                  <span className="text-xl font-bold">{metrics.enforcementActions.toLocaleString()}</span>
                  <span className="ml-2">Enforcement Actions (Past 30 Days)</span>
                </div>

                <div className="inline-flex items-center px-8">
                  <CheckSquare className="h-6 w-6 mr-2" />
                  <span className="text-xl font-bold">{metrics.inspectionsPassed.toLocaleString()}</span>
                  <span className="ml-2">Inspections Passed</span>
                </div>

                <a 
                  href="https://www.hhs.texas.gov/providers/protective-services-providers/child-care-regulation" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-8 hover:text-blue-200"
                >
                  <img 
                    src="https://www.hhs.texas.gov/sites/default/files/styles/media_image/public/2022-01/texas-hhs-logo-color.png" 
                    alt="Texas HHS" 
                    className="h-6 w-auto mr-2 bg-white rounded"
                  />
                  <span className="mr-1">Visit Texas HHS</span>
                  <ExternalLink className="h-4 w-4" />
                </a>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Hero Section */}
      <section className="w-full bg-navy-blue text-white py-20 px-4">
        <div className="container mx-auto text-center">
          <Shield className="h-20 w-20 mx-auto mb-6" />
          <h1 className="text-4xl md:text-5xl font-bold font-times mb-6">Encompliance.io</h1>
          <p className="text-xl md:text-2xl mb-8">Texas Daycare and GRO Compliance Made Simple</p>
          <button 
            onClick={() => handleNavigation('signup')}
            className="bg-white text-navy-blue px-8 py-3 rounded font-bold text-lg hover:bg-blue-100 transition duration-200"
          >
            Get Started
          </button>
        </div>
      </section>

      {/* Slogans Section */}
      <section className="w-full py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-gray-50 p-8 rounded shadow-md flex flex-col items-center text-center h-full">
              <div className="bg-navy-blue text-white rounded-full w-12 h-12 flex items-center justify-center mb-4">
                <CheckCircle className="h-6 w-6" />
              </div>
              <h2 className="text-2xl font-bold text-navy-blue mb-4 font-times">Expert Consulting in Seconds</h2>
              <p className="text-gray-700">Get immediate answers to your entire staff with strict adherence to Minimum Standards and Your Policy from our AI-powered agent.</p>
            </div>
            
            <div className="bg-gray-50 p-8 rounded shadow-md flex flex-col items-center text-center h-full">
              <div className="bg-navy-blue text-white rounded-full w-12 h-12 flex items-center justify-center mb-4">
                <Shield className="h-6 w-6" />
              </div>
              <h2 className="text-2xl font-bold text-navy-blue mb-4 font-times">Never Fail an Inspection</h2>
              <p className="text-gray-700">Stay ahead of inspections with comprehensive compliance guidance and checklists.</p>
            </div>
            
            <div className="bg-gray-50 p-8 rounded shadow-md flex flex-col items-center text-center h-full">
              <div className="bg-navy-blue text-white rounded-full w-12 h-12 flex items-center justify-center mb-4">
                <AlertTriangle className="h-6 w-6" />
              </div>
              <h2 className="text-2xl font-bold text-navy-blue mb-4 font-times">Always in Compliance</h2>
              <p className="text-gray-700">Keep your operation up-to-date with the latest regulatory requirements and changes.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="w-full py-16 bg-gray-100">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-navy-blue mb-12 font-times">How It Works</h2>
          
          <div className="max-w-3xl mx-auto space-y-8">
            <div className="flex items-start">
              <div className="bg-navy-blue text-white rounded-full w-10 h-10 flex items-center justify-center flex-shrink-0 mr-4">
                <span className="font-bold">1</span>
              </div>
              <div>
                <h3 className="text-xl font-bold text-navy-blue mb-2">Create Your Account</h3>
                <p className="text-gray-700">Set up your account with basic information about your operation.</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="bg-navy-blue text-white rounded-full w-10 h-10 flex items-center justify-center flex-shrink-0 mr-4">
                <span className="font-bold">2</span>
              </div>
              <div>
                <h3 className="text-xl font-bold text-navy-blue mb-2">Choose Your Operation Type</h3>
                <p className="text-gray-700">Specify whether you operate a Daycare or GRO/RTC facility and upload your operational policy for AI-powered analysis and compliance verification.</p>
              </div>
            </div>
            
            <div className="flex items-start">
              <div className="bg-navy-blue text-white rounded-full w-10 h-10 flex items-center justify-center flex-shrink-0 mr-4">
                <span className="font-bold">3</span>
              </div>
              <div>
                <h3 className="text-xl font-bold text-navy-blue mb-2">Access Compliance Tools</h3>
                <p className="text-gray-700">View regulations, get expert AI guidance on compliance questions, and receive personalized recommendations based on your operational policies.</p>
              </div>
            </div>
          </div>
          
          <div className="text-center mt-12">
            <button 
              onClick={() => handleNavigation('signup')}
              className="bg-navy-blue text-white px-8 py-3 rounded font-bold text-lg hover:bg-blue-800 transition duration-200 mb-8"
            >
              Sign Up Now
            </button>

            <div className="flex justify-center items-center">
              <a 
                href="https://www.hhs.texas.gov/providers/protective-services-providers/child-care-regulation" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center text-navy-blue hover:text-blue-800 transition duration-200"
              >
                <img 
                  src="https://www.hhs.texas.gov/sites/default/files/styles/media_image/public/2022-01/texas-hhs-logo-color.png" 
                  alt="Texas HHS" 
                  className="h-8 w-auto mr-2"
                />
                <span className="font-semibold mr-1">Visit Texas HHS Child Care Regulation</span>
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
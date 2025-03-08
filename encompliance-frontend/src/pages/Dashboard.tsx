import React from 'react';
import { Clock, Search, FileText } from 'lucide-react';

interface DashboardProps {
  navigateTo: (page: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ navigateTo }) => {
  // Mock data for query logs
  const queryLogs = [
    {
      id: 1,
      query: "What's the required ratio for 2-year-olds?",
      timestamp: "Today, 10:23 AM",
      document: "Chapter 746"
    },
    {
      id: 2,
      query: "How many hours of annual training are required?",
      timestamp: "Today, 9:45 AM",
      document: "Chapter 746"
    },
    {
      id: 3,
      query: "What are the background check requirements?",
      timestamp: "Yesterday, 3:12 PM",
      document: "Chapter 746"
    },
    {
      id: 4,
      query: "Do I need a food handler's permit?",
      timestamp: "Yesterday, 1:30 PM",
      document: "Chapter 746"
    },
    {
      id: 5,
      query: "What are the requirements for outdoor play equipment?",
      timestamp: "May 15, 2:45 PM",
      document: "Chapter 746"
    }
  ];
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-navy-blue mb-6 font-times">Owner Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold text-navy-blue mb-4">Quick Access</h2>
          <button 
            onClick={() => navigateTo('documentViewer')}
            className="w-full bg-navy-blue text-white py-2 px-4 rounded mb-3 flex items-center justify-center"
          >
            <FileText className="mr-2 h-5 w-5" />
            View Minimum Standards
          </button>
          <button className="w-full border border-navy-blue text-navy-blue py-2 px-4 rounded mb-3 flex items-center justify-center">
            <Search className="mr-2 h-5 w-5" />
            Search Regulations
          </button>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md md:col-span-2">
          <h2 className="text-xl font-bold text-navy-blue mb-4">Account Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-gray-200 rounded p-4">
              <h3 className="font-bold text-gray-700 mb-2">Operation Type</h3>
              <p>Child-Care Center (Chapter 746)</p>
            </div>
            <div className="border border-gray-200 rounded p-4">
              <h3 className="font-bold text-gray-700 mb-2">State</h3>
              <p>Texas</p>
            </div>
            <div className="border border-gray-200 rounded p-4">
              <h3 className="font-bold text-gray-700 mb-2">Account Status</h3>
              <p className="text-green-600">Active</p>
            </div>
            <div className="border border-gray-200 rounded p-4">
              <h3 className="font-bold text-gray-700 mb-2">Last Login</h3>
              <p>Today, 10:15 AM</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-navy-blue">Recent AI Queries</h2>
          <button className="text-navy-blue hover:underline text-sm">View All</button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Query
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Document
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {queryLogs.map((log) => (
                <tr key={log.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {log.query}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 flex items-center">
                    <Clock className="h-4 w-4 mr-1" />
                    {log.timestamp}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {log.document}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-navy-blue">
                    <button className="hover:underline">View</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
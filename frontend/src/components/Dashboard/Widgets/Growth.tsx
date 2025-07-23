import React from 'react';
import { ArrowTrendingUpIcon, UserPlusIcon } from '@heroicons/react/24/outline';

interface Lead {
  id: string;
  name: string;
  email: string;
  phone: string;
  propertyInterest: string;
  leadDate: string;
  source: string;
}

const mockLeads: Lead[] = [
  {
    id: '1',
    name: 'Sarah Johnson',
    email: 'sarah.j@email.com',
    phone: '(555) 123-4567',
    propertyInterest: 'Sunset Apartments Unit 2A',
    leadDate: '2024-01-15',
    source: 'Website',
  },
  {
    id: '2',
    name: 'Mike Chen',
    email: 'mike.chen@email.com',
    phone: '(555) 987-6543',
    propertyInterest: 'Oak Street House',
    leadDate: '2024-01-14',
    source: 'Referral',
  },
  {
    id: '3',
    name: 'Emily Rodriguez',
    email: 'emily.r@email.com',
    phone: '(555) 456-7890',
    propertyInterest: 'Downtown Loft 5B',
    leadDate: '2024-01-13',
    source: 'Zillow',
  },
  {
    id: '4',
    name: 'David Wilson',
    email: 'david.w@email.com',
    phone: '(555) 321-0987',
    propertyInterest: 'Pine Valley Condo 3C',
    leadDate: '2024-01-12',
    source: 'Facebook',
  },
];

const Growth: React.FC = () => {
  const currentBalance = 45750.25;
  const monthlyGrowth = 12.5; // percentage

  const getSourceColor = (source: string) => {
    switch (source.toLowerCase()) {
      case 'website':
        return 'bg-blue-100 text-blue-800';
      case 'referral':
        return 'bg-green-100 text-green-800';
      case 'zillow':
        return 'bg-purple-100 text-purple-800';
      case 'facebook':
        return 'bg-indigo-100 text-indigo-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white overflow-hidden shadow-sm rounded-lg">
      <div className="p-6">
        <div className="flex items-center mb-6">
          <div className="flex-shrink-0">
            <ArrowTrendingUpIcon className="h-8 w-8 text-green-500" />
          </div>
          <div className="ml-4">
            <h3 className="text-lg font-medium text-gray-900">Growth</h3>
            <div className="flex items-center space-x-2">
              <p className="text-2xl font-bold text-green-600">
                ${currentBalance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </p>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                +{monthlyGrowth}% this month
              </span>
            </div>
            <p className="text-sm text-gray-500">Current account balance</p>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-4">
          <div className="flex items-center mb-4">
            <UserPlusIcon className="h-5 w-5 text-blue-500 mr-2" />
            <h4 className="text-md font-medium text-gray-900">New Leads</h4>
            <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {mockLeads.length} this week
            </span>
          </div>

          <div className="space-y-3 max-h-64 overflow-y-auto">
            {mockLeads.map((lead) => (
              <div key={lead.id} className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h5 className="text-sm font-medium text-gray-900">{lead.name}</h5>
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getSourceColor(lead.source)}`}>
                        {lead.source}
                      </span>
                    </div>
                    <p className="text-xs text-gray-600 mb-1">{lead.email}</p>
                    <p className="text-xs text-gray-600 mb-1">{lead.phone}</p>
                    <p className="text-xs text-gray-500">Interested in: {lead.propertyInterest}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500 mb-2">{lead.leadDate}</p>
                    <div className="space-x-1">
                      <button className="text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700 transition-colors">
                        Contact
                      </button>
                      <button className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded hover:bg-gray-200 transition-colors">
                        View
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-4">
            <button className="bg-green-50 text-green-700 hover:bg-green-100 px-4 py-2 rounded-md text-sm font-medium transition-colors">
              View Financial Report
            </button>
            <button className="bg-blue-50 text-blue-700 hover:bg-blue-100 px-4 py-2 rounded-md text-sm font-medium transition-colors">
              Manage Leads
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Growth;
import React from 'react';
import { DocumentTextIcon } from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface LeaseData {
  month: string;
  offers: number;
  renewals: number;
  moveOuts: number;
  notStarted: number;
}

const leaseData: LeaseData[] = [
  { month: 'Jan', offers: 3, renewals: 8, moveOuts: 2, notStarted: 5 },
  { month: 'Feb', offers: 5, renewals: 12, moveOuts: 4, notStarted: 3 },
  { month: 'Mar', offers: 7, renewals: 15, moveOuts: 6, notStarted: 2 },
  { month: 'Apr', offers: 4, renewals: 10, moveOuts: 3, notStarted: 4 },
  { month: 'May', offers: 6, renewals: 14, moveOuts: 5, notStarted: 1 },
  { month: 'Jun', offers: 8, renewals: 18, moveOuts: 7, notStarted: 2 },
];

const ExpiringLeases: React.FC = () => {
  const currentMonth = leaseData[leaseData.length - 1];
  const totalExpiring = currentMonth.offers + currentMonth.renewals + currentMonth.moveOuts + currentMonth.notStarted;

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900 mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value} leases
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white overflow-hidden shadow-sm rounded-lg">
      <div className="p-6">
        <div className="flex items-center mb-4">
          <div className="flex-shrink-0">
            <DocumentTextIcon className="h-8 w-8 text-purple-500" />
          </div>
          <div className="ml-4">
            <h3 className="text-lg font-medium text-gray-900">Expiring Leases</h3>
            <p className="text-sm text-gray-500">
              {totalExpiring} leases expiring this month
            </p>
          </div>
        </div>

        {/* Current Month Summary */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-blue-50 p-3 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-900">Offers Sent</p>
                <p className="text-2xl font-bold text-blue-600">{currentMonth.offers}</p>
              </div>
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            </div>
          </div>
          <div className="bg-green-50 p-3 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-900">Renewals</p>
                <p className="text-2xl font-bold text-green-600">{currentMonth.renewals}</p>
              </div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
          </div>
          <div className="bg-red-50 p-3 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-red-900">Move-outs</p>
                <p className="text-2xl font-bold text-red-600">{currentMonth.moveOuts}</p>
              </div>
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            </div>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">Not Started</p>
                <p className="text-2xl font-bold text-gray-600">{currentMonth.notStarted}</p>
              </div>
              <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="h-64 mb-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={leaseData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar dataKey="offers" stackId="a" fill="#3B82F6" name="Offers" />
              <Bar dataKey="renewals" stackId="a" fill="#10B981" name="Renewals" />
              <Bar dataKey="moveOuts" stackId="a" fill="#EF4444" name="Move-outs" />
              <Bar dataKey="notStarted" stackId="a" fill="#6B7280" name="Not Started" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Action Items */}
        <div className="space-y-2">
          <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
            <div>
              <p className="text-sm font-medium text-yellow-900">Action Required</p>
              <p className="text-xs text-yellow-700">
                {currentMonth.notStarted} leases need renewal process started
              </p>
            </div>
            <button className="bg-yellow-600 text-white px-3 py-1 rounded text-xs hover:bg-yellow-700 transition-colors">
              Start Process
            </button>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
            <div>
              <p className="text-sm font-medium text-blue-900">Follow Up</p>
              <p className="text-xs text-blue-700">
                {currentMonth.offers} offers pending tenant response
              </p>
            </div>
            <button className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700 transition-colors">
              Follow Up
            </button>
          </div>
        </div>

        <div className="mt-4">
          <button className="w-full bg-purple-50 text-purple-700 hover:bg-purple-100 px-4 py-2 rounded-md text-sm font-medium transition-colors">
            View All Lease Expirations
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExpiringLeases;
import React from 'react';
import { ShieldCheckIcon } from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface InsuranceData {
  name: string;
  value: number;
  color: string;
}

const insuranceData: InsuranceData[] = [
  { name: 'MSI Insured', value: 45, color: '#10B981' },
  { name: '3rd Party Insured', value: 23, color: '#3B82F6' },
  { name: 'Uninsured', value: 12, color: '#EF4444' },
];

const totalRenters = insuranceData.reduce((sum, item) => sum + item.value, 0);

const RentersInsurance: React.FC = () => {
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        fontSize="12"
        fontWeight="bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900">{data.name}</p>
          <p className="text-sm text-gray-600">
            {data.value} renters ({((data.value / totalRenters) * 100).toFixed(1)}%)
          </p>
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
            <ShieldCheckIcon className="h-8 w-8 text-blue-500" />
          </div>
          <div className="ml-4">
            <h3 className="text-lg font-medium text-gray-900">Renters Insurance</h3>
            <p className="text-sm text-gray-500">
              {totalRenters} total renters
            </p>
          </div>
        </div>

        <div className="h-64 mb-4">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={insuranceData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderCustomizedLabel}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {insuranceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Legend and Stats */}
        <div className="space-y-3">
          {insuranceData.map((item) => (
            <div key={item.name} className="flex items-center justify-between">
              <div className="flex items-center">
                <div 
                  className="w-3 h-3 rounded-full mr-3"
                  style={{ backgroundColor: item.color }}
                ></div>
                <span className="text-sm font-medium text-gray-900">{item.name}</span>
              </div>
              <div className="text-right">
                <span className="text-sm font-bold text-gray-900">{item.value}</span>
                <span className="text-xs text-gray-500 ml-1">
                  ({((item.value / totalRenters) * 100).toFixed(1)}%)
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="mt-6 space-y-2">
          <button className="w-full bg-red-50 text-red-700 hover:bg-red-100 px-4 py-2 rounded-md text-sm font-medium transition-colors">
            Contact Uninsured Renters ({insuranceData.find(item => item.name === 'Uninsured')?.value})
          </button>
          <button className="w-full bg-blue-50 text-blue-700 hover:bg-blue-100 px-4 py-2 rounded-md text-sm font-medium transition-colors">
            View Insurance Details
          </button>
        </div>

        {/* Insurance Coverage Summary */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-green-600">
                {((insuranceData.filter(item => item.name !== 'Uninsured').reduce((sum, item) => sum + item.value, 0) / totalRenters) * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500">Coverage Rate</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-600">
                {insuranceData.find(item => item.name === 'MSI Insured')?.value || 0}
              </p>
              <p className="text-xs text-gray-500">MSI Policies</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RentersInsurance;
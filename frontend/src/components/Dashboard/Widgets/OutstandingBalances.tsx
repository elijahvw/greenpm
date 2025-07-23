import React, { useState, useEffect } from 'react';
import { CurrencyDollarIcon } from '@heroicons/react/24/outline';

interface Property {
  id: string;
  name: string;
  address: string;
  amountDue: number;
  daysOverdue: number;
}

const OutstandingBalances: React.FC = () => {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOutstandingBalances = async () => {
      try {
        // TODO: Replace with actual API call
        // const response = await api.get('/api/v1/properties/outstanding-balances');
        // setProperties(response.data);
        setProperties([]);
        setLoading(false);
      } catch (err) {
        setError('Failed to load outstanding balances');
        setLoading(false);
      }
    };

    fetchOutstandingBalances();
  }, []);

  const totalOutstanding = properties.reduce((sum, property) => sum + property.amountDue, 0);

  return (
    <div className="bg-white overflow-hidden shadow-sm rounded-lg">
      <div className="p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <CurrencyDollarIcon className="h-8 w-8 text-red-500" />
          </div>
          <div className="ml-4">
            <h3 className="text-lg font-medium text-gray-900">Outstanding Balances - Rentals</h3>
            <p className="text-2xl font-bold text-red-600">
              ${totalOutstanding.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </p>
          </div>
        </div>
        
        {loading ? (
          <div className="mt-6 flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
          </div>
        ) : error ? (
          <div className="mt-6 text-center text-red-600 text-sm">{error}</div>
        ) : properties.length === 0 ? (
          <div className="mt-6 text-center text-gray-500 text-sm">
            No outstanding balances found
          </div>
        ) : (
          <div className="mt-6">
            <div className="flow-root">
              <ul className="-my-3 divide-y divide-gray-200">
                {properties.map((property) => (
                  <li key={property.id} className="py-3">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {property.name}
                        </p>
                        <p className="text-sm text-gray-500 truncate">
                          {property.address}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-red-600">
                          ${property.amountDue.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                        </p>
                        <p className="text-xs text-gray-500">
                          {property.daysOverdue} days overdue
                        </p>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
        
        <div className="mt-4">
          <button className="w-full bg-red-50 text-red-700 hover:bg-red-100 px-4 py-2 rounded-md text-sm font-medium transition-colors">
            View All Outstanding Balances
          </button>
        </div>
      </div>
    </div>
  );
};

export default OutstandingBalances;
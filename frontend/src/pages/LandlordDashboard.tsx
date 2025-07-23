import React from 'react';
import OutstandingBalances from '../components/Dashboard/Widgets/OutstandingBalances';
import Tasks from '../components/Dashboard/Widgets/Tasks';
import OverdueTasks from '../components/Dashboard/Widgets/OverdueTasks';
import Growth from '../components/Dashboard/Widgets/Growth';
import RentersInsurance from '../components/Dashboard/Widgets/RentersInsurance';
import ExpiringLeases from '../components/Dashboard/Widgets/ExpiringLeases';

const LandlordDashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
            Dashboard
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Welcome back! Here's what's happening with your properties today.
          </p>
        </div>
        <div className="mt-4 flex md:ml-4 md:mt-0">
          <button
            type="button"
            className="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
          >
            Export Report
          </button>
          <button
            type="button"
            className="ml-3 inline-flex items-center rounded-md bg-green-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-green-600"
          >
            Add Property
          </button>
        </div>
      </div>

      {/* Dashboard Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
        {/* Outstanding Balances - Full width on mobile, half on lg, third on xl */}
        <div className="lg:col-span-1">
          <OutstandingBalances />
        </div>

        {/* Tasks - Full width on mobile, half on lg, third on xl */}
        <div className="lg:col-span-1">
          <Tasks />
        </div>

        {/* Overdue Tasks - Full width on mobile, half on lg, third on xl */}
        <div className="lg:col-span-2 xl:col-span-1">
          <OverdueTasks />
        </div>

        {/* Growth - Full width on mobile, half on lg, third on xl */}
        <div className="lg:col-span-1">
          <Growth />
        </div>

        {/* Renters Insurance - Full width on mobile, half on lg, third on xl */}
        <div className="lg:col-span-1">
          <RentersInsurance />
        </div>

        {/* Expiring Leases - Full width on mobile, full on lg, third on xl */}
        <div className="lg:col-span-2 xl:col-span-1">
          <ExpiringLeases />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow-sm rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            <button className="flex flex-col items-center p-4 text-center hover:bg-gray-50 rounded-lg transition-colors">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-2">
                <span className="text-2xl">🏠</span>
              </div>
              <span className="text-sm font-medium text-gray-900">Add Property</span>
            </button>
            
            <button className="flex flex-col items-center p-4 text-center hover:bg-gray-50 rounded-lg transition-colors">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-2">
                <span className="text-2xl">👥</span>
              </div>
              <span className="text-sm font-medium text-gray-900">Add Tenant</span>
            </button>
            
            <button className="flex flex-col items-center p-4 text-center hover:bg-gray-50 rounded-lg transition-colors">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-2">
                <span className="text-2xl">📄</span>
              </div>
              <span className="text-sm font-medium text-gray-900">Create Lease</span>
            </button>
            
            <button className="flex flex-col items-center p-4 text-center hover:bg-gray-50 rounded-lg transition-colors">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mb-2">
                <span className="text-2xl">🔧</span>
              </div>
              <span className="text-sm font-medium text-gray-900">Work Order</span>
            </button>
            
            <button className="flex flex-col items-center p-4 text-center hover:bg-gray-50 rounded-lg transition-colors">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mb-2">
                <span className="text-2xl">💰</span>
              </div>
              <span className="text-sm font-medium text-gray-900">Send Invoice</span>
            </button>
            
            <button className="flex flex-col items-center p-4 text-center hover:bg-gray-50 rounded-lg transition-colors">
              <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-2">
                <span className="text-2xl">📊</span>
              </div>
              <span className="text-sm font-medium text-gray-900">View Reports</span>
            </button>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white shadow-sm rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
        </div>
        <div className="p-6">
          <div className="flow-root">
            <ul className="-mb-8">
              <li>
                <div className="relative pb-8">
                  <span className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
                  <div className="relative flex space-x-3">
                    <div>
                      <span className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center ring-8 ring-white">
                        <span className="text-white text-sm">💰</span>
                      </span>
                    </div>
                    <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                      <div>
                        <p className="text-sm text-gray-500">
                          Payment received from <span className="font-medium text-gray-900">Sarah Johnson</span>
                        </p>
                      </div>
                      <div className="whitespace-nowrap text-right text-sm text-gray-500">
                        <time dateTime="2024-01-15">2 hours ago</time>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
              
              <li>
                <div className="relative pb-8">
                  <span className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
                  <div className="relative flex space-x-3">
                    <div>
                      <span className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center ring-8 ring-white">
                        <span className="text-white text-sm">🔧</span>
                      </span>
                    </div>
                    <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                      <div>
                        <p className="text-sm text-gray-500">
                          Maintenance request submitted for <span className="font-medium text-gray-900">Oak Street House</span>
                        </p>
                      </div>
                      <div className="whitespace-nowrap text-right text-sm text-gray-500">
                        <time dateTime="2024-01-15">4 hours ago</time>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
              
              <li>
                <div className="relative">
                  <div className="relative flex space-x-3">
                    <div>
                      <span className="h-8 w-8 rounded-full bg-purple-500 flex items-center justify-center ring-8 ring-white">
                        <span className="text-white text-sm">📄</span>
                      </span>
                    </div>
                    <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                      <div>
                        <p className="text-sm text-gray-500">
                          Lease renewal sent to <span className="font-medium text-gray-900">Mike Chen</span>
                        </p>
                      </div>
                      <div className="whitespace-nowrap text-right text-sm text-gray-500">
                        <time dateTime="2024-01-15">6 hours ago</time>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandlordDashboard;
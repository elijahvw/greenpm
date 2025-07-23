import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { leaseService } from '../services/leaseService';
import { Lease } from '../types/lease';
import toast from 'react-hot-toast';
import {
  HomeIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  WrenchScrewdriverIcon,
} from '@heroicons/react/24/outline';

const TenantDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [currentLease, setCurrentLease] = useState<Lease | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCurrentLease();
  }, []);

  const fetchCurrentLease = async () => {
    try {
      // For now, get the first active lease for the user
      const leases = await leaseService.getLeases();
      const activeLease = leases.find(lease => 
        lease.status === 'active' && lease.tenant_email === user?.email
      );
      setCurrentLease(activeLease || null);
    } catch (error) {
      console.error('Error fetching lease:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDaysUntilRent = () => {
    const today = new Date();
    const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1);
    const diffTime = nextMonth.getTime() - today.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const getDaysUntilExpiry = () => {
    if (!currentLease?.end_date) return 0;
    const today = new Date();
    const endDate = new Date(currentLease.end_date);
    const diffTime = endDate.getTime() - today.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const daysUntilRent = getDaysUntilRent();
  const daysUntilExpiry = getDaysUntilExpiry();
  const isExpiringSoon = daysUntilExpiry <= 60 && daysUntilExpiry > 0;

  // Button handlers
  const handlePayRent = () => {
    toast.success('Redirecting to rent payment portal...');
    navigate('/dashboard/payments');
  };

  const handleContactLandlord = () => {
    toast.success('Opening message to landlord...');
    navigate('/dashboard/communication');
  };

  const handleMaintenanceRequest = () => {
    toast.success('Opening maintenance request form...');
    navigate('/dashboard/maintenance');
  };

  const handlePaymentHistory = () => {
    navigate('/dashboard/payment-history');
  };

  const handleLeaseDetails = () => {
    navigate('/dashboard/lease');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.first_name}!
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Here's an overview of your rental information.
          </p>
        </div>
      </div>

      {!currentLease ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex">
            <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-yellow-800">No Active Lease</h3>
              <p className="mt-1 text-sm text-yellow-700">
                You don't currently have an active lease. Please contact your landlord.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <>
          {/* Current Lease Overview */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Current Lease</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <HomeIcon className="h-8 w-8 text-blue-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-500">Property</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {currentLease.property_name || 'Your Property'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-500">Monthly Rent</p>
                      <p className="text-lg font-semibold text-gray-900">
                        ${(currentLease.rent_amount || 0).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <CalendarIcon className="h-8 w-8 text-purple-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-500">Lease Ends</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {currentLease.end_date ? 
                          new Date(currentLease.end_date).toLocaleDateString() : 
                          'N/A'
                        }
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <CheckCircleIcon className="h-8 w-8 text-green-500" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-500">Status</p>
                      <p className="text-lg font-semibold text-green-600 capitalize">
                        {currentLease.status || 'Active'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Important Notifications */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Rent Due Notice */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className={`p-2 rounded-lg ${daysUntilRent <= 7 ? 'bg-red-100' : 'bg-blue-100'}`}>
                    <CurrencyDollarIcon className={`h-6 w-6 ${daysUntilRent <= 7 ? 'text-red-600' : 'text-blue-600'}`} />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900">Next Rent Payment</h3>
                    <p className="text-sm text-gray-600">
                      {daysUntilRent <= 7 ? (
                        <span className="text-red-600 font-medium">
                          Due in {daysUntilRent} days
                        </span>
                      ) : (
                        <span>Due in {daysUntilRent} days</span>
                      )}
                    </p>
                  </div>
                </div>
                <div className="mt-4">
                  <button 
                    onClick={handlePayRent}
                    className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                  >
                    Pay Rent - ${(currentLease.rent_amount || 0).toLocaleString()}
                  </button>
                </div>
              </div>
            </div>

            {/* Lease Renewal Notice */}
            {isExpiringSoon && (
              <div className="bg-white shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-center">
                    <div className="p-2 rounded-lg bg-orange-100">
                      <ExclamationTriangleIcon className="h-6 w-6 text-orange-600" />
                    </div>
                    <div className="ml-4">
                      <h3 className="text-lg font-medium text-gray-900">Lease Expiring</h3>
                      <p className="text-sm text-gray-600">
                        <span className="text-orange-600 font-medium">
                          Expires in {daysUntilExpiry} days
                        </span>
                      </p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <button 
                      onClick={handleContactLandlord}
                      className="w-full bg-orange-600 text-white py-2 px-4 rounded-md hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
                    >
                      Contact Landlord About Renewal
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <button 
                  onClick={handleMaintenanceRequest}
                  className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <WrenchScrewdriverIcon className="h-8 w-8 text-blue-600" />
                  <div className="ml-4 text-left">
                    <p className="text-sm font-medium text-gray-900">Request Maintenance</p>
                    <p className="text-xs text-gray-500">Submit a repair request</p>
                  </div>
                </button>

                <button 
                  onClick={handlePaymentHistory}
                  className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
                  <div className="ml-4 text-left">
                    <p className="text-sm font-medium text-gray-900">Payment History</p>
                    <p className="text-xs text-gray-500">View past payments</p>
                  </div>
                </button>

                <button 
                  onClick={handleLeaseDetails}
                  className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <HomeIcon className="h-8 w-8 text-purple-600" />
                  <div className="ml-4 text-left">
                    <p className="text-sm font-medium text-gray-900">Lease Details</p>
                    <p className="text-xs text-gray-500">View lease agreement</p>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default TenantDashboard;
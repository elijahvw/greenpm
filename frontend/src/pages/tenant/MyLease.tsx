import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { leaseService } from '../../services/leaseService';
import { Lease } from '../../types/lease';
import {
  DocumentTextIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  HomeIcon,
  ClockIcon,
  UserIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const MyLease: React.FC = () => {
  const { user } = useAuth();
  const [currentLease, setCurrentLease] = useState<Lease | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCurrentLease();
  }, []);

  const fetchCurrentLease = async () => {
    try {
      const leases = await leaseService.getLeases();
      const activeLease = leases.find(lease => 
        lease.status === 'active' && lease.tenant_email === user?.email
      );
      setCurrentLease(activeLease || null);
    } catch (error) {
      console.error('Error fetching lease:', error);
      toast.error('Failed to load lease information');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getDaysUntilExpiry = () => {
    if (!currentLease?.end_date) return 0;
    const today = new Date();
    const endDate = new Date(currentLease.end_date);
    const diffTime = endDate.getTime() - today.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const daysUntilExpiry = getDaysUntilExpiry();
  const isExpiringSoon = daysUntilExpiry <= 60 && daysUntilExpiry > 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  if (!currentLease) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex">
          <ExclamationTriangleIcon className="h-6 w-6 text-yellow-400 mr-3" />
          <div>
            <h3 className="text-lg font-medium text-yellow-800">No Active Lease</h3>
            <p className="mt-2 text-yellow-700">
              You don't currently have an active lease. Please contact your landlord for assistance.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center">
            <DocumentTextIcon className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <h1 className="text-2xl font-bold text-gray-900">My Lease Agreement</h1>
              <p className="text-sm text-gray-600">View your current lease details</p>
            </div>
          </div>
        </div>
      </div>

      {/* Expiration Warning */}
      {isExpiringSoon && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="flex">
            <ExclamationTriangleIcon className="h-5 w-5 text-orange-400 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-orange-800">Lease Expiring Soon</h3>
              <p className="mt-1 text-sm text-orange-700">
                Your lease expires in {daysUntilExpiry} days. Contact your landlord to discuss renewal options.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Property Information */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Property Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-center">
              <HomeIcon className="h-5 w-5 text-gray-400 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-500">Property</p>
                <p className="text-lg text-gray-900">{currentLease.property_name || 'Property Name'}</p>
              </div>
            </div>
            <div className="flex items-center">
              <UserIcon className="h-5 w-5 text-gray-400 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-500">Landlord</p>
                <p className="text-lg text-gray-900">Contact via Messages</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Lease Terms */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Lease Terms</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-center">
              <CalendarIcon className="h-5 w-5 text-gray-400 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-500">Start Date</p>
                <p className="text-lg text-gray-900">
                  {formatDate(currentLease.start_date || currentLease.startDate || '')}
                </p>
              </div>
            </div>
            <div className="flex items-center">
              <CalendarIcon className="h-5 w-5 text-gray-400 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-500">End Date</p>
                <p className="text-lg text-gray-900">
                  {formatDate(currentLease.end_date || currentLease.endDate || '')}
                </p>
              </div>
            </div>
            <div className="flex items-center">
              <ClockIcon className="h-5 w-5 text-gray-400 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-500">Lease Type</p>
                <p className="text-lg text-gray-900 capitalize">
                  {currentLease.lease_type || currentLease.leaseType || 'Fixed'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Financial Information */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Financial Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-center">
              <CurrencyDollarIcon className="h-5 w-5 text-gray-400 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-500">Monthly Rent</p>
                <p className="text-2xl font-bold text-green-600">
                  ${(currentLease.rent_amount || currentLease.monthlyRent || 0).toLocaleString()}
                </p>
              </div>
            </div>
            <div className="flex items-center">
              <CurrencyDollarIcon className="h-5 w-5 text-gray-400 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-500">Security Deposit</p>
                <p className="text-xl font-semibold text-gray-900">
                  ${(currentLease.security_deposit || currentLease.securityDeposit || 0).toLocaleString()}
                </p>
              </div>
            </div>
            <div className="flex items-center">
              <CurrencyDollarIcon className="h-5 w-5 text-gray-400 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-500">Late Fee</p>
                <p className="text-xl font-semibold text-gray-900">
                  ${(currentLease.late_fee_penalty || currentLease.lateFeePenalty || 0).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Information */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Additional Information</h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium text-gray-500">Status</p>
              <p className="text-lg text-green-600 font-semibold capitalize">{currentLease.status}</p>
            </div>
            {currentLease.notes && (
              <div>
                <p className="text-sm font-medium text-gray-500">Notes</p>
                <p className="text-gray-900">{currentLease.notes}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyLease;
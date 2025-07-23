import React from 'react';
import { Lease } from '../../types/lease';
import { 
  DocumentTextIcon,
  CalendarDaysIcon,
  CurrencyDollarIcon,
  HomeIcon,
  UserIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

interface LeaseCardProps {
  lease: Lease;
  onEdit: (lease: Lease) => void;
  onDelete: (leaseId: string) => void;
  onView: (lease: Lease) => void;
  onRenew?: (lease: Lease) => void;
  onTerminate?: (lease: Lease) => void;
}

const LeaseCard: React.FC<LeaseCardProps> = ({ 
  lease, 
  onEdit, 
  onDelete, 
  onView,
  onRenew,
  onTerminate
}) => {

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'expired':
        return 'bg-red-100 text-red-800';
      case 'terminated':
        return 'bg-gray-100 text-gray-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'draft':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getLeaseTypeDisplay = (type: string) => {
    switch (type) {
      case 'fixed':
        return 'Fixed Term';
      case 'month-to-month':
        return 'Month-to-Month';
      case 'yearly':
        return 'Yearly';
      default:
        return type;
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const getDaysUntilExpiry = () => {
    const endDateStr = lease.endDate || lease.end_date;
    if (!endDateStr) return 0;
    const endDate = new Date(endDateStr);
    const today = new Date();
    const diffTime = endDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const daysUntilExpiry = getDaysUntilExpiry();
  const isExpiringSoon = daysUntilExpiry <= 30 && daysUntilExpiry > 0;
  const isExpired = daysUntilExpiry < 0;

  const getTenantName = () => {
    if (lease.tenant_name) {
      return lease.tenant_name;
    }
    if (lease.tenant) {
      return `${lease.tenant.firstName} ${lease.tenant.lastName}`;
    }
    return 'Unknown Tenant';
  };

  const getPropertyName = () => {
    if (lease.property_name) {
      return lease.property_name;
    }
    if (lease.property) {
      return lease.property.name;
    }
    return 'Unknown Property';
  };

  return (
    <div className="bg-white overflow-hidden shadow-sm rounded-lg hover:shadow-md transition-shadow">
      {/* Lease Header */}
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <DocumentTextIcon className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Lease #{lease.id.slice(-8)}
              </h3>
              <div className="mt-1 flex items-center space-x-2">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(lease.status || 'active')}`}>
                  {lease.status ? lease.status.charAt(0).toUpperCase() + lease.status.slice(1) : 'Active'}
                </span>
                <span className="text-xs text-gray-500">
                  {getLeaseTypeDisplay(lease.leaseType || lease.lease_type || 'fixed')}
                </span>
              </div>
            </div>
          </div>

          {/* Expiry Warning */}
          {isExpiringSoon && (
            <div className="flex items-center text-orange-600">
              <ClockIcon className="h-4 w-4 mr-1" />
              <span className="text-xs font-medium">
                Expires in {daysUntilExpiry} days
              </span>
            </div>
          )}
          {isExpired && (
            <div className="flex items-center text-red-600">
              <ClockIcon className="h-4 w-4 mr-1" />
              <span className="text-xs font-medium">
                Expired {Math.abs(daysUntilExpiry)} days ago
              </span>
            </div>
          )}
        </div>

        {/* Property and Tenant Info */}
        <div className="mt-4 space-y-2">
          <div className="flex items-center text-sm text-gray-600">
            <HomeIcon className="h-4 w-4 mr-2" />
            <span className="font-medium">{getPropertyName()}</span>
          </div>
          
          <div className="flex items-center text-sm text-gray-600">
            <UserIcon className="h-4 w-4 mr-2" />
            <span>{getTenantName()}</span>
          </div>
        </div>

        {/* Lease Terms */}
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div>
            <div className="flex items-center text-sm text-gray-600 mb-1">
              <CalendarDaysIcon className="h-4 w-4 mr-1" />
              <span className="font-medium">Start Date</span>
            </div>
            <p className="text-sm text-gray-900">{formatDate(lease.startDate || lease.start_date || '')}</p>
          </div>

          <div>
            <div className="flex items-center text-sm text-gray-600 mb-1">
              <CalendarDaysIcon className="h-4 w-4 mr-1" />
              <span className="font-medium">End Date</span>
            </div>
            <p className="text-sm text-gray-900">{formatDate(lease.endDate || lease.end_date || '')}</p>
          </div>
        </div>

        {/* Financial Information */}
        <div className="mt-4">
          <div className="flex items-center text-lg font-bold text-green-600 mb-2">
            <CurrencyDollarIcon className="h-5 w-5 mr-1" />
            <span>${(lease.monthlyRent || lease.rent_amount || 0).toLocaleString()}/month</span>
          </div>
          
          <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
            <div>
              <span className="font-medium">Security Deposit:</span>
              <p className="text-gray-900">${(lease.securityDeposit || lease.security_deposit || 0).toLocaleString()}</p>
            </div>
            <div>
              <span className="font-medium">Late Fee:</span>
              <p className="text-gray-900">${(lease.lateFeePenalty || lease.late_fee_penalty || 0).toLocaleString()}</p>
            </div>
          </div>
        </div>

        {/* Pet Policy */}
        {lease.petPolicy && lease.petPolicy.allowed && (
          <div className="mt-4 p-3 bg-blue-50 rounded-md">
            <p className="text-xs font-medium text-blue-700 mb-1">Pet Policy</p>
            <div className="text-sm text-blue-600">
              <p>Deposit: ${lease.petPolicy.deposit || 0}</p>
              {(lease.petPolicy.monthlyFee || 0) > 0 && (
                <p>Monthly Fee: ${lease.petPolicy.monthlyFee}</p>
              )}
            </div>
          </div>
        )}

        {/* Utilities */}
        {lease.utilitiesIncluded && lease.utilitiesIncluded.length > 0 && (
          <div className="mt-4">
            <p className="text-xs font-medium text-gray-700 mb-2">Utilities Included</p>
            <div className="flex flex-wrap gap-1">
              {lease.utilitiesIncluded.slice(0, 3).map((utility, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                >
                  {utility}
                </span>
              ))}
              {lease.utilitiesIncluded.length > 3 && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  +{lease.utilitiesIncluded.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-2 pt-4 border-t border-gray-200 mt-4">
          <button
            onClick={() => onView(lease)}
            className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <EyeIcon className="h-4 w-4 mr-1" />
            View
          </button>
          
          <button
            onClick={() => onEdit(lease)}
            className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <PencilIcon className="h-4 w-4 mr-1" />
            Edit
          </button>
          
          <button
            onClick={() => onDelete(lease.id)}
            className="inline-flex items-center justify-center px-3 py-2 border border-red-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>

        {/* Additional Actions for Active Leases */}
        {lease.status === 'active' && (onRenew || onTerminate) && (
          <div className="flex space-x-2 mt-2">
            {onRenew && (
              <button
                onClick={() => onRenew(lease)}
                className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-green-300 shadow-sm text-sm leading-4 font-medium rounded-md text-green-700 bg-green-50 hover:bg-green-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Renew
              </button>
            )}
            {onTerminate && (
              <button
                onClick={() => onTerminate(lease)}
                className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-orange-300 shadow-sm text-sm leading-4 font-medium rounded-md text-orange-700 bg-orange-50 hover:bg-orange-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
              >
                Terminate
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default LeaseCard;
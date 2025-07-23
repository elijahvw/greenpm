import React from 'react';
import { Lease } from '../../types/lease';
import Modal from '../Common/Modal';
import {
  CalendarIcon,
  CurrencyDollarIcon,
  UserIcon,
  HomeIcon,
  ClockIcon,
  TagIcon,
  PhoneIcon,
  EnvelopeIcon,
} from '@heroicons/react/24/outline';

interface LeaseViewModalProps {
  isOpen: boolean;
  onClose: () => void;
  lease: Lease;
  onEdit?: (lease: Lease) => void;
  onRenew?: (lease: Lease) => void;
  onTerminate?: (lease: Lease) => void;
  onViewProperty?: (propertyId: string) => void;
  onViewTenant?: (tenantId: string) => void;
}

const LeaseViewModal: React.FC<LeaseViewModalProps> = ({
  isOpen,
  onClose,
  lease,
  onEdit,
  onRenew,
  onTerminate,
  onViewProperty,
  onViewTenant
}) => {
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const rentAmount = lease.monthlyRent || lease.rent_amount || 0;
  const securityDeposit = lease.securityDeposit || lease.security_deposit || 0;
  const startDate = lease.startDate || lease.start_date;
  const endDate = lease.endDate || lease.end_date;
  const tenantName = lease.tenant_name || 'Unknown Tenant';
  const propertyName = lease.property_name || 'Unknown Property';

  const getDaysUntilExpiry = () => {
    if (!endDate) return 0;
    const today = new Date();
    const expiry = new Date(endDate);
    const diffTime = expiry.getTime() - today.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const daysUntilExpiry = getDaysUntilExpiry();
  const isExpiringSoon = daysUntilExpiry <= 30 && daysUntilExpiry > 0;
  const isExpired = daysUntilExpiry < 0;

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'expired':
        return 'bg-red-100 text-red-800';
      case 'terminated':
        return 'bg-gray-100 text-gray-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-green-100 text-green-800';
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Lease Details" maxWidth="4xl">
      <div className="space-y-6">
        {/* Lease Header */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex justify-between items-start mb-3">
            <div>
              <h2 className="text-xl font-bold text-gray-900">Lease #{lease.id.slice(-8)}</h2>
              <p className="text-sm text-gray-600 mt-1">{propertyName}</p>
            </div>
            <div className="text-right">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(lease.status)}`}>
                <TagIcon className="h-4 w-4 mr-1" />
                {lease.status ? lease.status.charAt(0).toUpperCase() + lease.status.slice(1) : 'Active'}
              </div>
              {isExpiringSoon && (
                <div className="mt-2 text-xs text-orange-600">
                  <ClockIcon className="h-4 w-4 inline mr-1" />
                  Expires in {daysUntilExpiry} days
                </div>
              )}
              {isExpired && (
                <div className="mt-2 text-xs text-red-600">
                  <ClockIcon className="h-4 w-4 inline mr-1" />
                  Expired {Math.abs(daysUntilExpiry)} days ago
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Tenant Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
              Tenant Information
            </h3>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <UserIcon className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <span className="text-sm font-medium text-gray-500">Name</span>
                    <p className="text-sm text-gray-900">{tenantName}</p>
                  </div>
                </div>
                {onViewTenant && lease.tenant_id && (
                  <button
                    onClick={() => onViewTenant(lease.tenant_id!)}
                    className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                  >
                    View Tenant →
                  </button>
                )}
              </div>
              
              {lease.tenant_email && (
                <div className="flex items-center">
                  <EnvelopeIcon className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <span className="text-sm font-medium text-gray-500">Email</span>
                    <p className="text-sm text-gray-900">{lease.tenant_email}</p>
                  </div>
                </div>
              )}
              
              {lease.tenant_phone && (
                <div className="flex items-center">
                  <PhoneIcon className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <span className="text-sm font-medium text-gray-500">Phone</span>
                    <p className="text-sm text-gray-900">{lease.tenant_phone}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Property Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
              Property Information
            </h3>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <HomeIcon className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <span className="text-sm font-medium text-gray-500">Property</span>
                    <p className="text-sm text-gray-900">{propertyName}</p>
                  </div>
                </div>
                {onViewProperty && lease.property_id && (
                  <button
                    onClick={() => onViewProperty(lease.property_id!)}
                    className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                  >
                    View Property →
                  </button>
                )}
              </div>
              
              {lease.property_address && (
                <div className="flex items-start">
                  <div className="h-5 w-5 text-gray-400 mr-3 mt-0.5">
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Address</span>
                    <p className="text-sm text-gray-900">{lease.property_address}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Lease Terms */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
            Lease Terms
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center">
                <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-sm font-medium text-gray-500">Start Date</span>
              </div>
              <p className="text-lg font-semibold text-gray-900 mt-1">{formatDate(startDate)}</p>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center">
                <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-sm font-medium text-gray-500">End Date</span>
              </div>
              <p className="text-lg font-semibold text-gray-900 mt-1">{formatDate(endDate)}</p>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center">
                <ClockIcon className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-sm font-medium text-gray-500">Lease Type</span>
              </div>
              <p className="text-lg font-semibold text-gray-900 mt-1 capitalize">
                {lease.leaseType || lease.lease_type || 'Fixed'}
              </p>
            </div>
          </div>
        </div>

        {/* Financial Information */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
            Financial Information
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center">
                <CurrencyDollarIcon className="h-5 w-5 text-green-600 mr-2" />
                <span className="text-sm font-medium text-green-700">Monthly Rent</span>
              </div>
              <p className="text-xl font-bold text-green-700 mt-1">${rentAmount.toLocaleString()}</p>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center">
                <CurrencyDollarIcon className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-sm font-medium text-gray-500">Security Deposit</span>
              </div>
              <p className="text-lg font-semibold text-gray-900 mt-1">${securityDeposit.toLocaleString()}</p>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center">
                <CurrencyDollarIcon className="h-5 w-5 text-gray-400 mr-2" />
                <span className="text-sm font-medium text-gray-500">Late Fee</span>
              </div>
              <p className="text-lg font-semibold text-gray-900 mt-1">
                ${(lease.lateFeePenalty || lease.late_fee_penalty || 0).toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between pt-6 border-t border-gray-200">
          <button
            type="button"
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            onClick={onClose}
          >
            Close
          </button>
          
          <div className="flex space-x-3">
            {onEdit && (
              <button
                type="button"
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                onClick={() => {
                  onEdit(lease);
                  onClose();
                }}
              >
                Edit Lease
              </button>
            )}
            
            {onRenew && (lease.status === 'active' || isExpiringSoon) && (
              <button
                type="button"
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                onClick={() => {
                  onRenew(lease);
                  onClose();
                }}
              >
                Renew Lease
              </button>
            )}
            
            {onTerminate && lease.status === 'active' && (
              <button
                type="button"
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                onClick={() => {
                  onTerminate(lease);
                  onClose();
                }}
              >
                Terminate Lease
              </button>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default LeaseViewModal;
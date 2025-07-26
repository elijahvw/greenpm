import React from 'react';
import { Tenant } from '../../types/tenant';
import { Lease } from '../../types/lease';
import { 
  UserIcon, 
  EnvelopeIcon, 
  PhoneIcon,
  BriefcaseIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';

interface TenantCardProps {
  tenant: Tenant;
  leases?: Lease[];
  onEdit: (tenant: Tenant) => void;
  onDelete: (tenantId: string) => void;
  onView: (tenant: Tenant) => void;
}

const TenantCard: React.FC<TenantCardProps> = ({ 
  tenant, 
  leases = [],
  onEdit, 
  onDelete, 
  onView 
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'evicted':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getLeaseStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'expired':
        return 'bg-red-100 text-red-800';
      case 'terminated':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getLeaseStatus = () => {
    if (!leases || leases.length === 0) {
      return { status: 'No Active Lease', color: 'bg-gray-100 text-gray-800' };
    }

    const activeLease = leases.find(lease => lease.status?.toLowerCase() === 'active');
    if (activeLease) {
      return { 
        status: 'Active Lease', 
        color: getLeaseStatusColor('active'),
        property: activeLease.property_name || activeLease.property_address || 'Property'
      };
    }

    const pendingLease = leases.find(lease => lease.status?.toLowerCase() === 'pending');
    if (pendingLease) {
      return { 
        status: 'Pending Lease', 
        color: getLeaseStatusColor('pending'),
        property: pendingLease.property_name || pendingLease.property_address || 'Property'
      };
    }

    const latestLease = leases[0];
    const status = latestLease.status || 'unknown';
    return { 
      status: status.charAt(0).toUpperCase() + status.slice(1),
      color: getLeaseStatusColor(status),
      property: latestLease.property_name || latestLease.property_address || 'Property'
    };
  };

  const formatPhoneNumber = (phone: string) => {
    const cleaned = phone.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
    if (match) {
      return `(${match[1]}) ${match[2]}-${match[3]}`;
    }
    return phone;
  };

  const getFullName = () => {
    return `${tenant.firstName} ${tenant.lastName}`;
  };

  const formatAddress = (address: Tenant['address']) => {
    if (!address) return 'No address provided';
    return `${address.street}, ${address.city}, ${address.state} ${address.zipCode}`;
  };

  return (
    <div className="bg-white overflow-hidden shadow-sm rounded-lg hover:shadow-md transition-shadow">
      {/* Tenant Header */}
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-12 w-12 bg-gray-200 rounded-full flex items-center justify-center">
                <UserIcon className="h-6 w-6 text-gray-500" />
              </div>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">
                {getFullName()}
              </h3>
              <div className="mt-1">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(tenant.status || 'active')}`}>
                  {tenant.status ? tenant.status.charAt(0).toUpperCase() + tenant.status.slice(1) : 'Active'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="mt-4 space-y-2">
          <div className="flex items-center text-sm text-gray-600">
            <EnvelopeIcon className="h-4 w-4 mr-2" />
            <span>{tenant.email}</span>
          </div>
          
          <div className="flex items-center text-sm text-gray-600">
            <PhoneIcon className="h-4 w-4 mr-2" />
            <span>{formatPhoneNumber(tenant.phone)}</span>
          </div>
        </div>

        {/* Lease Status */}
        <div className="mt-4 p-3 bg-gray-50 rounded-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-700">Lease Status</span>
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getLeaseStatus().color}`}>
              {getLeaseStatus().status}
            </span>
          </div>
          {getLeaseStatus().property && getLeaseStatus().status !== 'No Active Lease' && (
            <div className="mt-1">
              <span className="text-xs text-gray-500">{getLeaseStatus().property}</span>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-2 pt-4 border-t border-gray-200 mt-4">
          <button
            onClick={() => onView(tenant)}
            className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <EyeIcon className="h-4 w-4 mr-1" />
            View
          </button>
          
          <button
            onClick={() => onEdit(tenant)}
            className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <PencilIcon className="h-4 w-4 mr-1" />
            Edit
          </button>
          
          <button
            onClick={() => onDelete(tenant.id)}
            className="inline-flex items-center justify-center px-3 py-2 border border-red-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default TenantCard;
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Tenant } from '../types/tenant';
import { tenantService } from '../services/tenantService';
import { leaseService } from '../services/leaseService';
import TenantEditModal from '../components/Tenants/TenantEditModal';
import toast from 'react-hot-toast';
import {
  ArrowLeftIcon,
  UserIcon,
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  BriefcaseIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  DocumentTextIcon,
  PencilIcon,
  HomeIcon,
  BanknotesIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface TenantLease {
  id: string;
  propertyId?: string;
  property_id?: string;
  tenant_id?: string;
  tenantId?: string;
  property_name?: string;
  property_address?: string;
  startDate?: string;
  start_date?: string;
  endDate?: string;
  end_date?: string;
  monthlyRent?: number;
  monthly_rent?: number;
  rent_amount?: number;
  status?: string;
  created_at?: string;
}

const TenantDetail: React.FC = () => {
  const { tenantId } = useParams<{ tenantId: string }>();
  const navigate = useNavigate();
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [leases, setLeases] = useState<TenantLease[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  useEffect(() => {
    if (tenantId) {
      fetchTenantData();
    }
  }, [tenantId]);

  const fetchTenantData = async () => {
    try {
      setLoading(true);
      
      // Fetch tenant details
      const tenantData = await tenantService.getTenant(tenantId!);
      setTenant(tenantData);
      
      // Fetch tenant's leases
      const leasesData = await leaseService.getLeases();
      const tenantLeases = leasesData.filter((lease: any) => 
        lease.tenant_id === tenantId || lease.tenantId === tenantId
      );
      setLeases(tenantLeases);
      
    } catch (error) {
      console.error('Error fetching tenant data:', error);
      toast.error('Failed to load tenant details');
    } finally {
      setLoading(false);
    }
  };

  const handleEditSubmit = async (data: Partial<Tenant>) => {
    try {
      if (!tenant?.id) return;
      
      await tenantService.updateTenant(data as any);
      toast.success('Tenant updated successfully!');
      
      // Refresh tenant data
      await fetchTenantData();
      setIsEditModalOpen(false);
    } catch (error) {
      console.error('Error updating tenant:', error);
      toast.error('Failed to update tenant');
      throw error;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
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

  const formatPhoneNumber = (phone: string) => {
    if (!phone) return 'N/A';
    const cleaned = phone.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
    if (match) {
      return `(${match[1]}) ${match[2]}-${match[3]}`;
    }
    return phone;
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  if (!tenant) {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Tenant not found</h3>
        <p className="mt-1 text-sm text-gray-500">The tenant you're looking for doesn't exist.</p>
        <div className="mt-6">
          <button
            onClick={() => navigate('/dashboard/tenants')}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back to Tenants
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <button
              onClick={() => navigate('/dashboard/tenants')}
              className="mr-4 p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
            >
              <ArrowLeftIcon className="h-5 w-5" />
            </button>
            <div className="flex items-center">
              <div className="h-12 w-12 bg-gray-200 rounded-full flex items-center justify-center mr-4">
                <UserIcon className="h-6 w-6 text-gray-500" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {tenant.firstName} {tenant.lastName}
                </h1>
                <div className="flex items-center mt-1">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(tenant.status || 'active')}`}>
                    {tenant.status ? tenant.status.charAt(0).toUpperCase() + tenant.status.slice(1) : 'Active'}
                  </span>
                  {tenant.moveInDate && (
                    <span className="ml-3 text-sm text-gray-500">
                      Moved in {formatDate(tenant.moveInDate)}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => setIsEditModalOpen(true)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <PencilIcon className="h-4 w-4 mr-2" />
              Edit Tenant
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-8">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: 'Overview', icon: UserIcon },
            { id: 'leases', name: 'Leases', icon: HomeIcon },
            { id: 'payments', name: 'Payments', icon: BanknotesIcon },
            { id: 'documents', name: 'Documents', icon: DocumentTextIcon },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Personal Information */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Information */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Personal Information</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Full Name</dt>
                  <dd className="mt-1 flex items-center text-sm text-gray-900">
                    <UserIcon className="h-4 w-4 mr-2 text-gray-400" />
                    {tenant.firstName} {tenant.lastName}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Email</dt>
                  <dd className="mt-1 flex items-center text-sm text-gray-900">
                    <EnvelopeIcon className="h-4 w-4 mr-2 text-gray-400" />
                    <a href={`mailto:${tenant.email}`} className="text-blue-600 hover:text-blue-800">
                      {tenant.email}
                    </a>
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Phone</dt>
                  <dd className="mt-1 flex items-center text-sm text-gray-900">
                    <PhoneIcon className="h-4 w-4 mr-2 text-gray-400" />
                    <a href={`tel:${tenant.phone}`} className="text-blue-600 hover:text-blue-800">
                      {formatPhoneNumber(tenant.phone)}
                    </a>
                  </dd>
                </div>
                {tenant.dateOfBirth && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Date of Birth</dt>
                    <dd className="mt-1 flex items-center text-sm text-gray-900">
                      <CalendarIcon className="h-4 w-4 mr-2 text-gray-400" />
                      {formatDate(tenant.dateOfBirth)}
                    </dd>
                  </div>
                )}
                <div>
                  <dt className="text-sm font-medium text-gray-500">Status</dt>
                  <dd className="mt-1">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(tenant.status || 'active')}`}>
                      {tenant.status ? tenant.status.charAt(0).toUpperCase() + tenant.status.slice(1) : 'Active'}
                    </span>
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Tenant Since</dt>
                  <dd className="mt-1 flex items-center text-sm text-gray-900">
                    <CalendarIcon className="h-4 w-4 mr-2 text-gray-400" />
                    {formatDate(tenant.createdAt)}
                  </dd>
                </div>
              </div>
            </div>

            {/* Address Information */}
            {tenant.address && (
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Address Information</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div className="sm:col-span-2">
                    <dt className="text-sm font-medium text-gray-500">Current Address</dt>
                    <dd className="mt-1 flex items-start text-sm text-gray-900">
                      <MapPinIcon className="h-4 w-4 mr-2 text-gray-400 mt-0.5" />
                      <div>
                        {tenant.address.street && <div>{tenant.address.street}</div>}
                        <div>
                          {tenant.address.city && `${tenant.address.city}, `}
                          {tenant.address.state && `${tenant.address.state} `}
                          {tenant.address.zipCode}
                        </div>
                        {tenant.address.country && tenant.address.country !== 'US' && (
                          <div>{tenant.address.country}</div>
                        )}
                      </div>
                    </dd>
                  </div>
                </div>
              </div>
            )}

            {/* Lease Information */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Lease Information</h3>
              
              {leases.length > 0 ? (
                <div className="space-y-4">
                  {leases.map((lease, index) => (
                    <div key={lease.id || index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center">
                          <HomeIcon className="h-5 w-5 mr-2 text-gray-400" />
                          <h4 className="text-md font-medium text-gray-900">
                            {lease.property_name || lease.property_address || 'Property'}
                          </h4>
                        </div>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getLeaseStatusColor(lease.status || 'active')}`}>
                          {lease.status ? lease.status.charAt(0).toUpperCase() + lease.status.slice(1) : 'Active'}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                        <div>
                          <dt className="text-gray-500">Start Date</dt>
                          <dd className="text-gray-900 flex items-center">
                            <CalendarIcon className="h-4 w-4 mr-1 text-gray-400" />
                            {(() => {
                              const startDate = lease.startDate || lease.start_date;
                              return startDate ? formatDate(startDate) : 'N/A';
                            })()}
                          </dd>
                        </div>
                        <div>
                          <dt className="text-gray-500">End Date</dt>
                          <dd className="text-gray-900 flex items-center">
                            <CalendarIcon className="h-4 w-4 mr-1 text-gray-400" />
                            {(() => {
                              const endDate = lease.endDate || lease.end_date;
                              return endDate ? formatDate(endDate) : 'N/A';
                            })()}
                          </dd>
                        </div>
                        <div>
                          <dt className="text-gray-500">Monthly Rent</dt>
                          <dd className="text-gray-900 flex items-center">
                            <CurrencyDollarIcon className="h-4 w-4 mr-1 text-gray-400" />
                            {(() => {
                              const rentAmount = lease.monthlyRent || lease.monthly_rent || lease.rent_amount;
                              return rentAmount ? formatCurrency(rentAmount) : 'N/A';
                            })()}
                          </dd>
                        </div>
                        <div>
                          <dt className="text-gray-500">Lease Duration</dt>
                          <dd className="text-gray-900 flex items-center">
                            <ClockIcon className="h-4 w-4 mr-1 text-gray-400" />
                            {(() => {
                              const startDate = lease.startDate || lease.start_date;
                              const endDate = lease.endDate || lease.end_date;
                              if (startDate && endDate) {
                                const months = Math.ceil((new Date(endDate).getTime() - new Date(startDate).getTime()) / (1000 * 60 * 60 * 24 * 30));
                                return `${months} months`;
                              }
                              return 'N/A';
                            })()}
                          </dd>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {/* Summary */}
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <dt className="text-gray-500">Active Leases</dt>
                        <dd className="text-gray-900 font-medium">
                          {leases.filter(lease => lease.status?.toLowerCase() === 'active').length}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-gray-500">Total Leases</dt>
                        <dd className="text-gray-900 font-medium">
                          {leases.length}
                        </dd>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-6">
                  <HomeIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No leases found</h3>
                  <p className="mt-1 text-sm text-gray-500">This tenant doesn't have any lease agreements yet.</p>
                </div>
              )}
            </div>

            {/* Employment Information */}
            {tenant.employment && (
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Employment Information</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Employer</dt>
                    <dd className="mt-1 flex items-center text-sm text-gray-900">
                      <BriefcaseIcon className="h-4 w-4 mr-2 text-gray-400" />
                      {tenant.employment.employer}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Position</dt>
                    <dd className="mt-1 flex items-center text-sm text-gray-900">
                      <BriefcaseIcon className="h-4 w-4 mr-2 text-gray-400" />
                      {tenant.employment.position}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Monthly Income</dt>
                    <dd className="mt-1 flex items-center text-sm text-gray-900">
                      <CurrencyDollarIcon className="h-4 w-4 mr-2 text-gray-400" />
                      {formatCurrency(tenant.employment.monthlyIncome || 0)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Annual Income</dt>
                    <dd className="mt-1 flex items-center text-sm text-gray-900">
                      <CurrencyDollarIcon className="h-4 w-4 mr-2 text-gray-400" />
                      {formatCurrency((tenant.employment.monthlyIncome || 0) * 12)}
                    </dd>
                  </div>
                  {tenant.employment.employmentStartDate && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Employment Start Date</dt>
                      <dd className="mt-1 flex items-center text-sm text-gray-900">
                        <CalendarIcon className="h-4 w-4 mr-2 text-gray-400" />
                        {formatDate(tenant.employment.employmentStartDate)}
                      </dd>
                    </div>
                  )}
                  {tenant.employment.monthlyIncome && tenant.currentRent && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Income to Rent Ratio</dt>
                      <dd className="mt-1 flex items-center text-sm text-gray-900">
                        <CurrencyDollarIcon className="h-4 w-4 mr-2 text-gray-400" />
                        {((tenant.employment.monthlyIncome / tenant.currentRent) * 100).toFixed(0)}% 
                        <span className="ml-1 text-xs text-gray-500">
                          ({tenant.employment.monthlyIncome >= tenant.currentRent * 3 ? 'Good' : 'Low'})
                        </span>
                      </dd>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Notes */}
            {tenant.notes && (
              <div className="bg-white shadow rounded-lg p-6 mt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Notes</h3>
                <p className="text-sm text-gray-600">{tenant.notes}</p>
              </div>
            )}
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Stats</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Account Status</span>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(tenant.status || 'active')}`}>
                    {tenant.status ? tenant.status.charAt(0).toUpperCase() + tenant.status.slice(1) : 'Active'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Total Leases</span>
                  <span className="text-sm font-medium text-gray-900">{leases.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Active Leases</span>
                  <span className="text-sm font-medium text-gray-900">
                    {leases.filter(lease => lease.status?.toLowerCase() === 'active').length}
                  </span>
                </div>
                {tenant.employment?.monthlyIncome && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Monthly Income</span>
                    <span className="text-sm font-medium text-gray-900">
                      {formatCurrency(tenant.employment.monthlyIncome)}
                    </span>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Tenant Since</span>
                  <span className="text-sm font-medium text-gray-900">
                    {new Date(tenant.createdAt).toLocaleDateString('en-US', { 
                      month: 'short', 
                      year: 'numeric' 
                    })}
                  </span>
                </div>
              </div>
            </div>

            {/* Emergency Contact */}
            {tenant.emergencyContact && (
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Emergency Contact</h3>
                <div className="space-y-3">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Name</dt>
                    <dd className="mt-1 flex items-center text-sm text-gray-900">
                      <UserIcon className="h-4 w-4 mr-2 text-gray-400" />
                      {tenant.emergencyContact.name}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Relationship</dt>
                    <dd className="mt-1 text-sm text-gray-900 ml-6">
                      {tenant.emergencyContact.relationship}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Phone</dt>
                    <dd className="mt-1 flex items-center text-sm text-gray-900">
                      <PhoneIcon className="h-4 w-4 mr-2 text-gray-400" />
                      <a href={`tel:${tenant.emergencyContact.phone}`} className="text-blue-600 hover:text-blue-800">
                        {formatPhoneNumber(tenant.emergencyContact.phone)}
                      </a>
                    </dd>
                  </div>
                </div>
              </div>
            )}

            {/* Account Information */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Account Information</h3>
              <div className="space-y-3">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Tenant ID</dt>
                  <dd className="mt-1 text-sm text-gray-900 font-mono">#{tenant.id}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Created</dt>
                  <dd className="mt-1 flex items-center text-sm text-gray-900">
                    <CalendarIcon className="h-4 w-4 mr-2 text-gray-400" />
                    {formatDate(tenant.createdAt)}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                  <dd className="mt-1 flex items-center text-sm text-gray-900">
                    <CalendarIcon className="h-4 w-4 mr-2 text-gray-400" />
                    {formatDate(tenant.updatedAt)}
                  </dd>
                </div>
                {tenant.socialSecurityNumber && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">SSN</dt>
                    <dd className="mt-1 text-sm text-gray-900 font-mono">
                      ***-**-{tenant.socialSecurityNumber.slice(-4)}
                    </dd>
                  </div>
                )}
              </div>
            </div>

            {/* Documents Summary */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Documents</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Total Documents</span>
                  <span className="text-sm font-medium text-gray-900">
                    {tenant.documents?.length || 0}
                  </span>
                </div>
                <div className="text-center py-4">
                  <DocumentTextIcon className="mx-auto h-8 w-8 text-gray-400" />
                  <p className="mt-2 text-xs text-gray-500">
                    Document management coming soon
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Leases Tab */}
      {activeTab === 'leases' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">Lease History</h3>
            <div className="text-sm text-gray-500">
              {leases.length} lease{leases.length !== 1 ? 's' : ''} found
            </div>
          </div>
          
          {leases.length === 0 ? (
            <div className="text-center py-12 bg-white shadow rounded-lg">
              <HomeIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No leases found</h3>
              <p className="mt-1 text-sm text-gray-500">This tenant doesn't have any leases yet.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {leases.map((lease) => (
                <div key={lease.id} className="bg-white shadow rounded-lg p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <h4 className="text-lg font-medium text-gray-900">
                          {lease.property_name || `Property #${lease.propertyId || lease.property_id || 'Unknown'}`}
                        </h4>
                        <span className={`ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getLeaseStatusColor(lease.status || 'unknown')}`}>
                          {(lease.status || 'unknown').charAt(0).toUpperCase() + (lease.status || 'unknown').slice(1)}
                        </span>
                      </div>
                      {lease.property_address && (
                        <p className="mt-1 text-sm text-gray-600">{lease.property_address}</p>
                      )}
                      <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div>
                          <dt className="text-sm font-medium text-gray-500">Start Date</dt>
                          <dd className="mt-1 text-sm text-gray-900">
                            {(lease.startDate || lease.start_date) ? formatDate(lease.startDate || lease.start_date!) : 'N/A'}
                          </dd>
                        </div>
                        <div>
                          <dt className="text-sm font-medium text-gray-500">End Date</dt>
                          <dd className="mt-1 text-sm text-gray-900">
                            {(lease.endDate || lease.end_date) ? formatDate(lease.endDate || lease.end_date!) : 'N/A'}
                          </dd>
                        </div>
                        <div>
                          <dt className="text-sm font-medium text-gray-500">Monthly Rent</dt>
                          <dd className="mt-1 text-sm text-gray-900">
                            {formatCurrency(lease.monthlyRent || lease.monthly_rent || lease.rent_amount || 0)}
                          </dd>
                        </div>
                        <div>
                          <dt className="text-sm font-medium text-gray-500">Lease Duration</dt>
                          <dd className="mt-1 text-sm text-gray-900">
                            {(() => {
                              const startDate = lease.startDate || lease.start_date;
                              const endDate = lease.endDate || lease.end_date;
                              if (startDate && endDate) {
                                const start = new Date(startDate);
                                const end = new Date(endDate);
                                const months = Math.round((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24 * 30.44));
                                return `${months} months`;
                              }
                              return 'N/A';
                            })()}
                          </dd>
                        </div>
                      </div>
                      
                      {/* Additional lease details */}
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs text-gray-500">
                          <div>
                            <span className="font-medium">Lease ID:</span> #{lease.id}
                          </div>
                          {lease.created_at && (
                            <div>
                              <span className="font-medium">Created:</span> {formatDate(lease.created_at)}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Payments Tab */}
      {activeTab === 'payments' && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Payment History</h3>
          <div className="text-center py-12">
            <BanknotesIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Payment history coming soon</h3>
            <p className="mt-1 text-sm text-gray-500">
              Payment tracking functionality will be available in a future update.
            </p>
          </div>
        </div>
      )}

      {/* Documents Tab */}
      {activeTab === 'documents' && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Documents</h3>
          <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Document management coming soon</h3>
            <p className="mt-1 text-sm text-gray-500">
              Document upload and management functionality will be available in a future update.
            </p>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {tenant && (
        <TenantEditModal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          tenant={tenant}
          onSubmit={handleEditSubmit}
        />
      )}
    </div>
  );
};

export default TenantDetail;
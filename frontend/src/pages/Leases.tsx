import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Lease, CreateLeaseRequest, UpdateLeaseRequest } from '../types/lease';
import { leaseService } from '../services/leaseService';
import { securityDepositService } from '../services/securityDepositService';
import { propertyService } from '../services/propertyService';
import { Property } from '../types/property';
import { CreateSecurityDepositRequest } from '../types/securityDeposit';
import LeaseCard from '../components/Leases/LeaseCard';
import LeaseViewModal from '../components/Leases/LeaseViewModal';
import LeaseRenewalModal from '../components/Leases/LeaseRenewalModal';
import LeaseTerminationModal from '../components/Leases/LeaseTerminationModal';
import LeaseEditModal from '../components/Leases/LeaseEditModal';
import LeaseCreateModal from '../components/Leases/LeaseCreateModal';
import { PlusIcon, MagnifyingGlassIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const Leases: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [leases, setLeases] = useState<Lease[]>([]);
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [propertyFilter, setPropertyFilter] = useState<string>(
    searchParams.get('propertyId') || 'all'
  );

  // Modal states
  const [viewingLease, setViewingLease] = useState<Lease | undefined>();
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [editingLease, setEditingLease] = useState<Lease | undefined>();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [renewingLease, setRenewingLease] = useState<Lease | undefined>();
  const [isRenewalModalOpen, setIsRenewalModalOpen] = useState(false);
  const [terminatingLease, setTerminatingLease] = useState<Lease | undefined>();
  const [isTerminationModalOpen, setIsTerminationModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  useEffect(() => {
    fetchLeases();
    fetchProperties();
  }, []);

  const fetchProperties = async () => {
    try {
      const data = await propertyService.getProperties();
      setProperties(data);
    } catch (error) {
      console.error('Error fetching properties:', error);
    }
  };

  const fetchLeases = async () => {
    try {
      setLoading(true);
      console.log('📝 Leases - Fetching leases...');
      const data = await leaseService.getLeases();
      console.log('📝 Leases - Fetched data:', data);
      setLeases(data);
      console.log('📝 Leases - Set leases state:', data);
    } catch (error) {
      console.error('❌ Leases - Error fetching leases:', error);
      toast.error('Failed to load leases');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteLease = async (leaseId: string) => {
    if (!window.confirm('Are you sure you want to delete this lease? This action cannot be undone.')) {
      return;
    }

    try {
      await leaseService.deleteLease(leaseId);
      setLeases(leases.filter(l => l.id !== leaseId));
      toast.success('Lease deleted successfully');
    } catch (error) {
      console.error('Error deleting lease:', error);
      toast.error('Failed to delete lease');
    }
  };

  const handleEditLease = (lease: Lease) => {
    setEditingLease(lease);
    setIsEditModalOpen(true);
  };

  const handleViewLease = (lease: Lease) => {
    setViewingLease(lease);
    setIsViewModalOpen(true);
  };

  const handleRenewLease = (lease: Lease) => {
    setRenewingLease(lease);
    setIsRenewalModalOpen(true);
  };

  const handleTerminateLease = (lease: Lease) => {
    setTerminatingLease(lease);
    setIsTerminationModalOpen(true);
  };

  // Modal handlers
  const handleRenewalSubmit = async (data: any) => {
    try {
      if (!renewingLease) return;
      
      // Create a new lease based on renewal data
      const newLeaseData: CreateLeaseRequest = {
        propertyId: renewingLease.property_id || renewingLease.propertyId || '',
        tenantId: renewingLease.tenant_id || renewingLease.tenantId || '',
        startDate: data.newStartDate,
        endDate: data.newEndDate,
        monthlyRent: data.newMonthlyRent,
        securityDeposit: data.newSecurityDeposit,
        leaseType: data.renewalType,
        lateFeePenalty: renewingLease.late_fee_penalty || renewingLease.lateFeePenalty || 0,
        gracePeriodDays: 5, // Default grace period
        renewalOption: true,
        petPolicy: {
          allowed: false,
          deposit: 0,
          monthlyFee: 0,
          restrictions: ''
        },
        utilitiesIncluded: [],
        tenantResponsibilities: ['Regular cleaning', 'Minor maintenance'],
        landlordResponsibilities: ['Major repairs', 'Property maintenance'],
        specialTerms: data.notes,
        notes: `Renewed lease from ${renewingLease.id} on ${new Date().toLocaleDateString()}`
      };

      // Create the new lease
      await leaseService.createLease(newLeaseData);
      
      // Update the old lease status to 'renewed'
      if (renewingLease.id) {
        try {
          await leaseService.updateLease({ 
            id: renewingLease.id,
            status: 'expired',
            notes: `Renewed on ${new Date().toLocaleDateString()}. ${data.notes || ''}`
          });
        } catch (updateError) {
          console.warn('Could not update old lease status:', updateError);
          // Don't throw - the new lease was created successfully
        }
      }
      
      toast.success('Lease renewal created successfully!');
      // Refresh leases to show the new one
      fetchLeases();
      // Close the modal
      setIsRenewalModalOpen(false);
      setRenewingLease(undefined);
    } catch (error) {
      console.error('Error creating lease renewal:', error);
      toast.error('Failed to create lease renewal');
      throw error;
    }
  };

  const handleTerminationSubmit = async (data: any) => {
    try {
      if (!terminatingLease) return;
      
      // Update the lease status to terminated
      const terminationData: UpdateLeaseRequest = {
        id: terminatingLease.id,
        status: 'terminated',
        endDate: data.terminationDate, // Update end date to termination date
        notes: `Terminated on ${new Date(data.terminationDate).toLocaleDateString()}. Reason: ${data.terminationReason}. Security deposit return: $${data.securityDepositReturn}. Final rent: $${data.finalRentAmount}. ${data.notes || ''}`
      };

      await leaseService.updateLease(terminationData);
      
      toast.success('Lease terminated successfully!');
      // Refresh leases to show the updated status
      fetchLeases();
      // Close the modal
      setIsTerminationModalOpen(false);
      setTerminatingLease(undefined);
    } catch (error) {
      console.error('Error terminating lease:', error);
      toast.error('Failed to terminate lease');
      throw error;
    }
  };

  // Handle lease edit submission
  const handleEditSubmit = async (data: UpdateLeaseRequest) => {
    try {
      console.log('📋 Leases page - Updating lease with data:', data);
      const result = await leaseService.updateLease(data);
      console.log('✅ Leases page - Update result:', result);
      toast.success('Lease updated successfully!');
      // Refresh leases to show the updated data
      await fetchLeases();
      console.log('🔄 Leases page - Leases refreshed');
      // Close the modal
      setIsEditModalOpen(false);
      setEditingLease(undefined);
    } catch (error) {
      console.error('❌ Leases page - Error updating lease:', error);
      toast.error('Failed to update lease');
      throw error;
    }
  };

  const openCreateForm = () => {
    setIsCreateModalOpen(true);
  };

  const handleCreateSubmit = async (data: CreateLeaseRequest) => {
    try {
      console.log('📋 Leases page - Creating lease with data:', data);
      const result = await leaseService.createLease(data);
      console.log('✅ Leases page - Create result:', result);
      
      // Automatically create a security deposit record if security deposit amount > 0
      if (data.securityDeposit && data.securityDeposit > 0) {
        try {
          const depositData: CreateSecurityDepositRequest = {
            leaseId: result.id,
            tenantId: data.tenantId,
            propertyId: data.propertyId,
            amount: data.securityDeposit,
            dateReceived: data.startDate, // Default to lease start date
            bankAccount: 'General Trust Account', // Default account
            paymentMethod: 'check', // Default method
            referenceNumber: `DEP-${result.id}-${Date.now()}`,
            notes: `Security deposit for lease ${result.id}`
          };
          
          console.log('💰 Creating security deposit:', depositData);
          await securityDepositService.createSecurityDeposit(depositData);
          console.log('✅ Security deposit created successfully');
          toast.success('Lease created successfully with security deposit tracked!');
        } catch (depositError) {
          console.error('⚠️ Failed to create security deposit record:', depositError);
          toast.success('Lease created successfully, but failed to create security deposit record');
        }
      } else {
        toast.success('Lease created successfully!');
      }
      
      // Refresh leases to show the new lease
      await fetchLeases();
      console.log('🔄 Leases page - Leases refreshed');
    } catch (error) {
      console.error('❌ Leases page - Error creating lease:', error);
      toast.error('Failed to create lease');
      throw error;
    }
  };

  // Filter leases based on search and filters
  const filteredLeases = leases.filter(lease => {
    const tenantName = lease.tenant_name || 
      (lease.tenant ? `${lease.tenant.firstName} ${lease.tenant.lastName}` : '');
    const propertyName = lease.property_name || 
      (lease.property ? lease.property.name : '');
    
    const matchesSearch = tenantName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         propertyName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         lease.id.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || (lease.status || 'active') === statusFilter;
    const matchesType = typeFilter === 'all' || (lease.leaseType || lease.lease_type || 'fixed') === typeFilter;
    const matchesProperty = propertyFilter === 'all' || 
                           (lease.propertyId || lease.property_id) === propertyFilter;

    return matchesSearch && matchesStatus && matchesType && matchesProperty;
  });

  const getStatusCounts = () => {
    return {
      all: leases.length,
      active: leases.filter(l => l.status === 'active').length,
      expired: leases.filter(l => l.status === 'expired').length,
      terminated: leases.filter(l => l.status === 'terminated').length,
      pending: leases.filter(l => l.status === 'pending').length,
      draft: leases.filter(l => l.status === 'draft').length,
    };
  };

  const getExpiringLeases = () => {
    const today = new Date();
    const thirtyDaysFromNow = new Date(today.getTime() + (30 * 24 * 60 * 60 * 1000));
    
    return leases.filter(lease => {
      const endDateStr = lease.endDate || lease.end_date;
      if (!endDateStr) return false;
      const endDate = new Date(endDateStr);
      return lease.status === 'active' && endDate <= thirtyDaysFromNow && endDate > today;
    });
  };

  const statusCounts = getStatusCounts();
  const expiringLeases = getExpiringLeases();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
            Leases
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Manage your rental leases and agreements
          </p>
        </div>
        <div className="mt-4 flex md:ml-4 md:mt-0">
          <button
            type="button"
            onClick={openCreateForm}
            className="inline-flex items-center rounded-md bg-green-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-green-600"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Create Lease
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <DocumentTextIcon className="h-5 w-5 text-blue-600" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Leases</dt>
                  <dd className="text-lg font-medium text-gray-900">{statusCounts.all}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                  <span className="text-green-600 font-semibold text-sm">AC</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active</dt>
                  <dd className="text-lg font-medium text-gray-900">{statusCounts.active}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                  <span className="text-orange-600 font-semibold text-sm">EX</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Expiring Soon</dt>
                  <dd className="text-lg font-medium text-gray-900">{expiringLeases.length}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                  <span className="text-red-600 font-semibold text-sm">EP</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Expired</dt>
                  <dd className="text-lg font-medium text-gray-900">{statusCounts.expired}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <span className="text-yellow-600 font-semibold text-sm">PD</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Pending</dt>
                  <dd className="text-lg font-medium text-gray-900">{statusCounts.pending}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                  <span className="text-gray-600 font-semibold text-sm">DR</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Drafts</dt>
                  <dd className="text-lg font-medium text-gray-900">{statusCounts.draft}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Expiring Leases Alert */}
      {expiringLeases.length > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-orange-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-orange-800">
                {expiringLeases.length} lease{expiringLeases.length > 1 ? 's' : ''} expiring soon
              </h3>
              <p className="mt-1 text-sm text-orange-700">
                Review and renew leases that are expiring within the next 30 days.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search leases..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-green-500 focus:border-green-500 sm:text-sm"
            />
          </div>

          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
            >
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="expired">Expired</option>
              <option value="terminated">Terminated</option>
              <option value="pending">Pending</option>
              <option value="draft">Draft</option>
            </select>
          </div>

          <div>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
            >
              <option value="all">All Types</option>
              <option value="fixed">Fixed Term</option>
              <option value="month-to-month">Month-to-Month</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>

          <div>
            <select
              value={propertyFilter}
              onChange={(e) => setPropertyFilter(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
            >
              <option value="all">All Properties</option>
              {properties.map(property => (
                <option key={property.id} value={property.id}>
                  {property.name} - {typeof property.address === 'string' ? property.address : 
                    `${property.address.street}, ${property.address.city}`}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Leases Grid */}
      {filteredLeases.length === 0 ? (
        <div className="text-center py-12">
          <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No leases found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {leases.length === 0 
              ? "Get started by creating your first lease."
              : "Try adjusting your search or filter criteria."
            }
          </p>
          {leases.length === 0 && (
            <div className="mt-6">
              <button
                type="button"
                onClick={openCreateForm}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Create Lease
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filteredLeases.map((lease) => (
            <LeaseCard
              key={lease.id}
              lease={lease}
              onEdit={handleEditLease}
              onDelete={handleDeleteLease}
              onView={handleViewLease}
              onRenew={handleRenewLease}
              onTerminate={handleTerminateLease}
            />
          ))}
        </div>
      )}

      {/* Modals */}
      {viewingLease && (
        <LeaseViewModal
          isOpen={isViewModalOpen}
          onClose={() => {
            setIsViewModalOpen(false);
            setViewingLease(undefined);
          }}
          lease={viewingLease}
          onEdit={handleEditLease}
          onRenew={handleRenewLease}
          onTerminate={handleTerminateLease}
          onViewProperty={(propertyId) => {
            console.log('Navigate to property:', propertyId);
            // TODO: Navigate to property details
            toast('Property navigation will be implemented soon!');
          }}
          onViewTenant={(tenantId) => {
            console.log('Navigate to tenant:', tenantId);
            // TODO: Navigate to tenant details
            toast('Tenant navigation will be implemented soon!');
          }}
        />
      )}

      {editingLease && (
        <LeaseEditModal
          isOpen={isEditModalOpen}
          onClose={() => {
            setIsEditModalOpen(false);
            setEditingLease(undefined);
          }}
          lease={editingLease}
          onSubmit={handleEditSubmit}
        />
      )}

      {renewingLease && (
        <LeaseRenewalModal
          isOpen={isRenewalModalOpen}
          onClose={() => {
            setIsRenewalModalOpen(false);
            setRenewingLease(undefined);
          }}
          lease={renewingLease}
          onSubmit={handleRenewalSubmit}
        />
      )}

      {terminatingLease && (
        <LeaseTerminationModal
          isOpen={isTerminationModalOpen}
          onClose={() => {
            setIsTerminationModalOpen(false);
            setTerminatingLease(undefined);
          }}
          lease={terminatingLease}
          onSubmit={handleTerminationSubmit}
        />
      )}

      <LeaseCreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateSubmit}
      />
    </div>
  );
};

export default Leases;
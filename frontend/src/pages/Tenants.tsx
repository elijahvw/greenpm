import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Tenant, CreateTenantRequest, UpdateTenantRequest } from '../types/tenant';
import { Lease } from '../types/lease';
import { tenantService } from '../services/tenantService';
import { leaseService } from '../services/leaseService';
import TenantCard from '../components/Tenants/TenantCard';
import TenantForm from '../components/Tenants/TenantForm';
import TenantEditModal from '../components/Tenants/TenantEditModal';
import { PlusIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const Tenants: React.FC = () => {
  const navigate = useNavigate();
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [leases, setLeases] = useState<Lease[]>([]);
  const [loading, setLoading] = useState(true);
  const [formLoading, setFormLoading] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingTenant, setEditingTenant] = useState<Tenant | undefined>();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    fetchTenants();
  }, []);

  const getTenantLeases = (tenantId: string): Lease[] => {
    return leases.filter(lease => 
      lease.tenant_id === tenantId || lease.tenantId === tenantId
    );
  };

  const fetchTenants = async () => {
    try {
      setLoading(true);
      const [tenantsData, leasesData] = await Promise.all([
        tenantService.getTenants(),
        leaseService.getLeases()
      ]);
      setTenants(tenantsData);
      setLeases(leasesData);
    } catch (error) {
      console.error('Error fetching tenants:', error);
      toast.error('Failed to load tenants');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTenant = async (data: CreateTenantRequest) => {
    try {
      setFormLoading(true);
      const newTenant = await tenantService.createTenant(data);
      setTenants([...tenants, newTenant]);
      setIsFormOpen(false);
      toast.success('Tenant created successfully');
    } catch (error) {
      console.error('Error creating tenant:', error);
      toast.error('Failed to create tenant');
    } finally {
      setFormLoading(false);
    }
  };

  const handleUpdateTenant = async (data: UpdateTenantRequest) => {
    try {
      setFormLoading(true);
      const updatedTenant = await tenantService.updateTenant(data);
      setTenants(tenants.map(t => t.id === updatedTenant.id ? updatedTenant : t));
      setIsFormOpen(false);
      setEditingTenant(undefined);
      toast.success('Tenant updated successfully');
    } catch (error) {
      console.error('Error updating tenant:', error);
      toast.error('Failed to update tenant');
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteTenant = async (tenantId: string) => {
    if (!window.confirm('Are you sure you want to delete this tenant? This action cannot be undone.')) {
      return;
    }

    try {
      await tenantService.deleteTenant(tenantId);
      setTenants(tenants.filter(t => t.id !== tenantId));
      toast.success('Tenant deleted successfully');
    } catch (error: any) {
      console.error('Error deleting tenant:', error);
      
      // Check if it's a 400 error (tenant has active leases)
      if (error?.response?.status === 400) {
        const errorMessage = error?.response?.data?.detail || 'Cannot delete tenant with active leases';
        toast.error(errorMessage);
      } else {
        toast.error('Failed to delete tenant');
      }
    }
  };

  const handleEditTenant = (tenant: Tenant) => {
    setEditingTenant(tenant);
    setIsEditModalOpen(true);
  };

  const handleViewTenant = (tenant: Tenant) => {
    navigate(`/dashboard/tenants/${tenant.id}`);
  };

  const handleEditSubmit = async (data: Partial<Tenant>) => {
    try {
      if (!editingTenant?.id) return;
      
      await tenantService.updateTenant(data as UpdateTenantRequest);
      toast.success('Tenant updated successfully!');
      fetchTenants();
      setIsEditModalOpen(false);
      setEditingTenant(undefined);
    } catch (error) {
      console.error('Error updating tenant:', error);
      toast.error('Failed to update tenant');
      throw error;
    }
  };

  const openCreateForm = () => {
    setEditingTenant(undefined);
    setIsFormOpen(true);
  };

  const closeForm = () => {
    setIsFormOpen(false);
    setEditingTenant(undefined);
  };

  // Filter tenants based on search and filters
  const filteredTenants = tenants.filter(tenant => {
    const fullName = `${tenant.firstName} ${tenant.lastName}`.toLowerCase();
    const matchesSearch = fullName.includes(searchTerm.toLowerCase()) ||
                         tenant.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         tenant.phone.includes(searchTerm);
    
    const matchesStatus = statusFilter === 'all' || tenant.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const getStatusCounts = () => {
    return {
      all: tenants.length,
      active: tenants.filter(t => t.status === 'active').length,
      inactive: tenants.filter(t => t.status === 'inactive').length,
      pending: tenants.filter(t => t.status === 'pending').length,
      evicted: tenants.filter(t => t.status === 'evicted').length,
    };
  };

  const statusCounts = getStatusCounts();

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
            Tenants
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Manage your tenants and their information
          </p>
        </div>
        <div className="mt-4 flex md:ml-4 md:mt-0">
          <button
            type="button"
            onClick={openCreateForm}
            className="inline-flex items-center rounded-md bg-green-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-green-600"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Tenant
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-5">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span className="text-blue-600 font-semibold text-sm">ALL</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Tenants</dt>
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
                  <span className="text-gray-600 font-semibold text-sm">IN</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Inactive</dt>
                  <dd className="text-lg font-medium text-gray-900">{statusCounts.inactive}</dd>
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
                  <span className="text-red-600 font-semibold text-sm">EV</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Evicted</dt>
                  <dd className="text-lg font-medium text-gray-900">{statusCounts.evicted}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search tenants..."
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
              <option value="inactive">Inactive</option>
              <option value="pending">Pending</option>
              <option value="evicted">Evicted</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tenants Grid */}
      {filteredTenants.length === 0 ? (
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-gray-400">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No tenants found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {tenants.length === 0 
              ? "Get started by adding your first tenant."
              : "Try adjusting your search or filter criteria."
            }
          </p>
          {tenants.length === 0 && (
            <div className="mt-6">
              <button
                type="button"
                onClick={openCreateForm}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Tenant
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filteredTenants.map((tenant) => (
            <TenantCard
              key={tenant.id}
              tenant={tenant}
              leases={getTenantLeases(tenant.id)}
              onEdit={handleEditTenant}
              onDelete={handleDeleteTenant}
              onView={handleViewTenant}
            />
          ))}
        </div>
      )}

      {/* Tenant Form Modal */}
      <TenantForm
        tenant={editingTenant}
        isOpen={isFormOpen}
        onClose={closeForm}
        onSubmit={async (data) => {
          if (editingTenant) {
            await handleUpdateTenant(data as UpdateTenantRequest);
          } else {
            await handleCreateTenant(data as CreateTenantRequest);
          }
        }}
        loading={formLoading}
      />

      {/* Tenant Edit Modal */}
      {editingTenant && (
        <TenantEditModal
          isOpen={isEditModalOpen}
          onClose={() => {
            setIsEditModalOpen(false);
            setEditingTenant(undefined);
          }}
          tenant={editingTenant}
          onSubmit={handleEditSubmit}
        />
      )}
    </div>
  );
};

export default Tenants;
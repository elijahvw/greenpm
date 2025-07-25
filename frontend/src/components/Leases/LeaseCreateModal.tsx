import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import Modal from '../Common/Modal';
import { CreateLeaseRequest } from '../../types/lease';
import { Property } from '../../types/property';
import { Tenant } from '../../types/tenant';
import { propertyService } from '../../services/propertyService';
import { tenantService } from '../../services/tenantService';
import { CalendarIcon, CurrencyDollarIcon, HomeIcon, UserIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface LeaseCreateFormData {
  propertyId: string;
  tenantId: string;
  startDate: string;
  endDate: string;
  monthlyRent: number;
  securityDeposit: number;
  lateFeePenalty: number;
  gracePeriodDays: number;
  leaseType: 'fixed' | 'month-to-month' | 'yearly';
  renewalOption: boolean;
  petPolicy: boolean;
  notes: string;
  specialTerms: string;
}

interface LeaseCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateLeaseRequest) => Promise<void>;
  preSelectedPropertyId?: string;
}

const LeaseCreateModal: React.FC<LeaseCreateModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  preSelectedPropertyId
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [properties, setProperties] = useState<Property[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [selectedTenant, setSelectedTenant] = useState<Tenant | null>(null);
  
  // Helper function to safely access address properties
  const getAddressString = (address?: string | { street: string; city: string; state: string; zipCode: string; country: string; } | null, property?: any) => {
    if (typeof address === 'string') {
      return address;
    } else if (address && typeof address === 'object') {
      return `${address.street}, ${address.city}`;
    } else if (property) {
      // Use individual fields from API response
      const street = property.street || property.address_line1 || '';
      const city = property.city || '';
      return street && city ? `${street}, ${city}` : street || city || '';
    }
    return '';
  };
  
  const { 
    register, 
    handleSubmit, 
    watch,
    setValue,
    reset,
    formState: { errors } 
  } = useForm<LeaseCreateFormData>();

  const watchedPropertyId = watch('propertyId');
  const watchedTenantId = watch('tenantId');

  // Load properties and tenants when modal opens
  useEffect(() => {
    if (isOpen) {
      loadPropertiesAndTenants();
      // Set default dates
      const today = new Date();
      const nextYear = new Date(today);
      nextYear.setFullYear(nextYear.getFullYear() + 1);
      
      setValue('startDate', today.toISOString().split('T')[0]);
      setValue('endDate', nextYear.toISOString().split('T')[0]);
      setValue('leaseType', 'fixed');
      setValue('gracePeriodDays', 5);
      setValue('renewalOption', true);
      setValue('petPolicy', false);
    }
  }, [isOpen, setValue]);

  const loadPropertiesAndTenants = async () => {
    try {
      const [propertiesData, tenantsData] = await Promise.all([
        propertyService.getPropertiesForLeases(), // Use the lease-specific endpoint
        tenantService.getTenants()
      ]);
      
      // Show ALL properties for lease creation (occupied properties can have draft/pending leases)
      // Only filter tenants to active/prospective
      const availableTenants = tenantsData.filter(t => ['active', 'prospective'].includes(t.status || 'prospective'));
      
      setProperties(propertiesData); // Show all properties
      setTenants(availableTenants);
      
      // Pre-select property if provided
      if (preSelectedPropertyId) {
        const preSelectedProperty = propertiesData.find((p: any) => p.id === preSelectedPropertyId);
        if (preSelectedProperty) {
          setValue('propertyId', preSelectedPropertyId);
          setSelectedProperty(preSelectedProperty);
          
          // Auto-fill rent amount from property if available
          if (preSelectedProperty.rentAmount || preSelectedProperty.rent_amount) {
            const rentAmount = preSelectedProperty.rentAmount || preSelectedProperty.rent_amount || 0;
            setValue('monthlyRent', rentAmount);
            setValue('securityDeposit', rentAmount); // Default to 1 month rent
          }
        }
      }
    } catch (error) {
      console.error('Error loading properties and tenants:', error);
      toast.error('Failed to load properties and tenants');
    }
  };

  // Update selected property when propertyId changes
  useEffect(() => {
    if (watchedPropertyId) {
      const property = properties.find(p => p.id === watchedPropertyId);
      setSelectedProperty(property || null);
      
      // Auto-fill rent amount from property if available
      if (property?.rentAmount) {
        setValue('monthlyRent', property.rentAmount);
        setValue('securityDeposit', property.rentAmount); // Default to 1 month rent
      }
    }
  }, [watchedPropertyId, properties, setValue]);

  // Update selected tenant when tenantId changes
  useEffect(() => {
    if (watchedTenantId) {
      const tenant = tenants.find(t => t.id === watchedTenantId);
      setSelectedTenant(tenant || null);
    }
  }, [watchedTenantId, tenants]);

  const onFormSubmit = async (data: LeaseCreateFormData) => {
    try {
      setIsSubmitting(true);
      
      // Determine initial status based on whether property has active lease
      const hasActiveLease = selectedProperty?.current_lease?.status === 'active';
      const initialStatus = hasActiveLease ? 'pending' : 'active';
      
      const leaseData: CreateLeaseRequest = {
        propertyId: data.propertyId,
        tenantId: data.tenantId,
        startDate: data.startDate,
        endDate: data.endDate,
        monthlyRent: Math.round((data.monthlyRent || 0) * 100) / 100,
        securityDeposit: Math.round((data.securityDeposit || 0) * 100) / 100,
        lateFeePenalty: Math.round((data.lateFeePenalty || 0) * 100) / 100,
        gracePeriodDays: data.gracePeriodDays,
        leaseType: data.leaseType,
        renewalOption: data.renewalOption,
        status: initialStatus,
        notes: data.notes,
        specialTerms: data.specialTerms,
        // Add required fields with defaults
        petPolicy: {
          allowed: false,
          deposit: 0,
          monthlyFee: 0,
          restrictions: ''
        },
        utilitiesIncluded: [],
        tenantResponsibilities: ['Utilities', 'Maintenance under $100', 'Keep property clean'],
        landlordResponsibilities: ['Major repairs', 'Property taxes', 'Insurance']
      };

      console.log('📝 LeaseCreate - Submitting lease data:', leaseData);
      await onSubmit(leaseData);
      
      toast.success('Lease created successfully!');
      reset();
      onClose();
    } catch (error) {
      console.error('Error creating lease:', error);
      toast.error('Failed to create lease');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    reset();
    setSelectedProperty(null);
    setSelectedTenant(null);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Create New Lease"
      maxWidth="4xl"
    >
      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
        {/* Property and Tenant Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <HomeIcon className="inline h-4 w-4 mr-1" />
              Property *
            </label>
            <select
              {...register('propertyId', { required: 'Property is required' })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="">Select a property...</option>
              {properties.map(property => (
                <option key={property.id} value={property.id}>
                  {`${property.name || (property as any).title} - ${property.address} - $${property.rentAmount || (property as any).rent_amount || 'N/A'}/month`}
                </option>
              ))}
            </select>
            {errors.propertyId && (
              <p className="mt-1 text-sm text-red-600">{errors.propertyId.message}</p>
            )}
            {selectedProperty && (
              <>
                <div className="mt-2 p-2 bg-blue-50 rounded text-xs">
                  <p>
                    <><strong>Address:</strong> {typeof selectedProperty.address === 'string' ? selectedProperty.address : `${selectedProperty.street || selectedProperty.address_line1 || ''} ${selectedProperty.city || ''}, ${selectedProperty.state || ''} ${selectedProperty.zipCode || selectedProperty.zip_code || ''}`}</>
                  </p>
                  <p>
                    <><strong>Type:</strong> {selectedProperty.type || 'N/A'} • <strong>Bedrooms:</strong> {selectedProperty.bedrooms || 'N/A'} • <strong>Bathrooms:</strong> {selectedProperty.bathrooms || 'N/A'} • <strong>Rent:</strong> ${(selectedProperty.rentAmount || selectedProperty.rent_amount || 0).toLocaleString()}/month</>
                  </p>
                </div>
                {/* Warning for properties with active leases */}
                {selectedProperty.current_lease && selectedProperty.current_lease.status === 'active' && (
                  <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded text-xs">
                    <div className="flex items-start">
                      <div className="flex-shrink-0">
                        <span className="text-yellow-600">⚠️</span>
                      </div>
                      <div className="ml-2">
                        <p className="text-yellow-800 font-medium">Active Lease Exists</p>
                        <p className="text-yellow-700 mt-1">
                          This property has an active lease with {selectedProperty.current_lease.tenant_name} until{' '}
                          {(() => {
                            const dateString = selectedProperty.current_lease.end_date!;
                            const date = dateString.includes('T') 
                              ? new Date(dateString) 
                              : new Date(dateString + 'T00:00:00');
                            return date.toLocaleDateString();
                          })()} 
                          . This new lease will be created in pending status.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <UserIcon className="inline h-4 w-4 mr-1" />
              Tenant *
            </label>
            <select
              {...register('tenantId', { required: 'Tenant is required' })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="">Select a tenant...</option>
              {tenants.map(tenant => (
                <option key={tenant.id} value={tenant.id}>
                  {tenant.firstName} {tenant.lastName} - {tenant.email}
                </option>
              ))}
            </select>
            {errors.tenantId && (
              <p className="mt-1 text-sm text-red-600">{errors.tenantId.message}</p>
            )}
            {selectedTenant && (
              <div className="mt-2 p-2 bg-green-50 rounded text-xs">
                <p><strong>Email:</strong> {selectedTenant.email}</p>
                <p><strong>Phone:</strong> {selectedTenant.phone}</p>
                <p><strong>Status:</strong> <span className="capitalize">{selectedTenant.status}</span></p>
              </div>
            )}
          </div>
        </div>

        {/* Lease Dates and Terms */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <CalendarIcon className="inline h-4 w-4 mr-1" />
              Start Date *
            </label>
            <input
              type="date"
              {...register('startDate', { required: 'Start date is required' })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
            {errors.startDate && (
              <p className="mt-1 text-xs text-red-600">{errors.startDate.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <CalendarIcon className="inline h-4 w-4 mr-1" />
              End Date *
            </label>
            <input
              type="date"
              {...register('endDate', { required: 'End date is required' })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
            {errors.endDate && (
              <p className="mt-1 text-xs text-red-600">{errors.endDate.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Lease Type *
            </label>
            <select
              {...register('leaseType', { required: 'Lease type is required' })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="fixed">Fixed Term</option>
              <option value="month-to-month">Month-to-Month</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Grace Period (Days)
            </label>
            <input
              type="number"
              min="0"
              max="30"
              {...register('gracePeriodDays', {
                min: { value: 0, message: 'Grace period cannot be negative' },
                max: { value: 30, message: 'Grace period cannot exceed 30 days' },
                valueAsNumber: true
              })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
            {errors.gracePeriodDays && (
              <p className="mt-1 text-xs text-red-600">{errors.gracePeriodDays.message}</p>
            )}
          </div>
        </div>

        {/* Financial Terms */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <CurrencyDollarIcon className="inline h-4 w-4 mr-1" />
              Monthly Rent *
            </label>
            <div className="relative">
              <span className="absolute left-3 top-2 text-gray-500">$</span>
              <input
                type="number"
                step="1"
                min="0"
                {...register('monthlyRent', {
                  required: 'Monthly rent is required',
                  min: { value: 0, message: 'Rent must be positive' },
                  valueAsNumber: true,
                  setValueAs: (value) => {
                    const num = parseFloat(value);
                    return isNaN(num) ? 0 : Math.round(num * 100) / 100;
                  }
                })}
                className="pl-8 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
            {errors.monthlyRent && (
              <p className="mt-1 text-xs text-red-600">{errors.monthlyRent.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <CurrencyDollarIcon className="inline h-4 w-4 mr-1" />
              Security Deposit *
            </label>
            <div className="relative">
              <span className="absolute left-3 top-2 text-gray-500">$</span>
              <input
                type="number"
                step="1"
                min="0"
                {...register('securityDeposit', {
                  required: 'Security deposit is required',
                  min: { value: 0, message: 'Deposit must be positive' },
                  valueAsNumber: true,
                  setValueAs: (value) => {
                    const num = parseFloat(value);
                    return isNaN(num) ? 0 : Math.round(num * 100) / 100;
                  }
                })}
                className="pl-8 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
            {errors.securityDeposit && (
              <p className="mt-1 text-xs text-red-600">{errors.securityDeposit.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <CurrencyDollarIcon className="inline h-4 w-4 mr-1" />
              Late Fee Penalty
            </label>
            <div className="relative">
              <span className="absolute left-3 top-2 text-gray-500">$</span>
              <input
                type="number"
                step="1"
                min="0"
                {...register('lateFeePenalty', {
                  min: { value: 0, message: 'Late fee must be positive' },
                  valueAsNumber: true,
                  setValueAs: (value) => {
                    const num = parseFloat(value);
                    return isNaN(num) ? 0 : Math.round(num * 100) / 100;
                  }
                })}
                className="pl-8 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
            {errors.lateFeePenalty && (
              <p className="mt-1 text-xs text-red-600">{errors.lateFeePenalty.message}</p>
            )}
          </div>
        </div>

        {/* Options */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              {...register('renewalOption')}
              className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-700">
              Renewal Option Available
            </label>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              {...register('petPolicy')}
              className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-700">
              Pets Allowed
            </label>
          </div>
        </div>

        {/* Notes and Special Terms */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              rows={3}
              {...register('notes')}
              placeholder="Internal notes about this lease..."
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Special Terms
            </label>
            <textarea
              rows={3}
              {...register('specialTerms')}
              placeholder="Special clauses or terms for this lease..."
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-6 border-t">
          <button
            type="button"
            onClick={handleClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Creating...' : 'Create Lease'}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default LeaseCreateModal;
import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { CreateLeaseRequest } from '../../types/lease';
import { Property } from '../../types/property';
import { Tenant } from '../../types/tenant';
import { propertyService } from '../../services/propertyService';
import { tenantService } from '../../services/tenantService';
import { XMarkIcon, CalendarIcon, CurrencyDollarIcon, HomeIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

interface LeaseFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateLeaseRequest) => Promise<void>;
  preSelectedPropertyId?: string;
  loading?: boolean;
}

const LeaseForm: React.FC<LeaseFormProps> = ({
  isOpen,
  onClose,
  onSubmit,
  preSelectedPropertyId,
  loading = false,
}) => {
  const [properties, setProperties] = useState<Property[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
    setValue,
    watch,
  } = useForm<CreateLeaseRequest>();

  const watchPropertyId = watch('propertyId');

  useEffect(() => {
    if (isOpen) {
      loadPropertiesAndTenants();
      resetForm();
    }
  }, [isOpen]);

  useEffect(() => {
    if (watchPropertyId) {
      const property = properties.find(p => p.id === watchPropertyId);
      setSelectedProperty(property || null);
      
      // Auto-fill rent from property
      if (property && (property.rentAmount || property.rent_amount)) {
        const rentAmount = property.rentAmount || property.rent_amount || 0;
        setValue('monthlyRent', rentAmount);
        setValue('securityDeposit', rentAmount); // Default to 1 month rent
      }
    }
  }, [watchPropertyId, properties, setValue]);

  const resetForm = () => {
    reset();
    setSelectedProperty(null);
    
    // Set default values
    setValue('leaseType', 'fixed');
    setValue('gracePeriodDays', 5);
    setValue('renewalOption', true);
    setValue('petPolicy', {
      allowed: false,
      deposit: 0,
      monthlyFee: 0,
      restrictions: ''
    });
    setValue('lateFeePenalty', 0);
    setValue('utilitiesIncluded', []);
    setValue('tenantResponsibilities', []);
    setValue('landlordResponsibilities', []);
  };

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

  const handleFormSubmit = async (data: CreateLeaseRequest) => {
    try {
      setIsSubmitting(true);
      await onSubmit(data);
      onClose();
      resetForm();
    } catch (error) {
      console.error('Error creating lease:', error);
      // Error handling is done in parent component
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-10 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" onClick={onClose}></div>

        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full sm:p-6">
          <form onSubmit={handleSubmit(handleFormSubmit)}>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-medium text-gray-900">
                Create New Lease
              </h3>
              <button
                type="button"
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Property & Tenant Selection */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3 flex items-center">
                  <HomeIcon className="h-5 w-5 mr-2" />
                  Property & Tenant
                </h4>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Property *
                    </label>
                    <select
                      {...register('propertyId', { required: 'Property is required' })}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    >
                      <option value="">Select a property</option>
                      {properties.map((property) => (
                        <option key={property.id} value={property.id}>
                          {`${property.name || property.title} - ${property.address}`}
                        </option>
                      ))}
                    </select>
                    {errors.propertyId && (
                      <p className="mt-1 text-sm text-red-600">{errors.propertyId.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Tenant *
                    </label>
                    <select
                      {...register('tenantId', { required: 'Tenant is required' })}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    >
                      <option value="">Select a tenant</option>
                      {tenants.map((tenant) => (
                        <option key={tenant.id} value={tenant.id}>
                          {`${tenant.firstName || ''} ${tenant.lastName || ''}`.trim()} - {tenant.email}
                        </option>
                      ))}
                    </select>
                    {errors.tenantId && (
                      <p className="mt-1 text-sm text-red-600">{errors.tenantId.message}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Lease Details */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3 flex items-center">
                  <CalendarIcon className="h-5 w-5 mr-2" />
                  Lease Details
                </h4>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Start Date *
                    </label>
                    <input
                      type="date"
                      {...register('startDate', { required: 'Start date is required' })}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    />
                    {errors.startDate && (
                      <p className="mt-1 text-sm text-red-600">{errors.startDate.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      End Date *
                    </label>
                    <input
                      type="date"
                      {...register('endDate', { required: 'End date is required' })}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    />
                    {errors.endDate && (
                      <p className="mt-1 text-sm text-red-600">{errors.endDate.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Lease Type *
                    </label>
                    <select
                      {...register('leaseType', { required: 'Lease type is required' })}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    >
                      <option value="fixed">Fixed Term</option>
                      <option value="month-to-month">Month-to-Month</option>
                      <option value="periodic">Periodic</option>
                    </select>
                    {errors.leaseType && (
                      <p className="mt-1 text-sm text-red-600">{errors.leaseType.message}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Financial Terms */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3 flex items-center">
                  <CurrencyDollarIcon className="h-5 w-5 mr-2" />
                  Financial Terms
                </h4>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Monthly Rent *
                    </label>
                    <div className="mt-1 relative rounded-md shadow-sm">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <span className="text-gray-500 sm:text-sm">$</span>
                      </div>
                      <input
                        type="number"
                        step="0.01"
                        {...register('monthlyRent', { 
                          required: 'Monthly rent is required',
                          min: { value: 0, message: 'Rent must be positive' }
                        })}
                        className="mt-1 block w-full pl-7 border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="0.00"
                      />
                    </div>
                    {errors.monthlyRent && (
                      <p className="mt-1 text-sm text-red-600">{errors.monthlyRent.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Security Deposit *
                    </label>
                    <div className="mt-1 relative rounded-md shadow-sm">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <span className="text-gray-500 sm:text-sm">$</span>
                      </div>
                      <input
                        type="number"
                        step="0.01"
                        {...register('securityDeposit', { 
                          required: 'Security deposit is required',
                          min: { value: 0, message: 'Security deposit must be positive' }
                        })}
                        className="mt-1 block w-full pl-7 border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="0.00"
                      />
                    </div>
                    {errors.securityDeposit && (
                      <p className="mt-1 text-sm text-red-600">{errors.securityDeposit.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Late Fee Penalty
                    </label>
                    <div className="mt-1 relative rounded-md shadow-sm">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <span className="text-gray-500 sm:text-sm">$</span>
                      </div>
                      <input
                        type="number"
                        step="0.01"
                        {...register('lateFeePenalty', { 
                          required: 'Late fee penalty is required',
                          min: { value: 0, message: 'Late fee penalty must be non-negative' }
                        })}
                        className="mt-1 block w-full pl-7 border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="0.00"
                      />
                    </div>
                    {errors.lateFeePenalty && (
                      <p className="mt-1 text-sm text-red-600">{errors.lateFeePenalty.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Grace Period (Days)
                    </label>
                    <input
                      type="number"
                      {...register('gracePeriodDays', { 
                        min: { value: 0, message: 'Grace period must be non-negative' }
                      })}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      placeholder="5"
                    />
                    {errors.gracePeriodDays && (
                      <p className="mt-1 text-sm text-red-600">{errors.gracePeriodDays.message}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Additional Terms */}
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3">Additional Terms</h4>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        {...register('renewalOption')}
                        className="rounded border-gray-300 text-green-600 shadow-sm focus:border-green-300 focus:ring focus:ring-green-200 focus:ring-opacity-50"
                      />
                      <span className="ml-2 text-sm text-gray-700">Renewal Option Available</span>
                    </label>
                  </div>

                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        {...register('petPolicy')}
                        className="rounded border-gray-300 text-green-600 shadow-sm focus:border-green-300 focus:ring focus:ring-green-200 focus:ring-opacity-50"
                      />
                      <span className="ml-2 text-sm text-gray-700">Pets Allowed</span>
                    </label>
                  </div>
                </div>
              </div>

              {/* Selected Property Preview */}
              {selectedProperty && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h5 className="text-sm font-medium text-green-800 mb-2">Selected Property</h5>
                  <div className="text-sm text-green-700">
                    <p className="font-medium">{selectedProperty.name || selectedProperty.title}</p>
                    <p>{typeof selectedProperty.address === 'object' ? selectedProperty.address.street : selectedProperty.address_line1}, {typeof selectedProperty.address === 'object' ? selectedProperty.address.city : selectedProperty.city}</p>
                    <p>Type: {selectedProperty.type} • Rent: ${(selectedProperty.rentAmount || selectedProperty.rent_amount || 0).toLocaleString()}/month</p>
                  </div>
                </div>
              )}
            </div>

            {/* Form Actions */}
            <div className="mt-8 flex justify-end space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting || loading}
                className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting || loading ? 'Creating...' : 'Create Lease'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LeaseForm;
import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Tenant, CreateTenantRequest, UpdateTenantRequest } from '../../types/tenant';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface TenantFormProps {
  tenant?: Tenant;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateTenantRequest | UpdateTenantRequest) => Promise<void>;
  loading?: boolean;
}

const TenantForm: React.FC<TenantFormProps> = ({
  tenant,
  isOpen,
  onClose,
  onSubmit,
  loading = false,
}) => {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
    setValue,
  } = useForm<CreateTenantRequest>();

  useEffect(() => {
    if (tenant) {
      // Populate form with existing tenant data
      setValue('firstName', tenant.firstName);
      setValue('lastName', tenant.lastName);
      setValue('email', tenant.email);
      setValue('phone', tenant.phone);
      setValue('dateOfBirth', tenant.dateOfBirth || '');
      setValue('socialSecurityNumber', tenant.socialSecurityNumber || '');
      setValue('emergencyContact.name', tenant.emergencyContact?.name || '');
      setValue('emergencyContact.phone', tenant.emergencyContact?.phone || '');
      setValue('emergencyContact.relationship', tenant.emergencyContact?.relationship || '');
      setValue('employment.employer', tenant.employment?.employer || '');
      setValue('employment.position', tenant.employment?.position || '');
      setValue('employment.monthlyIncome', tenant.employment?.monthlyIncome || 0);
      setValue('employment.employmentStartDate', tenant.employment?.employmentStartDate || '');
      setValue('address.street', tenant.address?.street || '');
      setValue('address.city', tenant.address?.city || '');
      setValue('address.state', tenant.address?.state || '');
      setValue('address.zipCode', tenant.address?.zipCode || '');
      setValue('address.country', tenant.address?.country || 'USA');
      setValue('notes', tenant.notes || '');
    } else {
      // Reset form for new tenant
      reset();
    }
  }, [tenant, setValue, reset]);

  const handleFormSubmit = async (data: CreateTenantRequest) => {
    const formData = {
      ...data,
      ...(tenant && { id: tenant.id }),
    };

    await onSubmit(formData as CreateTenantRequest | UpdateTenantRequest);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <form onSubmit={handleSubmit(handleFormSubmit)}>
            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  {tenant ? 'Edit Tenant' : 'Add New Tenant'}
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
                {/* Personal Information */}
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">Personal Information</h4>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        First Name *
                      </label>
                      <input
                        type="text"
                        {...register('firstName', { required: 'First name is required' })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="John"
                      />
                      {errors.firstName && (
                        <p className="mt-1 text-sm text-red-600">{errors.firstName.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Last Name *
                      </label>
                      <input
                        type="text"
                        {...register('lastName', { required: 'Last name is required' })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="Doe"
                      />
                      {errors.lastName && (
                        <p className="mt-1 text-sm text-red-600">{errors.lastName.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Email *
                      </label>
                      <input
                        type="email"
                        {...register('email', { 
                          required: 'Email is required',
                          pattern: {
                            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                            message: 'Invalid email address'
                          }
                        })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="john.doe@example.com"
                      />
                      {errors.email && (
                        <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Phone *
                      </label>
                      <input
                        type="tel"
                        {...register('phone', { required: 'Phone number is required' })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="(555) 123-4567"
                      />
                      {errors.phone && (
                        <p className="mt-1 text-sm text-red-600">{errors.phone.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Date of Birth *
                      </label>
                      <input
                        type="date"
                        {...register('dateOfBirth', { required: 'Date of birth is required' })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      />
                      {errors.dateOfBirth && (
                        <p className="mt-1 text-sm text-red-600">{errors.dateOfBirth.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Social Security Number
                      </label>
                      <input
                        type="text"
                        {...register('socialSecurityNumber')}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="XXX-XX-XXXX"
                      />
                    </div>
                  </div>
                </div>

                {/* Address */}
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">Address</h4>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Street Address *
                      </label>
                      <input
                        type="text"
                        {...register('address.street', { required: 'Street address is required' })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="123 Main Street"
                      />
                      {errors.address?.street && (
                        <p className="mt-1 text-sm text-red-600">{errors.address.street.message}</p>
                      )}
                    </div>

                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          City *
                        </label>
                        <input
                          type="text"
                          {...register('address.city', { required: 'City is required' })}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                          placeholder="San Francisco"
                        />
                        {errors.address?.city && (
                          <p className="mt-1 text-sm text-red-600">{errors.address.city.message}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          State *
                        </label>
                        <input
                          type="text"
                          {...register('address.state', { required: 'State is required' })}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                          placeholder="CA"
                        />
                        {errors.address?.state && (
                          <p className="mt-1 text-sm text-red-600">{errors.address.state.message}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          ZIP Code *
                        </label>
                        <input
                          type="text"
                          {...register('address.zipCode', { required: 'ZIP code is required' })}
                          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                          placeholder="94102"
                        />
                        {errors.address?.zipCode && (
                          <p className="mt-1 text-sm text-red-600">{errors.address.zipCode.message}</p>
                        )}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Country *
                      </label>
                      <input
                        type="text"
                        {...register('address.country', { required: 'Country is required' })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="United States"
                        defaultValue="United States"
                      />
                      {errors.address?.country && (
                        <p className="mt-1 text-sm text-red-600">{errors.address.country.message}</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Employment Information */}
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">Employment Information</h4>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Employer *
                      </label>
                      <input
                        type="text"
                        {...register('employment.employer', { required: 'Employer is required' })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="ABC Company"
                      />
                      {errors.employment?.employer && (
                        <p className="mt-1 text-sm text-red-600">{errors.employment.employer.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Position *
                      </label>
                      <input
                        type="text"
                        {...register('employment.position', { required: 'Position is required' })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="Software Engineer"
                      />
                      {errors.employment?.position && (
                        <p className="mt-1 text-sm text-red-600">{errors.employment.position.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Monthly Income *
                      </label>
                      <div className="mt-1 relative rounded-md shadow-sm">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <span className="text-gray-500 sm:text-sm">$</span>
                        </div>
                        <input
                          type="number"
                          min="0"
                          step="0.01"
                          {...register('employment.monthlyIncome', { 
                            required: 'Monthly income is required',
                            min: { value: 0, message: 'Income cannot be negative' }
                          })}
                          className="pl-7 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                          placeholder="5000.00"
                        />
                      </div>
                      {errors.employment?.monthlyIncome && (
                        <p className="mt-1 text-sm text-red-600">{errors.employment.monthlyIncome.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Employment Start Date *
                      </label>
                      <input
                        type="date"
                        {...register('employment.employmentStartDate', { required: 'Employment start date is required' })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      />
                      {errors.employment?.employmentStartDate && (
                        <p className="mt-1 text-sm text-red-600">{errors.employment.employmentStartDate.message}</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Emergency Contact */}
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">Emergency Contact</h4>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Name *
                      </label>
                      <input
                        type="text"
                        {...register('emergencyContact.name', { required: 'Emergency contact name is required' })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="Jane Doe"
                      />
                      {errors.emergencyContact?.name && (
                        <p className="mt-1 text-sm text-red-600">{errors.emergencyContact.name.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Phone *
                      </label>
                      <input
                        type="tel"
                        {...register('emergencyContact.phone', { required: 'Emergency contact phone is required' })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="(555) 987-6543"
                      />
                      {errors.emergencyContact?.phone && (
                        <p className="mt-1 text-sm text-red-600">{errors.emergencyContact.phone.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Relationship *
                      </label>
                      <select
                        {...register('emergencyContact.relationship', { required: 'Relationship is required' })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      >
                        <option value="">Select relationship</option>
                        <option value="spouse">Spouse</option>
                        <option value="parent">Parent</option>
                        <option value="sibling">Sibling</option>
                        <option value="child">Child</option>
                        <option value="friend">Friend</option>
                        <option value="other">Other</option>
                      </select>
                      {errors.emergencyContact?.relationship && (
                        <p className="mt-1 text-sm text-red-600">{errors.emergencyContact.relationship.message}</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Notes */}
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Notes
                  </label>
                  <textarea
                    rows={4}
                    {...register('notes')}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    placeholder="Any additional notes about the tenant..."
                  />
                </div>
              </div>
            </div>

            <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                type="submit"
                disabled={loading}
                className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Saving...' : tenant ? 'Update Tenant' : 'Create Tenant'}
              </button>
              <button
                type="button"
                onClick={onClose}
                className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default TenantForm;
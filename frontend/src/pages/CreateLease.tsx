import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { CreateLeaseRequest } from '../types/lease';
import { Property } from '../types/property';
import { Tenant } from '../types/tenant';
import { leaseService } from '../services/leaseService';
import { propertyService } from '../services/propertyService';
import { tenantService } from '../services/tenantService';
import { formatCurrencyWithoutSymbol, roundToCents } from '../utils/currency';
import { 
  ArrowLeftIcon, 
  ArrowRightIcon, 
  CheckIcon,
  HomeIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { isTokenExpired, getTokenTimeUntilExpiration } from '../utils/token';

const CreateLease: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [properties, setProperties] = useState<Property[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    trigger,
    watch,
    setValue,
  } = useForm<CreateLeaseRequest>();

  const watchPropertyId = watch('propertyId');
  const totalSteps = 4;

  const steps = [
    {
      id: 1,
      name: 'Property & Tenant',
      description: 'Select property and tenant',
      icon: HomeIcon,
      fields: ['propertyId', 'tenantId']
    },
    {
      id: 2,
      name: 'Lease Terms',
      description: 'Set lease duration and type',
      icon: CalendarIcon,
      fields: ['startDate', 'endDate', 'leaseType']
    },
    {
      id: 3,
      name: 'Financial Terms',
      description: 'Rent and fees',
      icon: CurrencyDollarIcon,
      fields: ['monthlyRent', 'securityDeposit', 'lateFeePenalty', 'gracePeriodDays']
    },
    {
      id: 4,
      name: 'Additional Terms',
      description: 'Policies and responsibilities',
      icon: DocumentTextIcon,
      fields: ['renewalOption', 'petPolicy']
    }
  ];

  useEffect(() => {
    loadPropertiesAndTenants();
    setDefaultValues();
  }, []);

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

  const setDefaultValues = () => {
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

    // Pre-select property if provided in URL
    const propertyId = searchParams.get('propertyId');
    if (propertyId) {
      setValue('propertyId', propertyId);
    }
  };

  const loadPropertiesAndTenants = async () => {
    try {
      console.log('🔄 Loading properties and tenants...');
      const token = localStorage.getItem('token');
      console.log('🔍 Token exists when loading data:', !!token);
      
      if (token) {
        const timeUntilExpiration = getTokenTimeUntilExpiration(token);
        console.log('🔍 Time until token expiration when loading:', timeUntilExpiration, 'seconds');
        
        if (isTokenExpired(token)) {
          console.warn('🚨 Token is expired when loading data!');
          toast.error('Session expired. Please log in again.');
          navigate('/login');
          return;
        }
      }
      
      const [propertiesData, tenantsData] = await Promise.all([
        propertyService.getPropertiesForLeases(), // Use the lease-specific endpoint
        tenantService.getTenants()
      ]);
      
      console.log('✅ Properties loaded:', propertiesData.length);
      console.log('✅ Tenants loaded:', tenantsData.length);
      
      // Show ALL properties for lease creation (occupied properties can have draft/pending leases)
      // Only filter tenants to active/prospective
      const availableTenants = tenantsData.filter(t => ['active', 'prospective'].includes(t.status || 'prospective'));
      
      setProperties(propertiesData); // Show all properties
      setTenants(availableTenants);
    } catch (error: any) {
      console.error('❌ Error loading properties and tenants:', error);
      console.error('❌ Error response:', error.response?.data);
      console.error('❌ Error status:', error.response?.status);
      toast.error('Failed to load properties and tenants');
    }
  };

  const nextStep = async () => {
    const currentStepData = steps[currentStep - 1];
    const isValid = await trigger(currentStepData.fields as any);
    
    if (isValid) {
      setCurrentStep(prev => Math.min(prev + 1, totalSteps));
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const onSubmit = async (data: CreateLeaseRequest) => {
    try {
      setLoading(true);
      console.log('🔄 Creating lease:', data);
      
      // Check token validity before making the request
      const token = localStorage.getItem('token');
      console.log('🔍 Token exists:', !!token);
      
      if (token) {
        console.log('🔍 Token preview:', token.substring(0, 20) + '...');
        const timeUntilExpiration = getTokenTimeUntilExpiration(token);
        console.log('🔍 Time until token expiration:', timeUntilExpiration, 'seconds');
        
        if (isTokenExpired(token)) {
          console.warn('🚨 Token is expired!');
          toast.error('Session expired. Please log in again.');
          setTimeout(() => {
            window.location.href = '/login';
          }, 2000);
          return;
        }
      } else {
        console.warn('🚨 No token found!');
        toast.error('Please log in to continue.');
        navigate('/login');
        return;
      }
      
      // Ensure currency values are properly rounded
      const processedData: CreateLeaseRequest = {
        ...data,
        monthlyRent: roundToCents(data.monthlyRent),
        securityDeposit: roundToCents(data.securityDeposit || 0),
        lateFeePenalty: roundToCents(data.lateFeePenalty || 0),
        ...(data.petPolicy && {
          petPolicy: {
            ...data.petPolicy,
            deposit: roundToCents(data.petPolicy.deposit || 0),
            monthlyFee: roundToCents(data.petPolicy.monthlyFee || 0)
          }
        })
      };

      const newLease = await leaseService.createLease(processedData);
      console.log('✅ Lease created:', newLease);
      
      toast.success('Lease created successfully!');
      navigate('/dashboard/leases');
    } catch (error: any) {
      console.error('❌ Error creating lease:', error);
      console.error('❌ Error response:', error.response?.data);
      console.error('❌ Error status:', error.response?.status);
      
      if (error.response?.status === 401) {
        toast.error('Session expired. Please log in again.');
      } else {
        toast.error('Failed to create lease. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-8">
            {/* Property Selection */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Select Property</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Property *
                </label>
                <select
                  {...register('propertyId', { required: 'Property is required' })}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
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

              {/* Selected Property Preview */}
              {selectedProperty && (
                <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-4">
                  <h5 className="text-sm font-medium text-green-800 mb-2">Selected Property</h5>
                  <div className="text-sm text-green-700">
                    <p className="font-medium">{selectedProperty.name || selectedProperty.title}</p>
                    <p>{typeof selectedProperty.address === 'object' ? selectedProperty.address.street : selectedProperty.address_line1}, {typeof selectedProperty.address === 'object' ? selectedProperty.address.city : selectedProperty.city}</p>
                    <p>Type: {selectedProperty.type} • Rent: ${formatCurrencyWithoutSymbol(selectedProperty.rentAmount || selectedProperty.rent_amount)}/month</p>
                  </div>
                </div>
              )}
            </div>

            {/* Tenant Selection */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Select Tenant</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tenant *
                </label>
                <select
                  {...register('tenantId', { required: 'Tenant is required' })}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
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
        );

      case 2:
        return (
          <div className="space-y-8">
            {/* Lease Duration */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Lease Duration</h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Start Date *
                  </label>
                  <input
                    type="date"
                    {...register('startDate', { required: 'Start date is required' })}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                  />
                  {errors.startDate && (
                    <p className="mt-1 text-sm text-red-600">{errors.startDate.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    End Date *
                  </label>
                  <input
                    type="date"
                    {...register('endDate', { required: 'End date is required' })}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                  />
                  {errors.endDate && (
                    <p className="mt-1 text-sm text-red-600">{errors.endDate.message}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Lease Type */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Lease Type</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Lease Type *
                </label>
                <select
                  {...register('leaseType', { required: 'Lease type is required' })}
                  className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                >
                  <option value="fixed">Fixed Term</option>
                  <option value="month-to-month">Month-to-Month</option>
                  <option value="yearly">Yearly</option>
                </select>
                {errors.leaseType && (
                  <p className="mt-1 text-sm text-red-600">{errors.leaseType.message}</p>
                )}
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-8">
            {/* Rent & Deposits */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Rent & Deposits</h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Monthly Rent *
                  </label>
                  <div className="relative rounded-md shadow-sm">
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
                      className="block w-full pl-7 border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      placeholder="0.00"
                    />
                  </div>
                  {errors.monthlyRent && (
                    <p className="mt-1 text-sm text-red-600">{errors.monthlyRent.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Security Deposit *
                  </label>
                  <div className="relative rounded-md shadow-sm">
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
                      className="block w-full pl-7 border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      placeholder="0.00"
                    />
                  </div>
                  {errors.securityDeposit && (
                    <p className="mt-1 text-sm text-red-600">{errors.securityDeposit.message}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Fees & Penalties */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Fees & Penalties</h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Late Fee Penalty
                  </label>
                  <div className="relative rounded-md shadow-sm">
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
                      className="block w-full pl-7 border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      placeholder="0.00"
                    />
                  </div>
                  {errors.lateFeePenalty && (
                    <p className="mt-1 text-sm text-red-600">{errors.lateFeePenalty.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Grace Period (Days)
                  </label>
                  <input
                    type="number"
                    {...register('gracePeriodDays', { 
                      min: { value: 0, message: 'Grace period must be non-negative' }
                    })}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    placeholder="5"
                  />
                  {errors.gracePeriodDays && (
                    <p className="mt-1 text-sm text-red-600">{errors.gracePeriodDays.message}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-8">
            {/* Additional Terms */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Additional Terms</h3>
              <div className="space-y-4">
                <div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      {...register('renewalOption')}
                      className="rounded border-gray-300 text-green-600 shadow-sm focus:border-green-300 focus:ring focus:ring-green-200 focus:ring-opacity-50"
                    />
                    <span className="ml-2 text-sm text-gray-700">Renewal Option Available</span>
                  </label>
                  <p className="mt-1 text-sm text-gray-500">Allow tenant to renew lease at the end of term</p>
                </div>
              </div>
            </div>

            {/* Pet Policy */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Pet Policy</h3>
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    {...register('petPolicy.allowed')}
                    className="rounded border-gray-300 text-green-600 shadow-sm focus:border-green-300 focus:ring focus:ring-green-200 focus:ring-opacity-50"
                  />
                  <span className="ml-2 text-sm text-gray-700">Pets Allowed</span>
                </label>
                <p className="mt-1 text-sm text-gray-500">Check if pets are allowed in this property</p>
              </div>
            </div>

            {/* Summary */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h4 className="text-md font-medium text-gray-900 mb-2">Lease Summary</h4>
              <div className="text-sm text-gray-600 space-y-1">
                <p><span className="font-medium">Property:</span> {selectedProperty?.name || selectedProperty?.title}</p>
                <p><span className="font-medium">Monthly Rent:</span> ${watch('monthlyRent')?.toLocaleString() || 0}/month</p>
                <p><span className="font-medium">Security Deposit:</span> ${watch('securityDeposit')?.toLocaleString() || 0}</p>
                <p><span className="font-medium">Lease Type:</span> {watch('leaseType')}</p>
                <p><span className="font-medium">Duration:</span> {watch('startDate')} to {watch('endDate')}</p>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <button
                  onClick={() => navigate('/dashboard/leases')}
                  className="mr-4 inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700"
                >
                  <ArrowLeftIcon className="h-5 w-5 mr-1" />
                  Back to Leases
                </button>
                <h1 className="text-2xl font-bold text-gray-900">Create New Lease</h1>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <nav aria-label="Progress">
          <ol className="flex items-center justify-center space-x-5">
            {steps.map((step, stepIdx) => (
              <li key={step.id} className="flex items-center">
                {stepIdx > 0 && (
                  <div className="hidden sm:block w-5 h-0.5 bg-gray-200 mr-5" />
                )}
                <div className="relative flex items-center justify-center">
                  <div
                    className={`
                      flex items-center justify-center w-10 h-10 rounded-full border-2 
                      ${currentStep > step.id 
                        ? 'bg-green-600 border-green-600' 
                        : currentStep === step.id 
                        ? 'border-green-600 bg-white' 
                        : 'border-gray-300 bg-white'
                      }
                    `}
                  >
                    {currentStep > step.id ? (
                      <CheckIcon className="w-6 h-6 text-white" />
                    ) : (
                      <step.icon 
                        className={`w-6 h-6 ${
                          currentStep === step.id ? 'text-green-600' : 'text-gray-400'
                        }`} 
                      />
                    )}
                  </div>
                  <div className="absolute top-12 w-32 text-center">
                    <div 
                      className={`text-sm font-medium ${
                        currentStep >= step.id ? 'text-green-600' : 'text-gray-500'
                      }`}
                    >
                      {step.name}
                    </div>
                    <div className="text-xs text-gray-400">{step.description}</div>
                  </div>
                </div>
              </li>
            ))}
          </ol>
        </nav>

        {/* Form Content */}
        <div className="mt-16">
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-8">
                {renderStepContent()}
              </div>

              {/* Form Actions */}
              <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between">
                <button
                  type="button"
                  onClick={prevStep}
                  disabled={currentStep === 1}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ArrowLeftIcon className="h-4 w-4 mr-2" />
                  Previous
                </button>

                {currentStep < totalSteps ? (
                  <button
                    type="button"
                    onClick={nextStep}
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  >
                    Next
                    <ArrowRightIcon className="h-4 w-4 ml-2" />
                  </button>
                ) : (
                  <button
                    type="submit"
                    disabled={loading}
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Creating...' : 'Create Lease'}
                    <CheckIcon className="h-4 w-4 ml-2" />
                  </button>
                )}
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateLease;
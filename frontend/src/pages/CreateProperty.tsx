import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { CreatePropertyRequest } from '../types/property';
import { propertyService } from '../services/propertyService';
import { 
  ArrowLeftIcon, 
  ArrowRightIcon, 
  CheckIcon,
  HomeIcon,
  CurrencyDollarIcon,
  SparklesIcon,
  PlusIcon,
  TrashIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const CreateProperty: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [amenities, setAmenities] = useState<string[]>([]);
  const [newAmenity, setNewAmenity] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
    trigger,
    watch,
  } = useForm<CreatePropertyRequest>();

  const totalSteps = 3;

  const steps = [
    {
      id: 1,
      name: 'Basic Info & Address',
      description: 'Property details and location',
      icon: HomeIcon,
      fields: ['name', 'type', 'address.street', 'address.city', 'address.state', 'address.zipCode', 'address.country']
    },
    {
      id: 2,
      name: 'Details & Pricing',
      description: 'Property specs and rent',
      icon: CurrencyDollarIcon,
      fields: ['bedrooms', 'bathrooms', 'squareFeet', 'rentAmount', 'deposit']
    },
    {
      id: 3,
      name: 'Amenities & Description',
      description: 'Final touches',
      icon: SparklesIcon,
      fields: ['description']
    }
  ];

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

  const addAmenity = () => {
    if (newAmenity.trim() && !amenities.includes(newAmenity.trim())) {
      setAmenities([...amenities, newAmenity.trim()]);
      setNewAmenity('');
    }
  };

  const removeAmenity = (index: number) => {
    setAmenities(amenities.filter((_, i) => i !== index));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addAmenity();
    }
  };

  const onSubmit = async (data: CreatePropertyRequest) => {
    try {
      setLoading(true);
      console.log('🔄 Creating property:', { ...data, amenities });
      
      const formData = {
        ...data,
        amenities,
      };

      const newProperty = await propertyService.createProperty(formData);
      console.log('✅ Property created successfully:', newProperty);
      
      toast.success('Property created successfully!');
      navigate('/properties');
    } catch (error) {
      console.error('❌ Error creating property:', error);
      toast.error('Failed to create property');
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-8">
            {/* Basic Information */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Property Name *
                  </label>
                  <input
                    type="text"
                    {...register('name', { required: 'Property name is required' })}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    placeholder="e.g., Sunset Apartments Unit 2A"
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Property Type *
                  </label>
                  <select
                    {...register('type', { required: 'Property type is required' })}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                  >
                    <option value="">Select type</option>
                    <option value="apartment">Apartment</option>
                    <option value="house">House</option>
                    <option value="condo">Condo</option>
                    <option value="townhouse">Townhouse</option>
                    <option value="studio">Studio</option>
                    <option value="commercial">Commercial</option>
                  </select>
                  {errors.type && (
                    <p className="mt-1 text-sm text-red-600">{errors.type.message}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Address Information */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Address Information</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Street Address *
                  </label>
                  <input
                    type="text"
                    {...register('address.street', { required: 'Street address is required' })}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    placeholder="123 Main Street"
                  />
                  {errors.address?.street && (
                    <p className="mt-1 text-sm text-red-600">{errors.address.street.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Unit/Apartment Number
                  </label>
                  <input
                    type="text"
                    {...register('address.unit')}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    placeholder="Apt 2B, Unit 105, etc. (optional)"
                  />
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      City *
                    </label>
                    <input
                      type="text"
                      {...register('address.city', { required: 'City is required' })}
                      className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      placeholder="San Francisco"
                    />
                    {errors.address?.city && (
                      <p className="mt-1 text-sm text-red-600">{errors.address.city.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      State *
                    </label>
                    <input
                      type="text"
                      {...register('address.state', { required: 'State is required' })}
                      className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      placeholder="CA"
                    />
                    {errors.address?.state && (
                      <p className="mt-1 text-sm text-red-600">{errors.address.state.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      ZIP Code *
                    </label>
                    <input
                      type="text"
                      {...register('address.zipCode', { required: 'ZIP code is required' })}
                      className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      placeholder="94102"
                    />
                    {errors.address?.zipCode && (
                      <p className="mt-1 text-sm text-red-600">{errors.address.zipCode.message}</p>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Country *
                  </label>
                  <input
                    type="text"
                    {...register('address.country', { required: 'Country is required' })}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    placeholder="United States"
                    defaultValue="United States"
                  />
                  {errors.address?.country && (
                    <p className="mt-1 text-sm text-red-600">{errors.address.country.message}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Property Details & Pricing</h3>
              <div className="space-y-6">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Bedrooms *
                    </label>
                    <input
                      type="number"
                      min="0"
                      {...register('bedrooms', { 
                        required: 'Number of bedrooms is required',
                        min: { value: 0, message: 'Bedrooms cannot be negative' }
                      })}
                      className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    />
                    {errors.bedrooms && (
                      <p className="mt-1 text-sm text-red-600">{errors.bedrooms.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Bathrooms *
                    </label>
                    <input
                      type="number"
                      min="0"
                      step="0.5"
                      {...register('bathrooms', { 
                        required: 'Number of bathrooms is required',
                        min: { value: 0, message: 'Bathrooms cannot be negative' }
                      })}
                      className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    />
                    {errors.bathrooms && (
                      <p className="mt-1 text-sm text-red-600">{errors.bathrooms.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Square Feet
                    </label>
                    <input
                      type="number"
                      min="0"
                      {...register('squareFeet', { 
                        min: { value: 0, message: 'Square feet cannot be negative' }
                      })}
                      className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      placeholder="e.g., 850"
                    />
                    {errors.squareFeet && (
                      <p className="mt-1 text-sm text-red-600">{errors.squareFeet.message}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Monthly Rent *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <span className="text-gray-500 sm:text-sm">$</span>
                      </div>
                      <input
                        type="number"
                        min="0"
                        step="0.01"
                        {...register('rentAmount', { 
                          required: 'Rent amount is required',
                          min: { value: 0, message: 'Rent cannot be negative' }
                        })}
                        className="block w-full pl-7 border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="2500.00"
                      />
                    </div>
                    {errors.rentAmount && (
                      <p className="mt-1 text-sm text-red-600">{errors.rentAmount.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Security Deposit
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <span className="text-gray-500 sm:text-sm">$</span>
                      </div>
                      <input
                        type="number"
                        min="0"
                        step="0.01"
                        {...register('deposit', { 
                          min: { value: 0, message: 'Deposit cannot be negative' }
                        })}
                        className="block w-full pl-7 border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="2500.00"
                      />
                    </div>
                    {errors.deposit && (
                      <p className="mt-1 text-sm text-red-600">{errors.deposit.message}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Description & Amenities</h3>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Property Description
                  </label>
                  <textarea
                    rows={4}
                    {...register('description')}
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    placeholder="Describe the property, its features, and what makes it special..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Amenities
                  </label>
                  <div className="space-y-3">
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newAmenity}
                        onChange={(e) => setNewAmenity(e.target.value)}
                        onKeyPress={handleKeyPress}
                        className="flex-1 border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="Add an amenity (e.g., Parking, Pool, Gym)"
                      />
                      <button
                        type="button"
                        onClick={addAmenity}
                        className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                      >
                        <PlusIcon className="h-4 w-4" />
                      </button>
                    </div>

                    {amenities.length > 0 && (
                      <div className="space-y-2">
                        <p className="text-sm text-gray-600">Added amenities:</p>
                        <div className="flex flex-wrap gap-2">
                          {amenities.map((amenity, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800"
                            >
                              {amenity}
                              <button
                                type="button"
                                onClick={() => removeAmenity(index)}
                                className="ml-2 inline-flex items-center justify-center w-4 h-4 rounded-full text-green-600 hover:bg-green-200 hover:text-green-800 focus:outline-none"
                              >
                                <TrashIcon className="h-3 w-3" />
                              </button>
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
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
      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/properties')}
            className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 mb-4"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-1" />
            Back to Properties
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Create New Property</h1>
          <p className="mt-2 text-gray-600">Add a new property to your portfolio</p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <nav aria-label="Progress">
            <ol className="flex items-center">
              {steps.map((step, stepIdx) => (
                <li key={step.name} className={`${stepIdx !== steps.length - 1 ? 'pr-8 sm:pr-20' : ''} relative`}>
                  <div className="flex items-center">
                    <div className={`
                      flex items-center justify-center w-10 h-10 rounded-full border-2 
                      ${currentStep > step.id 
                        ? 'bg-green-600 border-green-600' 
                        : currentStep === step.id 
                          ? 'border-green-600 bg-white' 
                          : 'border-gray-300 bg-white'
                      }
                    `}>
                      {currentStep > step.id ? (
                        <CheckIcon className="w-6 h-6 text-white" />
                      ) : (
                        <step.icon className={`w-5 h-5 ${
                          currentStep === step.id ? 'text-green-600' : 'text-gray-400'
                        }`} />
                      )}
                    </div>
                    <div className="ml-4 min-w-0">
                      <p className={`text-sm font-medium ${
                        currentStep >= step.id ? 'text-green-600' : 'text-gray-500'
                      }`}>
                        {step.name}
                      </p>
                      <p className="text-sm text-gray-500">{step.description}</p>
                    </div>
                  </div>
                  {stepIdx !== steps.length - 1 && (
                    <div className="absolute top-5 left-5 -ml-px mt-0.5 h-full w-0.5 bg-gray-300" aria-hidden="true" />
                  )}
                </li>
              ))}
            </ol>
          </nav>
        </div>

        {/* Form */}
        <div className="bg-white shadow-sm rounded-lg">
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="px-6 py-8">
              {renderStepContent()}
            </div>

            {/* Navigation */}
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between">
              <button
                type="button"
                onClick={prevStep}
                disabled={currentStep === 1}
                className={`
                  inline-flex items-center px-4 py-2 text-sm font-medium rounded-md
                  ${currentStep === 1 
                    ? 'text-gray-400 cursor-not-allowed' 
                    : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
                  }
                `}
              >
                <ArrowLeftIcon className="h-4 w-4 mr-2" />
                Previous
              </button>

              {currentStep < totalSteps ? (
                <button
                  type="button"
                  onClick={nextStep}
                  className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  Next
                  <ArrowRightIcon className="h-4 w-4 ml-2" />
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={loading}
                  className="inline-flex items-center px-6 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Creating...
                    </>
                  ) : (
                    <>
                      <CheckIcon className="h-4 w-4 mr-2" />
                      Create Property
                    </>
                  )}
                </button>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateProperty;
import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Property, CreatePropertyRequest, UpdatePropertyRequest } from '../../types/property';
import { XMarkIcon, PhotoIcon, PlusIcon, TrashIcon } from '@heroicons/react/24/outline';

interface PropertyFormProps {
  property?: Property;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreatePropertyRequest | UpdatePropertyRequest) => Promise<void>;
  loading?: boolean;
}

const PropertyForm: React.FC<PropertyFormProps> = ({
  property,
  isOpen,
  onClose,
  onSubmit,
  loading = false,
}) => {
  const [amenities, setAmenities] = useState<string[]>([]);
  const [newAmenity, setNewAmenity] = useState('');

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
    setValue,
    watch,
  } = useForm<CreatePropertyRequest>();

  useEffect(() => {
    if (property) {
      // Populate form with existing property data - try all possible name fields
      const propertyName = property.name || 
                          (property as any).title || 
                          (property as any).name || 
                          '';
      console.log('Populating form with property:', property);
      console.log('Property name found:', propertyName);
      setValue('name', propertyName);
      
      // Handle address - parse address_line1 to separate street and unit
      const addressLine1 = (property as any).address_line1 || '';
      const city = (property as any).city || '';
      const state = (property as any).state || '';
      const zipCode = (property as any).zipCode || (property as any).zip_code || '';
      
      // Parse street and unit from address_line1 (format: "123 Main St, Apt 2B")
      let street = '';
      let unit = '';
      
      if (addressLine1) {
        console.log('🏠 Parsing address_line1:', addressLine1);
        // Look for comma to separate street from unit
        const commaIndex = addressLine1.lastIndexOf(',');
        if (commaIndex > 0) {
          street = addressLine1.substring(0, commaIndex).trim();
          unit = addressLine1.substring(commaIndex + 1).trim();
          console.log('🏠 Parsed - Street:', street, 'Unit:', unit);
        } else {
          // No comma found, entire string is street
          street = addressLine1.trim();
          console.log('🏠 No comma found - Street:', street, 'Unit: (empty)');
        }
      }
      
      if (typeof property.address === 'string') {
        // For string addresses, we'll need to parse or set defaults
        setValue('address.street', street);
        setValue('address.unit', unit);
        setValue('address.city', city);
        setValue('address.state', state);
        setValue('address.zipCode', zipCode);
        setValue('address.country', 'USA');
      } else if (property.address && typeof property.address === 'object') {
        setValue('address.street', property.address.street || street);
        setValue('address.unit', property.address.unit || unit);
        setValue('address.city', property.address.city || city);
        setValue('address.state', property.address.state || state);
        setValue('address.zipCode', property.address.zipCode || zipCode);
        setValue('address.country', property.address.country || 'USA');
      } else {
        // Use parsed fields from API
        setValue('address.street', street);
        setValue('address.unit', unit);
        setValue('address.city', city);
        setValue('address.state', state);
        setValue('address.zipCode', zipCode);
        setValue('address.country', 'USA');
      }
      
      setValue('type', (property.type || 'apartment') as any);
      setValue('bedrooms', property.bedrooms || 0);
      setValue('bathrooms', property.bathrooms || 0);
      setValue('squareFeet', property.squareFeet || (property as any).square_feet || 0);
      setValue('rentAmount', property.rentAmount || (property as any).rent_amount || 0);
      setValue('deposit', property.deposit || 0);
      setValue('description', property.description || '');
      setAmenities(property.amenities || []);
    } else {
      // Reset form for new property
      reset();
      setAmenities([]);
    }
  }, [property, setValue, reset]);

  const handleFormSubmit = async (data: CreatePropertyRequest) => {
    const formData = {
      ...data,
      amenities,
      ...(property && { id: property.id }),
    };

    await onSubmit(formData as CreatePropertyRequest | UpdatePropertyRequest);
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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          <form onSubmit={handleSubmit(handleFormSubmit)}>
            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  {property ? 'Edit Property' : 'Add New Property'}
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
                {/* Basic Information */}
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">Basic Information</h4>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Property Name *
                      </label>
                      <input
                        type="text"
                        {...register('name', { required: 'Property name is required' })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="e.g., Sunset Apartments Unit 2A"
                      />
                      {errors.name && (
                        <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Property Type *
                      </label>
                      <select
                        {...register('type', { required: 'Property type is required' })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
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

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Unit/Apartment Number
                      </label>
                      <input
                        type="text"
                        {...register('address.unit')}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        placeholder="Apt 2B, Unit 105, etc. (optional)"
                      />
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

                {/* Property Details */}
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">Property Details</h4>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Bedrooms *
                      </label>
                      <input
                        type="number"
                        min="0"
                        {...register('bedrooms', { 
                          required: 'Number of bedrooms is required',
                          min: { value: 0, message: 'Bedrooms cannot be negative' }
                        })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      />
                      {errors.bedrooms && (
                        <p className="mt-1 text-sm text-red-600">{errors.bedrooms.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
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
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      />
                      {errors.bathrooms && (
                        <p className="mt-1 text-sm text-red-600">{errors.bathrooms.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Square Feet *
                      </label>
                      <input
                        type="number"
                        min="0"
                        {...register('squareFeet', { 
                          required: 'Square footage is required',
                          min: { value: 0, message: 'Square feet cannot be negative' }
                        })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      />
                      {errors.squareFeet && (
                        <p className="mt-1 text-sm text-red-600">{errors.squareFeet.message}</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Financial Information */}
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">Financial Information</h4>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
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
                          min="0"
                          step="0.01"
                          {...register('rentAmount', { 
                            required: 'Rent amount is required',
                            min: { value: 0, message: 'Rent cannot be negative' }
                          })}
                          className="pl-7 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                          placeholder="0.00"
                        />
                      </div>
                      {errors.rentAmount && (
                        <p className="mt-1 text-sm text-red-600">{errors.rentAmount.message}</p>
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
                          min="0"
                          step="0.01"
                          {...register('deposit', { 
                            required: 'Deposit amount is required',
                            min: { value: 0, message: 'Deposit cannot be negative' }
                          })}
                          className="pl-7 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                          placeholder="0.00"
                        />
                      </div>
                      {errors.deposit && (
                        <p className="mt-1 text-sm text-red-600">{errors.deposit.message}</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Description
                  </label>
                  <textarea
                    rows={4}
                    {...register('description')}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    placeholder="Describe the property, its features, and any special notes..."
                  />
                </div>

                {/* Amenities */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Amenities
                  </label>
                  <div className="flex space-x-2 mb-3">
                    <input
                      type="text"
                      value={newAmenity}
                      onChange={(e) => setNewAmenity(e.target.value)}
                      onKeyPress={handleKeyPress}
                      className="flex-1 border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      placeholder="Add amenity (e.g., Pool, Gym, Parking)"
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
                            className="ml-2 text-green-600 hover:text-green-800"
                          >
                            <TrashIcon className="h-3 w-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                type="submit"
                disabled={loading}
                className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Saving...' : property ? 'Update Property' : 'Create Property'}
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

export default PropertyForm;
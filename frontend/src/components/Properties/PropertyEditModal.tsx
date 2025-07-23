import React, { useState, useEffect } from 'react';
import { Dialog } from '@headlessui/react';
import { useForm } from 'react-hook-form';
import { XMarkIcon, PencilIcon } from '@heroicons/react/24/outline';
import { Property } from '../../types/property';

interface PropertyEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  property: Property;
  onSubmit: (data: Partial<Property>) => Promise<void>;
}

interface PropertyEditForm {
  name: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
  propertyType: 'apartment' | 'house' | 'condo' | 'townhouse' | 'commercial';
  bedrooms: number;
  bathrooms: number;
  squareFootage: number;
  yearBuilt: number;
  description: string;
  amenities: string;
  notes: string;
  monthlyRent: number;
  status: 'available' | 'occupied' | 'maintenance' | 'inactive';
}

const PropertyEditModal: React.FC<PropertyEditModalProps> = ({
  isOpen,
  onClose,
  property,
  onSubmit
}) => {
  const [loading, setLoading] = useState(false);
  
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm<PropertyEditForm>();

  useEffect(() => {
    if (isOpen && property) {
      console.log('🏠 PropertyEditModal - Property data:', property);
      
      // Handle address structure - most API responses will have address as string
      const isAddressObject = typeof property.address === 'object' && property.address !== null;
      
      let addressString = '';
      let city = '';
      let state = '';
      let zipCode = '';
      let country = 'US';
      
      if (isAddressObject) {
        // If address is an object, extract fields
        const addressObj = property.address as {street?: string; city?: string; state?: string; zipCode?: string; country?: string;};
        addressString = addressObj.street || '';
        city = addressObj.city || '';
        state = addressObj.state || '';
        zipCode = addressObj.zipCode || '';
        country = addressObj.country || 'US';
      } else if (typeof property.address === 'string') {
        // If address is a string, try to parse it into components
        const addressParts = property.address.split(',').map(part => part.trim());
        console.log('🏠 PropertyEditModal - Parsing address string:', property.address);
        console.log('🏠 PropertyEditModal - Address parts:', addressParts);
        
        if (addressParts.length >= 1) {
          addressString = addressParts[0]; // Street address
        }
        if (addressParts.length >= 2) {
          city = addressParts[1]; // City
        }
        if (addressParts.length >= 3) {
          // Last part might be "State ZIP" format
          const lastPart = addressParts[2];
          const stateZipMatch = lastPart.match(/^([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$/);
          if (stateZipMatch) {
            state = stateZipMatch[1];
            zipCode = stateZipMatch[2];
          } else {
            // If no match, put the whole thing in state field
            state = lastPart;
          }
        }
        
        console.log('🏠 PropertyEditModal - Parsed address:', {
          street: addressString,
          city: city,
          state: state,
          zipCode: zipCode
        });
      }
        
      reset({
        name: property.name || '',
        address: addressString,
        city: city,
        state: state,
        zipCode: zipCode,
        country: country,
        propertyType: (property.type || 'apartment') as any,
        bedrooms: property.bedrooms || 0,
        bathrooms: property.bathrooms || 0,
        squareFootage: property.squareFeet || property.square_feet || 0,
        yearBuilt: new Date().getFullYear(), // Property type doesn't have yearBuilt
        description: property.description || '',
        amenities: Array.isArray(property.amenities) ? property.amenities.join(', ') : '',
        notes: '', // Property type doesn't have notes
        monthlyRent: property.rentAmount || property.rent_amount || 0,
        status: (property.status || 'available') as any,
      });
    }
  }, [isOpen, property, reset]);

  const handleFormSubmit = async (data: PropertyEditForm) => {
    try {
      setLoading(true);
      console.log('🏠 PropertyEditModal - Form data submitted:', data);
      
      const updateData: Partial<Property> = {
        id: property.id,
        name: data.name,
        address: {
          street: data.address,
          city: data.city,
          state: data.state,
          zipCode: data.zipCode,
          country: data.country,
        },
        type: data.propertyType,
        bedrooms: data.bedrooms,
        bathrooms: Math.round((data.bathrooms || 0) * 2) / 2, // Ensure proper 0.5 increments
        squareFeet: data.squareFootage,
        description: data.description,
        amenities: data.amenities.split(',').map(a => a.trim()).filter(Boolean),
        rentAmount: Math.round((data.monthlyRent || 0) * 100) / 100, // Ensure proper currency precision
        status: data.status,
      };

      console.log('🏠 PropertyEditModal - Sending update data:', updateData);
      await onSubmit(updateData);
      console.log('✅ PropertyEditModal - Update successful');
      onClose();
    } catch (error) {
      console.error('❌ PropertyEditModal - Update failed:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black bg-opacity-25" />
      
      <div className="fixed inset-0 overflow-y-auto">
        <div className="flex min-h-full items-center justify-center p-4 text-center">
          <Dialog.Panel className="w-full max-w-4xl transform overflow-hidden rounded-lg bg-white p-6 text-left align-middle shadow-xl transition-all">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center">
                <PencilIcon className="h-6 w-6 text-blue-600 mr-3" />
                <div>
                  <Dialog.Title className="text-lg font-medium text-gray-900">
                    Edit Property
                  </Dialog.Title>
                  <p className="text-sm text-gray-500">
                    Update property information
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="rounded-md bg-white text-gray-400 hover:text-gray-500"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
              {/* Basic Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900">Basic Information</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Property Name *
                    </label>
                    <input
                      type="text"
                      {...register('name', { required: 'Property name is required' })}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    {errors.name && (
                      <p className="mt-1 text-xs text-red-600">{errors.name.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Property Type
                    </label>
                    <select
                      {...register('propertyType')}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                      <option value="apartment">Apartment</option>
                      <option value="house">House</option>
                      <option value="condo">Condo</option>
                      <option value="townhouse">Townhouse</option>
                      <option value="commercial">Commercial</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Address *
                  </label>
                  <input
                    type="text"
                    {...register('address', { required: 'Address is required' })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                  {errors.address && (
                    <p className="mt-1 text-xs text-red-600">{errors.address.message}</p>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      City *
                    </label>
                    <input
                      type="text"
                      {...register('city', { required: 'City is required' })}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    {errors.city && (
                      <p className="mt-1 text-xs text-red-600">{errors.city.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      State *
                    </label>
                    <input
                      type="text"
                      {...register('state', { required: 'State is required' })}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    {errors.state && (
                      <p className="mt-1 text-xs text-red-600">{errors.state.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      ZIP Code
                    </label>
                    <input
                      type="text"
                      {...register('zipCode')}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Country
                    </label>
                    <input
                      type="text"
                      {...register('country')}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>

              {/* Property Details */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900">Property Details</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Bedrooms
                    </label>
                    <input
                      type="number"
                      {...register('bedrooms', { min: 0 })}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Bathrooms
                      <span className="text-xs text-gray-500 ml-1">(0.5 for half bath)</span>
                    </label>
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      placeholder="2.5"
                      {...register('bathrooms', { 
                        min: { value: 0, message: 'Bathrooms must be positive' },
                        valueAsNumber: true,
                        setValueAs: (value) => {
                          // Round to nearest 0.5 (half bathroom)
                          const num = parseFloat(value);
                          return isNaN(num) ? 0 : Math.round(num * 2) / 2;
                        }
                      })}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Square Footage
                    </label>
                    <input
                      type="number"
                      {...register('squareFootage', { min: 0 })}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Year Built
                    </label>
                    <input
                      type="number"
                      {...register('yearBuilt', { min: 1800, max: new Date().getFullYear() })}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Monthly Rent
                    </label>
                    <div className="relative">
                      <span className="absolute left-3 top-2 text-gray-500">$</span>
                      <input
                        type="number"
                        step="1"
                        min="0"
                        {...register('monthlyRent', { 
                          min: 0,
                          valueAsNumber: true,
                          setValueAs: (value) => {
                            // Round to nearest cent to avoid floating point issues
                            const num = parseFloat(value);
                            return isNaN(num) ? 0 : Math.round(num * 100) / 100;
                          }
                        })}
                        className="pl-8 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Status
                    </label>
                    <select
                      {...register('status')}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                      <option value="available">Available</option>
                      <option value="occupied">Occupied</option>
                      <option value="maintenance">Under Maintenance</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Description and Amenities */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    {...register('description')}
                    rows={3}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    placeholder="Detailed description of the property..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Amenities
                  </label>
                  <textarea
                    {...register('amenities')}
                    rows={2}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    placeholder="Comma-separated amenities (e.g., Pool, Gym, Parking)"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Notes
                  </label>
                  <textarea
                    {...register('notes')}
                    rows={2}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    placeholder="Internal notes about this property..."
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
                <button
                  type="button"
                  onClick={onClose}
                  disabled={loading}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  {loading && (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  )}
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </Dialog.Panel>
        </div>
      </div>
    </Dialog>
  );
};

export default PropertyEditModal;
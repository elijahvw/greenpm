import React from 'react';
import { Property } from '../../types/property';
import { 
  HomeIcon, 
  MapPinIcon, 
  CurrencyDollarIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon
} from '@heroicons/react/24/outline';

interface PropertyCardProps {
  property: Property;
  onEdit: (property: Property) => void;
  onDelete: (propertyId: string) => void;
  onView: (property: Property) => void;
}

const PropertyCard: React.FC<PropertyCardProps> = ({ 
  property, 
  onEdit, 
  onDelete, 
  onView 
}) => {

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'bg-green-100 text-green-800';
      case 'occupied':
        return 'bg-blue-100 text-blue-800';
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPropertyTypeIcon = (type: string) => {
    switch (type) {
      case 'house':
        return '🏠';
      case 'apartment':
        return '🏢';
      case 'condo':
        return '🏘️';
      case 'townhouse':
        return '🏘️';
      case 'commercial':
        return '🏢';
      default:
        return '🏠';
    }
  };

  const formatAddress = (address: any) => {
    // Handle both string and object address formats
    if (typeof address === 'string') {
      return address;
    }
    return `${address.street}, ${address.city}, ${address.state} ${address.zipCode}`;
  };

  return (
    <div className="bg-white overflow-hidden shadow-sm rounded-lg hover:shadow-md transition-shadow">
      {/* Property Image */}
      <div className="h-48 bg-gray-200 relative">
        {property.images && property.images.length > 0 ? (
          <img
            src={property.images[0]}
            alt={property.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <HomeIcon className="h-16 w-16 text-gray-400" />
          </div>
        )}
        
        {/* Status Badge */}
        <div className="absolute top-3 right-3">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(property.status || 'available')}`}>
            {property.status ? property.status.charAt(0).toUpperCase() + property.status.slice(1) : 'Available'}
          </span>
        </div>

        {/* Property Type Icon */}
        <div className="absolute top-3 left-3">
          <div className="bg-white bg-opacity-90 rounded-full p-2">
            <span className="text-lg">{getPropertyTypeIcon(property.type)}</span>
          </div>
        </div>
      </div>

      {/* Property Details */}
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {property.name}
            </h3>
            
            <div className="flex items-center text-sm text-gray-600 mb-2">
              <MapPinIcon className="h-4 w-4 mr-1" />
              <span>{formatAddress(property.address)}</span>
            </div>

            <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
              <span>{property.bedrooms} bed</span>
              <span>{property.bathrooms} bath</span>
              <span>{(property.squareFeet || property.square_feet || 0).toLocaleString()} sq ft</span>
            </div>

            <div className="flex items-center text-lg font-bold text-green-600 mb-4">
              <CurrencyDollarIcon className="h-5 w-5 mr-1" />
              <span>${(property.rentAmount || property.rent_amount || 0).toLocaleString()}/month</span>
            </div>

            {/* Amenities */}
            {property.amenities && property.amenities.length > 0 && (
              <div className="mb-4">
                <div className="flex flex-wrap gap-1">
                  {property.amenities.slice(0, 3).map((amenity, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                    >
                      {amenity}
                    </span>
                  ))}
                  {property.amenities.length > 3 && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      +{property.amenities.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-2 pt-4 border-t border-gray-200">
          <button
            onClick={() => onView(property)}
            className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <EyeIcon className="h-4 w-4 mr-1" />
            View
          </button>
          
          <button
            onClick={() => onEdit(property)}
            className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <PencilIcon className="h-4 w-4 mr-1" />
            Edit
          </button>
          
          <button
            onClick={() => onDelete(property.id)}
            className="inline-flex items-center justify-center px-3 py-2 border border-red-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default PropertyCard;
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Property } from '../../types/property';
import { formatCurrencyWithoutSymbol } from '../../utils/currency';
import { 
  HomeIcon, 
  MapPinIcon, 
  CurrencyDollarIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  DocumentTextIcon,
  PlusIcon,
  UserIcon,
  CalendarIcon
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
  const navigate = useNavigate();

  const getLeaseStatusColor = (leaseStatus: string) => {
    switch (leaseStatus) {
      case 'vacant':
        return 'bg-green-100 text-green-800';
      case 'occupied':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

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

  const formatAddress = (property: Property) => {
    // Always build complete address from individual fields to ensure city, state, zip are included
    const street = (property as any).street || (property as any).address_line1 || (property as any).address || '';
    const unit = (property as any).unit || (property as any).address_line2 || '';
    const city = (property as any).city || '';
    const state = (property as any).state || '';
    const zipCode = (property as any).zipCode || (property as any).zip_code || '';
    
    // Build address string from individual components
    const streetWithUnit = unit ? `${street}, ${unit}` : street;
    const parts = [streetWithUnit, city, state, zipCode].filter(part => part && part.trim());
    return parts.length > 0 ? parts.join(', ') : 'Address not available';
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
        
        {/* Lease Status Badge */}
        <div className="absolute top-3 right-3">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getLeaseStatusColor(property.lease_status || 'vacant')}`}>
            {property.lease_status ? property.lease_status.charAt(0).toUpperCase() + property.lease_status.slice(1) : 'Vacant'}
          </span>
        </div>

        {/* Property Type Icon */}
        <div className="absolute top-3 left-3">
          <div className="bg-white bg-opacity-90 rounded-full p-2">
            <span className="text-lg">{getPropertyTypeIcon(property.type || 'apartment')}</span>
          </div>
        </div>
      </div>

      {/* Property Details */}
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {property.name || (property as any).title || 'Untitled Property'}
            </h3>
            
            <div className="flex items-start text-sm text-gray-600 mb-2">
              <MapPinIcon className="h-4 w-4 mr-1 flex-shrink-0 mt-0.5" />
              <span className="break-words">{formatAddress(property)}</span>
            </div>

            <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
              <span>{property.bedrooms} bed</span>
              <span>{property.bathrooms} bath</span>
              <span>{(property.squareFeet || property.square_feet || 0).toLocaleString()} sq ft</span>
            </div>

            <div className="flex items-center text-lg font-bold text-green-600 mb-4">
              <CurrencyDollarIcon className="h-5 w-5 mr-1" />
              <span>${formatCurrencyWithoutSymbol(property.rentAmount || property.rent_amount)}/month</span>
            </div>

            {/* Lease Information - Show current active lease */}
            {property.current_lease && (property.current_lease.status === 'active' || !property.current_lease.status) && (
              <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center text-sm text-blue-800 mb-2">
                  <UserIcon className="h-4 w-4 mr-1" />
                  <span className="font-medium">{property.current_lease.tenant_name}</span>
                </div>
                <div className="flex items-center justify-between text-xs text-blue-600">
                  <div className="flex items-center">
                    <CalendarIcon className="h-3 w-3 mr-1" />
                    <span>
                      Lease ends: {property.current_lease.end_date ? 
                        (() => {
                          const dateString = property.current_lease.end_date;
                          const date = dateString.includes('T') 
                            ? new Date(dateString) 
                            : new Date(dateString + 'T00:00:00');
                          return date.toLocaleDateString();
                        })() : 
                        'N/A'
                      }
                    </span>
                  </div>
                  <div className="flex items-center">
                    <CurrencyDollarIcon className="h-3 w-3 mr-1" />
                    <span>${property.current_lease.monthly_rent?.toLocaleString() || 0}/mo</span>
                  </div>
                </div>
              </div>
            )}

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
        <div className="space-y-2 pt-4 border-t border-gray-200">
          {/* Primary Actions */}
          <div className="flex space-x-2">
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

          {/* Lease Actions */}
          <div className="flex space-x-2">
            {property.lease_status === 'vacant' ? (
              <button
                onClick={() => navigate(`/dashboard/leases/create?propertyId=${property.id}`)}
                className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-green-300 shadow-sm text-sm leading-4 font-medium rounded-md text-green-700 bg-green-50 hover:bg-green-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <PlusIcon className="h-4 w-4 mr-1" />
                Create Lease
              </button>
            ) : (
              <button
                onClick={() => navigate(`/dashboard/leases?propertyId=${property.id}`)}
                className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-blue-300 shadow-sm text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <DocumentTextIcon className="h-4 w-4 mr-1" />
                View Lease
              </button>
            )}
            
            <button
              onClick={() => navigate(`/dashboard/leases?propertyId=${property.id}`)}
              className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <DocumentTextIcon className="h-4 w-4 mr-1" />
              Lease History
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PropertyCard;
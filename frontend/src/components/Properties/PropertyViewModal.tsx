import React, { useState, useEffect } from 'react';
import { Property } from '../../types/property';
import { Lease } from '../../types/lease';
import { leaseService } from '../../services/leaseService';
import Modal from '../Common/Modal';
import {
  MapPinIcon,
  HomeIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  TagIcon,
} from '@heroicons/react/24/outline';

interface PropertyViewModalProps {
  isOpen: boolean;
  onClose: () => void;
  property: Property;
  onViewLeases?: (propertyId: string) => void;
  onEdit?: (property: Property) => void;
}

const PropertyViewModal: React.FC<PropertyViewModalProps> = ({
  isOpen,
  onClose,
  property,
  onViewLeases,
  onEdit
}) => {
  // Use lease data from property instead of separate API call
  const activeLease = property?.current_lease ? {
    id: property.current_lease.id,
    propertyId: property.id,
    property_id: property.id,
    tenant_name: property.current_lease.tenant_name,
    tenant_email: property.current_lease.tenant_email,
    start_date: property.current_lease.start_date,
    end_date: property.current_lease.end_date,
    startDate: property.current_lease.start_date, // Add camelCase version
    endDate: property.current_lease.end_date, // Add camelCase version  
    monthly_rent: property.current_lease.monthly_rent,
    rent_amount: property.current_lease.monthly_rent,
    monthlyRent: property.current_lease.monthly_rent, // Add camelCase version
    status: property.current_lease.status,
  } : null;

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

  const rentAmount = property.rentAmount || property.rent_amount || 0;
  const squareFeet = property.squareFeet || property.square_feet || 0;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Property Details" maxWidth="2xl">
      <div className="space-y-6">
        {/* Property Header */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h2 className="text-xl font-bold text-gray-900 mb-2">{property.name || (property as any).title || 'Untitled Property'}</h2>
          <div className="flex items-center text-gray-600 mb-2">
            <MapPinIcon className="h-5 w-5 mr-2" />
            <span>{formatAddress(property)}</span>
          </div>
          <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            <TagIcon className="h-4 w-4 mr-1" />
            {property.status ? property.status.charAt(0).toUpperCase() + property.status.slice(1) : 'Available'}
          </div>
        </div>

        {/* Property Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Basic Info */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
              Basic Information
            </h3>
            
            <div className="space-y-3">
              <div className="flex items-center">
                <HomeIcon className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <span className="text-sm font-medium text-gray-500">Property Type</span>
                  <p className="text-sm text-gray-900 capitalize">{property.type}</p>
                </div>
              </div>
              
              <div className="flex items-center">
                <div className="h-5 w-5 text-gray-400 mr-3 flex items-center justify-center">
                  <span className="text-xs font-bold">BR</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Bedrooms</span>
                  <p className="text-sm text-gray-900">{property.bedrooms}</p>
                </div>
              </div>
              
              <div className="flex items-center">
                <div className="h-5 w-5 text-gray-400 mr-3 flex items-center justify-center">
                  <span className="text-xs font-bold">BA</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Bathrooms</span>
                  <p className="text-sm text-gray-900">{property.bathrooms}</p>
                </div>
              </div>
              
              <div className="flex items-center">
                <div className="h-5 w-5 text-gray-400 mr-3 flex items-center justify-center">
                  <span className="text-xs font-bold">SF</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Square Feet</span>
                  <p className="text-sm text-gray-900">{squareFeet.toLocaleString()} sq ft</p>
                </div>
              </div>
            </div>
          </div>

          {/* Financial Info */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
              Financial Information
            </h3>
            
            <div className="space-y-3">
              <div className="flex items-center">
                <CurrencyDollarIcon className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <span className="text-sm font-medium text-gray-500">Monthly Rent</span>
                  <p className="text-lg font-bold text-green-600">${rentAmount.toLocaleString()}</p>
                </div>
              </div>
              
              <div className="flex items-center">
                <CurrencyDollarIcon className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <span className="text-sm font-medium text-gray-500">Security Deposit</span>
                  <p className="text-sm text-gray-900">${(property.deposit || 0).toLocaleString()}</p>
                </div>
              </div>
              
              <div className="flex items-center">
                <CalendarIcon className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <span className="text-sm font-medium text-gray-500">Created</span>
                  <p className="text-sm text-gray-900">
                    {property.createdAt || property.created_at ? 
                      new Date(property.createdAt || property.created_at || '').toLocaleDateString() : 
                      'Unknown'
                    }
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Description */}
        {property.description && (
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
              Description
            </h3>
            <p className="text-sm text-gray-700 leading-relaxed">
              {property.description}
            </p>
          </div>
        )}

        {/* Amenities */}
        {property.amenities && property.amenities.length > 0 && (
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
              Amenities
            </h3>
            <div className="flex flex-wrap gap-2">
              {property.amenities.map((amenity, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  {amenity}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Current Lease Information */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900">Current Lease</h3>
            {onViewLeases && property.id && (
              <button
                onClick={() => onViewLeases(property.id!)}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                View All Leases →
              </button>
            )}
          </div>

          {false ? (
            <div className="flex items-center justify-center py-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className="ml-2 text-sm text-gray-600">Loading lease...</span>
            </div>
          ) : activeLease ? (
            <div className="space-y-2">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-900">Tenant:</span>
                  <p className="text-sm text-gray-600">{activeLease.tenant_name || 'Unknown'}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-900">Monthly Rent:</span>
                  <p className="text-sm text-gray-600">
                    ${(activeLease.monthlyRent || activeLease.rent_amount || 0).toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-900">Start Date:</span>
                  <p className="text-sm text-gray-600">
                    {new Date(activeLease.startDate || activeLease.start_date || '').toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-900">End Date:</span>
                  <p className="text-sm text-gray-600">
                    {new Date(activeLease.endDate || activeLease.end_date || '').toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center justify-between pt-2 border-t border-gray-200">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Active Lease
                </span>
                <span className="text-xs text-gray-500">Lease ID: #{activeLease.id}</span>
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-sm text-gray-500 mb-2">No active lease for this property</p>
              <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                Available
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          {onViewLeases && property.id && (
            <button
              type="button"
              className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              onClick={() => onViewLeases(property.id!)}
            >
              View Leases
            </button>
          )}
          {onEdit && (
            <button
              type="button"
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              onClick={() => onEdit(property)}
            >
              Edit Property
            </button>
          )}
          <button
            type="button"
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default PropertyViewModal;
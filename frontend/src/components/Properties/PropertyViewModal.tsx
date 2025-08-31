import React, { useState, useEffect } from 'react';
import { Property } from '../../types/property';
import { Lease } from '../../types/lease';
import { leaseService } from '../../services/leaseService';
import { propertyService } from '../../services/propertyService';
import Modal from '../Common/Modal';
import {
  MapPinIcon,
  HomeIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  TagIcon,
  PhotoIcon,
  ArrowUpTrayIcon,
  TrashIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

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
  const [images, setImages] = useState<any[]>([]);
  const [uploadingImages, setUploadingImages] = useState(false);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [showImageGallery, setShowImageGallery] = useState(false);

  // Fetch images when modal opens
  useEffect(() => {
    if (isOpen && property?.id) {
      fetchImages();
    }
  }, [isOpen, property?.id]);

  const fetchImages = async () => {
    try {
      const imageData = await propertyService.getPropertyImages(property.id);
      setImages(imageData.images || []);
    } catch (error) {
      console.error('Error fetching property images:', error);
    }
  };

  const handleImageUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    setUploadingImages(true);
    try {
      const fileArray = Array.from(files);
      const response = await propertyService.uploadPropertyImages(property.id, fileArray);
      
      toast.success(`Successfully uploaded ${fileArray.length} image(s)`);
      
      // Refresh images
      fetchImages();
    } catch (error) {
      console.error('Error uploading images:', error);
      toast.error('Failed to upload images');
    } finally {
      setUploadingImages(false);
    }
  };

  const handleImageDelete = async (imageId: string) => {
    if (!window.confirm('Are you sure you want to delete this image?')) return;

    try {
      await propertyService.deletePropertyImage(property.id, imageId);
      toast.success('Image deleted successfully');
      fetchImages();
    } catch (error) {
      console.error('Error deleting image:', error);
      toast.error('Failed to delete image');
    }
  };

  const nextImage = () => {
    setSelectedImageIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = () => {
    setSelectedImageIndex((prev) => (prev - 1 + images.length) % images.length);
  };

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
    // Handle both nested address object and flat address fields
    const address = property.address;
    
    let street, unit, city, state, zipCode;
    
    if (address && typeof address === 'object') {
      // New nested address structure
      street = address.street || '';
      unit = address.unit || '';
      city = address.city || '';
      state = address.state || '';
      zipCode = address.zipCode || '';
    } else {
      // Fallback to old flat structure
      street = (property as any).street || (property as any).address_line1 || (property as any).address || '';
      unit = (property as any).unit || (property as any).address_line2 || '';
      city = (property as any).city || '';
      state = (property as any).state || '';
      zipCode = (property as any).zipCode || (property as any).zip_code || '';
    }
    
    // Build address string from individual components - ensure all parts are strings
    const streetWithUnit = unit ? `${String(street)}, ${String(unit)}` : String(street);
    const parts = [streetWithUnit, city, state, zipCode]
      .map(part => String(part || ''))
      .filter(part => part.trim());
    
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

        {/* Property Images */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
            Property Images
          </h3>

          {/* Image Upload */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
            <div className="text-center">
              <PhotoIcon className="mx-auto h-8 w-8 text-gray-400" />
              <div className="mt-2">
                <label
                  htmlFor="image-upload"
                  className="cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                >
                  <span className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                    <ArrowUpTrayIcon className="h-4 w-4 mr-2" />
                    {uploadingImages ? 'Uploading...' : 'Upload Images'}
                  </span>
                  <input
                    id="image-upload"
                    name="image-upload"
                    type="file"
                    className="sr-only"
                    multiple
                    accept="image/*"
                    onChange={(e) => handleImageUpload(e.target.files)}
                    disabled={uploadingImages}
                  />
                </label>
              </div>
              <p className="mt-1 text-xs text-gray-500">
                JPG, JPEG, PNG up to 10MB each
              </p>
            </div>
          </div>

          {/* Image Gallery */}
          {images.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-700">Uploaded Images ({images.length})</h4>
              
              {/* Main Image Display */}
              {images.length > 0 && (
                <div className="relative">
                  <img
                    src={images[selectedImageIndex]?.image_url}
                    alt={`Property image ${selectedImageIndex + 1}`}
                    className="w-full h-64 object-cover rounded-lg cursor-pointer"
                    onClick={() => setShowImageGallery(true)}
                  />
                  {images.length > 1 && (
                    <>
                      <button
                        onClick={prevImage}
                        className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70"
                      >
                        <ChevronLeftIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={nextImage}
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70"
                      >
                        <ChevronRightIcon className="h-4 w-4" />
                      </button>
                      <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
                        {selectedImageIndex + 1} / {images.length}
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* Thumbnail Gallery */}
              <div className="grid grid-cols-4 gap-2">
                {images.map((image, index) => (
                  <div key={image.id} className="relative group">
                    <img
                      src={image.image_url}
                      alt={`Property thumbnail ${index + 1}`}
                      className={`w-full h-20 object-cover rounded cursor-pointer transition-opacity ${
                        index === selectedImageIndex ? 'ring-2 ring-blue-500' : ''
                      }`}
                      onClick={() => setSelectedImageIndex(index)}
                    />
                    <button
                      onClick={() => handleImageDelete(image.id)}
                      className="absolute top-1 right-1 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                    >
                      <TrashIcon className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {images.length === 0 && (
            <div className="text-center py-4">
              <PhotoIcon className="mx-auto h-12 w-12 text-gray-300" />
              <p className="mt-2 text-sm text-gray-500">No images uploaded yet</p>
            </div>
          )}
        </div>

        {/* Full Screen Image Gallery Modal */}
        {showImageGallery && (
          <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center">
            <div className="relative max-w-4xl max-h-screen p-4">
              <button
                onClick={() => setShowImageGallery(false)}
                className="absolute top-4 right-4 text-white text-xl hover:text-gray-300 z-10"
              >
                ✕
              </button>
              <img
                src={images[selectedImageIndex]?.image_url}
                alt={`Property image ${selectedImageIndex + 1}`}
                className="max-w-full max-h-full object-contain"
              />
              {images.length > 1 && (
                <>
                  <button
                    onClick={prevImage}
                    className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-3 rounded-full hover:bg-opacity-70"
                  >
                    <ChevronLeftIcon className="h-6 w-6" />
                  </button>
                  <button
                    onClick={nextImage}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-3 rounded-full hover:bg-opacity-70"
                  >
                    <ChevronRightIcon className="h-6 w-6" />
                  </button>
                  <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black bg-opacity-50 text-white px-3 py-2 rounded">
                    {selectedImageIndex + 1} / {images.length}
                  </div>
                </>
              )}
            </div>
          </div>
        )}

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
import axios from 'axios';
import { Property, CreatePropertyRequest, UpdatePropertyRequest } from '../types/property';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const propertyService = {
  // Get all properties for the current landlord
  async getProperties(): Promise<Property[]> {
    const response = await api.get('/properties');
    return response.data;
  },

  // Get properties formatted for lease creation (from leases database)
  async getPropertiesForLeases(): Promise<Property[]> {
    console.log('🏠 Fetching properties for lease creation...');
    const response = await api.get('/leases/properties');
    console.log('🏠 Properties for leases:', response.data);
    return response.data;
  },

  // Get a single property by ID
  async getProperty(id: string): Promise<Property> {
    const response = await api.get(`/properties/${id}`);
    return response.data;
  },

  // Create a new property
  async createProperty(property: CreatePropertyRequest): Promise<Property> {
    const response = await api.post('/properties', property);
    return response.data;
  },

  // Update an existing property
  async updateProperty(property: UpdatePropertyRequest): Promise<Property> {
    const response = await api.put(`/properties/${property.id}`, property);
    return response.data;
  },

  // Delete a property
  async deleteProperty(id: string): Promise<void> {
    await api.delete(`/properties/${id}`);
  },

  // Upload property images
  async uploadImages(propertyId: string, files: File[]): Promise<string[]> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('images', file);
    });

    const response = await api.post(`/properties/${propertyId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.imageUrls;
  },

  // Delete property image
  async deleteImage(propertyId: string, imageUrl: string): Promise<void> {
    await api.delete(`/properties/${propertyId}/images`, {
      data: { imageUrl },
    });
  },
};
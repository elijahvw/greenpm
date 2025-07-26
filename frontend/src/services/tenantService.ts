import axios from 'axios';
import { Tenant, CreateTenantRequest, UpdateTenantRequest } from '../types/tenant';

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

export const tenantService = {
  // Get all tenants for the current landlord
  async getTenants(): Promise<Tenant[]> {
    try {
      // Use the dedicated tenants endpoint
      const response = await api.get('/users/tenants');
      const tenants = response.data;
      
      // Transform tenants data to match expected interface
      return tenants.map((tenant: any) => ({
        id: tenant.id,
        firstName: tenant.firstName || tenant.first_name || '',
        lastName: tenant.lastName || tenant.last_name || '',
        email: tenant.email || '',
        phone: tenant.phone || '',
        dateOfBirth: tenant.dateOfBirth || '',
        socialSecurityNumber: tenant.socialSecurityNumber || '',
        emergencyContact: tenant.emergencyContact || {
          name: '',
          phone: '',
          relationship: ''
        },
        employment: tenant.employment || {
          employer: '',
          position: '',
          monthlyIncome: 0,
          employmentStartDate: ''
        },
        address: tenant.address || {
          street: '',
          city: '',
          state: '',
          zipCode: '',
          country: 'US'
        },
        status: tenant.status || 'active',
        moveInDate: tenant.moveInDate || '',
        moveOutDate: tenant.moveOutDate || '',
        notes: tenant.notes || '',
        documents: [],
        leaseHistory: [],
        paymentHistory: [],
        createdAt: tenant.created_at || tenant.createdAt || '',
        updatedAt: tenant.updated_at || tenant.updatedAt || '',
        isActive: tenant.status === 'active',
        // Current lease info - would need additional API call to get this
        currentProperty: '',
        currentRent: 0,
        leaseStartDate: '',
        leaseEndDate: ''
      }));
    } catch (error) {
      console.error('Error fetching tenants from leases:', error);
      return [];
    }
  },

  // Get a single tenant by ID
  async getTenant(id: string): Promise<Tenant> {
    const response = await api.get(`/users/tenants/${id}`);
    const tenant = response.data;
    
    // Transform tenant data to match expected interface
    return {
      id: tenant.id,
      firstName: tenant.firstName || tenant.first_name || '',
      lastName: tenant.lastName || tenant.last_name || '',
      email: tenant.email || '',
      phone: tenant.phone || '',
      dateOfBirth: tenant.dateOfBirth || '',
      socialSecurityNumber: tenant.socialSecurityNumber || '',
      emergencyContact: tenant.emergencyContact || {
        name: '',
        phone: '',
        relationship: ''
      },
      employment: tenant.employment || {
        employer: '',
        position: '',
        monthlyIncome: 0,
        employmentStartDate: ''
      },
      address: tenant.address || {
        street: '',
        city: '',
        state: '',
        zipCode: '',
        country: 'US'
      },
      status: tenant.status || 'active',
      moveInDate: tenant.moveInDate || '',
      moveOutDate: tenant.moveOutDate || '',
      notes: tenant.notes || '',
      documents: [],
      createdAt: tenant.created_at || tenant.createdAt || '',
      updatedAt: tenant.updated_at || tenant.updatedAt || '',
      isActive: tenant.status === 'active',
      // Current lease info - would need additional API call to get this
      currentProperty: '',
      currentRent: 0,
      leaseStartDate: '',
      leaseEndDate: '',
      leaseHistory: [],
      paymentHistory: []
    };
  },

  // Create a new tenant
  async createTenant(tenant: CreateTenantRequest): Promise<Tenant> {
    const response = await api.post('/users/tenants', tenant);
    return response.data;
  },

  // Update an existing tenant
  async updateTenant(tenant: UpdateTenantRequest): Promise<Tenant> {
    const response = await api.put(`/users/tenants/${tenant.id}`, tenant);
    return response.data;
  },

  // Delete a tenant
  async deleteTenant(id: string): Promise<void> {
    await api.delete(`/users/tenants/${id}`);
  },

  // Upload tenant documents
  async uploadDocuments(tenantId: string, files: File[]): Promise<string[]> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('documents', file);
    });

    const response = await api.post(`/tenants/${tenantId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.documentUrls;
  },

  // Delete tenant document
  async deleteDocument(tenantId: string, documentUrl: string): Promise<void> {
    await api.delete(`/tenants/${tenantId}/documents`, {
      data: { documentUrl },
    });
  },

  // Get tenants by property
  async getTenantsByProperty(propertyId: string): Promise<Tenant[]> {
    const response = await api.get(`/properties/${propertyId}/tenants`);
    return response.data;
  },
};
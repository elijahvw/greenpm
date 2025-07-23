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
  // Get all tenants for the current landlord (extracted from leases)
  async getTenants(): Promise<Tenant[]> {
    try {
      // Since there's no dedicated tenants endpoint, we'll extract tenant data from leases
      const response = await api.get('/leases');
      const leases = response.data;
      
      // Extract unique tenants from lease data
      const tenantMap = new Map();
      
      leases.forEach((lease: any) => {
        if (lease.tenant_id && lease.tenant_name) {
          tenantMap.set(lease.tenant_id, {
            id: lease.tenant_id,
            firstName: lease.tenant_name.split(' ')[0] || '',
            lastName: lease.tenant_name.split(' ').slice(1).join(' ') || '',
            email: lease.tenant_email || '',
            phone: lease.tenant_phone || '',
            // Additional fields with defaults
            dateOfBirth: '',
            emergencyContact: {
              name: '',
              phone: '',
              relationship: ''
            },
            employment: {
              employer: '',
              position: '',
              monthlyIncome: 0,
              employmentStartDate: ''
            },
            documents: [],
            leaseHistory: [],
            paymentHistory: [],
            createdAt: lease.created_at || '',
            updatedAt: lease.updated_at || '',
            isActive: lease.status === 'active',
            // Current lease info
            currentProperty: lease.property_name || '',
            currentRent: lease.rent_amount || 0,
            leaseStartDate: lease.start_date || '',
            leaseEndDate: lease.end_date || ''
          });
        }
      });
      
      return Array.from(tenantMap.values());
    } catch (error) {
      console.error('Error fetching tenants from leases:', error);
      return [];
    }
  },

  // Get a single tenant by ID
  async getTenant(id: string): Promise<Tenant> {
    const response = await api.get(`/tenants/${id}`);
    return response.data;
  },

  // Create a new tenant
  async createTenant(tenant: CreateTenantRequest): Promise<Tenant> {
    const response = await api.post('/tenants', tenant);
    return response.data;
  },

  // Update an existing tenant
  async updateTenant(tenant: UpdateTenantRequest): Promise<Tenant> {
    const response = await api.put(`/tenants/${tenant.id}`, tenant);
    return response.data;
  },

  // Delete a tenant
  async deleteTenant(id: string): Promise<void> {
    await api.delete(`/tenants/${id}`);
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
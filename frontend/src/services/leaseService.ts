import axios from 'axios';
import { Lease, CreateLeaseRequest, UpdateLeaseRequest, LeaseRenewal, LeaseTermination } from '../types/lease';

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

export const leaseService = {
  // Get all leases for the current landlord
  async getLeases(): Promise<Lease[]> {
    const response = await api.get('/leases');
    return response.data;
  },

  // Get a single lease by ID
  async getLease(id: string): Promise<Lease> {
    const response = await api.get(`/leases/${id}`);
    return response.data;
  },

  // Create a new lease
  async createLease(lease: CreateLeaseRequest): Promise<Lease> {
    const response = await api.post('/leases', lease);
    return response.data;
  },

  // Update an existing lease
  async updateLease(lease: UpdateLeaseRequest): Promise<Lease> {
    const response = await api.put(`/leases/${lease.id}`, lease);
    return response.data;
  },

  // Delete a lease
  async deleteLease(id: string): Promise<void> {
    await api.delete(`/leases/${id}`);
  },

  // Get leases by property
  async getLeasesByProperty(propertyId: string): Promise<Lease[]> {
    const response = await api.get(`/leases?propertyId=${propertyId}`);
    return response.data;
  },

  // Get leases by tenant
  async getLeasesByTenant(tenantId: string): Promise<Lease[]> {
    const response = await api.get(`/leases?tenantId=${tenantId}`);
    return response.data;
  },

  // Get active leases
  async getActiveLeases(): Promise<Lease[]> {
    const response = await api.get('/leases?status=active');
    return response.data;
  },

  // Get expiring leases (within specified days)
  async getExpiringLeases(days: number = 30): Promise<Lease[]> {
    const response = await api.get(`/leases/expiring?days=${days}`);
    return response.data;
  },

  // Terminate a lease
  async terminateLease(leaseId: string, termination: Omit<LeaseTermination, 'id' | 'leaseId' | 'createdAt'>): Promise<LeaseTermination> {
    const response = await api.post(`/leases/${leaseId}/terminate`, termination);
    return response.data;
  },

  // Renew a lease
  async renewLease(leaseId: string, renewal: Omit<LeaseRenewal, 'id' | 'originalLeaseId' | 'createdAt'>): Promise<LeaseRenewal> {
    const response = await api.post(`/leases/${leaseId}/renew`, renewal);
    return response.data;
  },

  // Upload lease documents
  async uploadDocuments(leaseId: string, files: File[]): Promise<string[]> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('documents', file);
    });

    const response = await api.post(`/leases/${leaseId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.documentUrls;
  },

  // Delete lease document
  async deleteDocument(leaseId: string, documentUrl: string): Promise<void> {
    await api.delete(`/leases/${leaseId}/documents`, {
      data: { documentUrl },
    });
  },

  // Generate lease document
  async generateLeaseDocument(leaseId: string): Promise<string> {
    const response = await api.post(`/leases/${leaseId}/generate-document`);
    return response.data.documentUrl;
  },

  // Sign lease
  async signLease(leaseId: string, signatureData: { signature: string; signedBy: string }): Promise<Lease> {
    const response = await api.post(`/leases/${leaseId}/sign`, signatureData);
    return response.data;
  },
};
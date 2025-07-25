import { api } from './api';
import { Lease, CreateLeaseRequest, UpdateLeaseRequest, LeaseRenewal, LeaseTermination } from '../types/lease';

export const leaseService = {
  // Get all leases for the current landlord
  async getLeases(): Promise<Lease[]> {
    const response = await api.get('/leases/');
    return response.data;
  },

  // Get a single lease by ID
  async getLease(id: string): Promise<Lease> {
    const response = await api.get(`/leases/${id}`);
    return response.data;
  },

  // Create a new lease
  async createLease(lease: CreateLeaseRequest): Promise<Lease> {
    // Transform frontend payload to match backend GCP database schema
    const backendPayload = {
      property_id: lease.propertyId,
      tenant_id: lease.tenantId,
      start_date: lease.startDate,
      end_date: lease.endDate,
      monthly_rent: lease.monthlyRent,
      security_deposit: lease.securityDeposit || 0,
      late_fee_amount: lease.lateFeePenalty || 0,
      late_fee_grace_period: lease.gracePeriodDays || 5,
      lease_terms: {
        pet_policy: lease.petPolicy?.restrictions || null,
        smoking_allowed: false, // Default value
        subletting_allowed: false, // Default value
        maintenance_responsibility: lease.landlordResponsibilities?.join(', ') || null,
        utilities_included: lease.utilitiesIncluded || [],
        parking_included: false, // Default value
        additional_terms: [
          lease.specialTerms,
          lease.notes,
          `Lease Type: ${lease.leaseType}`,
          `Renewal Option: ${lease.renewalOption ? 'Yes' : 'No'}`,
          lease.petPolicy?.allowed ? `Pet Policy: Allowed (Deposit: $${lease.petPolicy.deposit}, Monthly: $${lease.petPolicy.monthlyFee})` : 'Pet Policy: Not Allowed',
          `Tenant Responsibilities: ${lease.tenantResponsibilities?.join(', ') || 'None specified'}`
        ].filter(Boolean).join('\n\n')
      }
    };

    console.log('🔄 Original lease data:', lease);
    console.log('🔄 Transformed lease payload for GCP DB:', backendPayload);
    
    // Debug API call details
    console.log('🔍 Making API call to /leases...');
    console.log('🔍 API base URL:', api.defaults.baseURL);
    console.log('🔍 Authorization header:', api.defaults.headers.common['Authorization']);
    
    try {
      const response = await api.post('/leases', backendPayload);
      console.log('✅ Lease creation successful:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('❌ Lease creation failed:', error);
      console.error('❌ Error status:', error.response?.status);
      console.error('❌ Error data:', error.response?.data);
      console.error('❌ Error headers:', error.response?.headers);
      throw error;
    }
  },

  // Update an existing lease
  async updateLease(lease: UpdateLeaseRequest): Promise<Lease> {
    console.log('🔄 Updating lease:', lease);
    
    try {
      const response = await api.put(`/leases/${lease.id}`, lease);
      console.log('✅ Lease update successful:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('❌ Lease update failed:', error);
      console.error('❌ Error status:', error.response?.status);
      console.error('❌ Error data:', error.response?.data);
      throw error;
    }
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
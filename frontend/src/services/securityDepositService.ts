import axios from 'axios';
import { 
  SecurityDeposit, 
  CreateSecurityDepositRequest, 
  UpdateSecurityDepositRequest,
  AddDeductionRequest,
  ProcessRefundRequest,
  SecurityDepositSummary
} from '../types/securityDeposit';

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

export const securityDepositService = {
  // Get all security deposits
  async getSecurityDeposits(): Promise<SecurityDeposit[]> {
    const response = await api.get('/security-deposits');
    return response.data;
  },

  // Get a single security deposit by ID
  async getSecurityDeposit(id: string): Promise<SecurityDeposit> {
    const response = await api.get(`/security-deposits/${id}`);
    return response.data;
  },

  // Get security deposit for a specific lease
  async getLeaseSecurityDeposit(leaseId: string): Promise<SecurityDeposit> {
    const response = await api.get(`/leases/${leaseId}/security-deposit`);
    return response.data;
  },

  // Create a new security deposit
  async createSecurityDeposit(deposit: CreateSecurityDepositRequest): Promise<SecurityDeposit> {
    const response = await api.post('/security-deposits', deposit);
    return response.data;
  },

  // Update an existing security deposit
  async updateSecurityDeposit(deposit: UpdateSecurityDepositRequest): Promise<SecurityDeposit> {
    const response = await api.put(`/security-deposits/${deposit.id}`, deposit);
    return response.data;
  },

  // Add a deduction to a security deposit
  async addDeduction(depositId: string, deduction: AddDeductionRequest): Promise<SecurityDeposit> {
    const response = await api.post(`/security-deposits/${depositId}/deductions`, deduction);
    return response.data;
  },

  // Process a refund
  async processRefund(depositId: string, refund: ProcessRefundRequest): Promise<SecurityDeposit> {
    const response = await api.post(`/security-deposits/${depositId}/refund`, refund);
    return response.data;
  },

  // Get security deposits by status
  async getSecurityDepositsByStatus(status: 'unpaid' | 'held' | 'partial_refunded' | 'refunded'): Promise<SecurityDeposit[]> {
    const response = await api.get(`/security-deposits?status=${status}`);
    return response.data;
  },

  // Get security deposits for a specific tenant
  async getTenantSecurityDeposits(tenantId: string): Promise<SecurityDeposit[]> {
    const response = await api.get(`/security-deposits?tenantId=${tenantId}`);
    return response.data;
  },

  // Get security deposits for a specific property
  async getPropertySecurityDeposits(propertyId: string): Promise<SecurityDeposit[]> {
    const response = await api.get(`/security-deposits?propertyId=${propertyId}`);
    return response.data;
  },

  // Calculate interest for a security deposit
  async calculateInterest(depositId: string): Promise<{ interestAccrued: number; calculatedDate: string }> {
    const response = await api.post(`/security-deposits/${depositId}/calculate-interest`);
    return response.data;
  },

  // Generate security deposit summary/report
  async getSecurityDepositSummary(): Promise<SecurityDepositSummary> {
    const response = await api.get('/security-deposits/summary');
    return response.data;
  },

  // Delete a security deposit (admin only)
  async deleteSecurityDeposit(id: string): Promise<void> {
    await api.delete(`/security-deposits/${id}`);
  },
};
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000, // Increased to 30 seconds for safety
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      console.warn('🚨 API: 401 Unauthorized - Token may be expired');
      localStorage.removeItem('token');
      
      // Only redirect if we're not already on login page
      if (!window.location.pathname.includes('/login')) {
        // Give user a moment to see any error messages before redirecting
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      }
    }
    return Promise.reject(error);
  }
);

// API service classes
export class AuthService {
  static async login(email: string, password: string) {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  }

  static async register(userData: any) {
    const response = await api.post('/auth/register', userData);
    return response.data;
  }

  static async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  }

  static async refreshToken() {
    const response = await api.post('/auth/refresh');
    return response.data;
  }
}

export class PropertyService {
  static async getProperties(params: any = {}) {
    console.log('🏠 Fetching properties from:', `${API_BASE_URL}/api/v1/properties`);
    const response = await api.get('/properties', { params });
    console.log('🏠 Properties response:', response.data);
    return response.data;
  }

  static async getProperty(id: string) {
    const response = await api.get(`/properties/${id}`);
    return response.data;
  }

  static async createProperty(data: any) {
    const response = await api.post('/properties', data);
    return response.data;
  }

  static async updateProperty(id: string, data: any) {
    const response = await api.put(`/properties/${id}`, data);
    return response.data;
  }

  static async deleteProperty(id: string) {
    const response = await api.delete(`/properties/${id}`);
    return response.data;
  }

  static async uploadPropertyImages(id: string, files: FileList) {
    const formData = new FormData();
    Array.from(files).forEach((file) => {
      formData.append('files', file);
    });

    const response = await api.post(`/properties/${id}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
}

export class ApplicationService {
  static async getApplications(params: any = {}) {
    const response = await api.get('/applications', { params });
    return response.data;
  }

  static async getApplication(id: string) {
    const response = await api.get(`/applications/${id}`);
    return response.data;
  }

  static async createApplication(data: any) {
    const response = await api.post('/applications', data);
    return response.data;
  }

  static async updateApplication(id: string, data: any) {
    const response = await api.put(`/applications/${id}`, data);
    return response.data;
  }

  static async approveApplication(id: string) {
    const response = await api.post(`/applications/${id}/approve`);
    return response.data;
  }

  static async rejectApplication(id: string, reason: string) {
    const response = await api.post(`/applications/${id}/reject`, { reason });
    return response.data;
  }
}

export class LeaseService {
  static async getLeases(params: any = {}) {
    const response = await api.get('/leases', { params });
    return response.data;
  }

  static async getLease(id: string) {
    const response = await api.get(`/leases/${id}`);
    return response.data;
  }

  static async createLease(data: any) {
    const response = await api.post('/leases', data);
    return response.data;
  }

  static async updateLease(id: string, data: any) {
    const response = await api.put(`/leases/${id}`, data);
    return response.data;
  }

  static async signLease(id: string, signatureData: any) {
    const response = await api.post(`/leases/${id}/sign`, signatureData);
    return response.data;
  }

  static async terminateLease(id: string, terminationData: any) {
    const response = await api.post(`/leases/${id}/terminate`, terminationData);
    return response.data;
  }
}

export class MaintenanceService {
  static async getMaintenanceRequests(params: any = {}) {
    const response = await api.get('/maintenance/requests', { params });
    return response.data;
  }

  static async getMaintenanceRequest(id: string) {
    const response = await api.get(`/maintenance/requests/${id}`);
    return response.data;
  }

  static async createMaintenanceRequest(data: any) {
    const response = await api.post('/maintenance/requests', data);
    return response.data;
  }

  static async updateMaintenanceRequest(id: string, data: any) {
    const response = await api.put(`/maintenance/requests/${id}`, data);
    return response.data;
  }

  static async uploadMaintenanceImages(id: string, files: FileList) {
    const formData = new FormData();
    Array.from(files).forEach((file) => {
      formData.append('files', file);
    });

    const response = await api.post(`/maintenance/requests/${id}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  static async closeMaintenanceRequest(id: string, resolution: string) {
    const response = await api.post(`/maintenance/requests/${id}/close`, { resolution_notes: resolution });
    return response.data;
  }
}

export class PaymentService {
  static async getPayments(params: any = {}) {
    const response = await api.get('/payments', { params });
    return response.data;
  }

  static async getPayment(id: string) {
    const response = await api.get(`/payments/${id}`);
    return response.data;
  }

  static async createPayment(data: any) {
    const response = await api.post('/payments', data);
    return response.data;
  }

  static async getPaymentSchedule(leaseId: string) {
    const response = await api.get(`/payments/schedule/${leaseId}`);
    return response.data;
  }

  static async getPaymentSummary() {
    const response = await api.get('/payments/summary');
    return response.data;
  }
}

export class MessageService {
  static async getThreads(params: any = {}) {
    const response = await api.get('/messages/threads', { params });
    return response.data;
  }

  static async getThread(id: string) {
    const response = await api.get(`/messages/threads/${id}`);
    return response.data;
  }

  static async getMessages(threadId: string, params: any = {}) {
    const response = await api.get('/messages', { params: { thread_id: threadId, ...params } });
    return response.data;
  }

  static async sendMessage(data: any) {
    const response = await api.post('/messages', data);
    return response.data;
  }

  static async sendQuickMessage(recipientId: string, subject: string, content: string) {
    const response = await api.post('/messages/quick-message', {
      recipient_id: recipientId,
      subject,
      content,
    });
    return response.data;
  }

  static async markThreadRead(threadId: string) {
    const response = await api.post(`/messages/threads/${threadId}/mark-read`);
    return response.data;
  }

  static async getUnreadCount() {
    const response = await api.get('/messages/unread-count');
    return response.data;
  }
}

export class DashboardService {
  static async getDashboardStats() {
    console.log('🔍 Fetching dashboard stats from:', `${API_BASE_URL}/api/v1/dashboard/stats`);
    const response = await api.get('/dashboard/stats');
    console.log('📊 Dashboard stats response:', response.data);
    return response.data;
  }

  static async getRecentActivity() {
    console.log('🔍 Fetching recent activity from:', `${API_BASE_URL}/api/v1/dashboard/activity`);
    const response = await api.get('/dashboard/activity');
    console.log('📈 Recent activity response:', response.data);
    return response.data;
  }
}

export class AdminService {
  static async getAdminDashboard() {
    const response = await api.get('/admin/dashboard');
    return response.data;
  }

  static async getUsers(params: any = {}) {
    const response = await api.get('/admin/users', { params });
    return response.data;
  }

  static async updateUser(id: string, data: any) {
    const response = await api.put(`/admin/users/${id}`, data);
    return response.data;
  }

  static async deleteUser(id: string) {
    const response = await api.delete(`/admin/users/${id}`);
    return response.data;
  }

  static async getActivityLog(params: any = {}) {
    const response = await api.get('/admin/activity-log', { params });
    return response.data;
  }

  static async getSystemHealth() {
    const response = await api.get('/admin/system-health');
    return response.data;
  }
}
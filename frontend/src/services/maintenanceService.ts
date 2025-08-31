import { api } from './api';

export interface MaintenanceRequest {
  id: string;
  property_id: string;
  tenant_id: string;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'open' | 'in_progress' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
  property_name?: string;
  property_address?: string;
  tenant_name?: string;
  tenant_email?: string;
  tenant_phone?: string;
  landlord_name?: string;
  landlord_email?: string;
}

export interface CreateMaintenanceRequest {
  property_id: string;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

export interface UpdateMaintenanceRequest {
  title?: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  status?: 'open' | 'in_progress' | 'completed' | 'cancelled';
}

export interface MaintenanceStats {
  total_requests: number;
  open_requests: number;
  in_progress_requests: number;
  completed_requests: number;
  high_priority: number;
  urgent_priority: number;
}

export interface MaintenanceHistory {
  request_id: string;
  history: Array<{
    id: string;
    action: string;
    old_value?: string;
    new_value?: string;
    notes: string;
    created_at: string;
    user_name: string;
    role: string;
  }>;
}

export const maintenanceService = {
  // Get all maintenance requests
  async getMaintenanceRequests(filters?: {
    status?: string;
    priority?: string;
    property_id?: string;
  }): Promise<MaintenanceRequest[]> {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.priority) params.append('priority', filters.priority);
    if (filters?.property_id) params.append('property_id', filters.property_id);

    const response = await api.get(`/maintenance/?${params.toString()}`);
    return response.data;
  },

  // Get a single maintenance request
  async getMaintenanceRequest(id: string): Promise<MaintenanceRequest> {
    const response = await api.get(`/maintenance/${id}`);
    return response.data;
  },

  // Create a new maintenance request
  async createMaintenanceRequest(data: CreateMaintenanceRequest): Promise<MaintenanceRequest> {
    const response = await api.post('/maintenance/', data);
    return response.data;
  },

  // Update a maintenance request
  async updateMaintenanceRequest(id: string, data: UpdateMaintenanceRequest): Promise<MaintenanceRequest> {
    const response = await api.put(`/maintenance/${id}`, data);
    return response.data;
  },

  // Delete a maintenance request
  async deleteMaintenanceRequest(id: string): Promise<void> {
    await api.delete(`/maintenance/${id}`);
  },

  // Update maintenance status with notes
  async updateMaintenanceStatus(
    id: string, 
    status: 'open' | 'in_progress' | 'completed' | 'cancelled',
    notes?: string
  ): Promise<{
    message: string;
    request_id: string;
    old_status: string;
    new_status: string;
    notification_sent: boolean;
  }> {
    const response = await api.post(`/maintenance/${id}/status`, null, {
      params: { status, notes }
    });
    return response.data;
  },

  // Get maintenance request history
  async getMaintenanceHistory(id: string): Promise<MaintenanceHistory> {
    const response = await api.get(`/maintenance/${id}/history`);
    return response.data;
  },

  // Add comment to maintenance request
  async addMaintenanceComment(id: string, comment: string): Promise<{
    message: string;
    comment_id: string;
  }> {
    const response = await api.post(`/maintenance/${id}/comments`, null, {
      params: { comment }
    });
    return response.data;
  },

  // Get maintenance statistics
  async getMaintenanceStats(): Promise<MaintenanceStats> {
    const response = await api.get('/maintenance/stats/overview');
    return response.data;
  },

  // Helper functions for UI
  getPriorityColor(priority: string): string {
    const colors = {
      low: 'text-green-600 bg-green-100',
      medium: 'text-yellow-600 bg-yellow-100',
      high: 'text-orange-600 bg-orange-100',
      urgent: 'text-red-600 bg-red-100'
    };
    return colors[priority as keyof typeof colors] || 'text-gray-600 bg-gray-100';
  },

  getStatusColor(status: string): string {
    const colors = {
      open: 'text-blue-600 bg-blue-100',
      in_progress: 'text-yellow-600 bg-yellow-100',
      completed: 'text-green-600 bg-green-100',
      cancelled: 'text-red-600 bg-red-100'
    };
    return colors[status as keyof typeof colors] || 'text-gray-600 bg-gray-100';
  },

  getPriorityIcon(priority: string): string {
    const icons = {
      low: '⚪',
      medium: '🟡',
      high: '🟠',
      urgent: '🔴'
    };
    return icons[priority as keyof typeof icons] || '⚪';
  },

  getStatusIcon(status: string): string {
    const icons = {
      open: '📋',
      in_progress: '🔧',
      completed: '✅',
      cancelled: '❌'
    };
    return icons[status as keyof typeof icons] || '📋';
  }
};
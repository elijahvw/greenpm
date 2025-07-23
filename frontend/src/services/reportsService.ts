import axios from 'axios';
import { 
  Report, 
  ReportTemplate, 
  CreateReportRequest, 
  AnalyticsDashboard,
  FinancialReport,
  OccupancyReport,
  MaintenanceReport,
  TenantReport,
  PropertyReport
} from '../types/reports';

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

export const reportsService = {
  // Reports
  async getReports(): Promise<Report[]> {
    const response = await api.get('/reports');
    return response.data;
  },

  async getReport(id: string): Promise<Report> {
    const response = await api.get(`/reports/${id}`);
    return response.data;
  },

  async createReport(report: CreateReportRequest): Promise<Report> {
    const response = await api.post('/reports', report);
    return response.data;
  },

  async deleteReport(id: string): Promise<void> {
    await api.delete(`/reports/${id}`);
  },

  async downloadReport(id: string): Promise<Blob> {
    const response = await api.get(`/reports/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Specific Report Types
  async generateFinancialReport(
    startDate: string, 
    endDate: string, 
    propertyIds?: string[]
  ): Promise<FinancialReport> {
    const response = await api.post('/reports/financial', {
      startDate,
      endDate,
      propertyIds,
    });
    return response.data;
  },

  async generateOccupancyReport(
    startDate: string, 
    endDate: string, 
    propertyIds?: string[]
  ): Promise<OccupancyReport> {
    const response = await api.post('/reports/occupancy', {
      startDate,
      endDate,
      propertyIds,
    });
    return response.data;
  },

  async generateMaintenanceReport(
    startDate: string, 
    endDate: string, 
    propertyIds?: string[]
  ): Promise<MaintenanceReport> {
    const response = await api.post('/reports/maintenance', {
      startDate,
      endDate,
      propertyIds,
    });
    return response.data;
  },

  async generateTenantReport(
    startDate: string, 
    endDate: string, 
    propertyIds?: string[]
  ): Promise<TenantReport> {
    const response = await api.post('/reports/tenant', {
      startDate,
      endDate,
      propertyIds,
    });
    return response.data;
  },

  async generatePropertyReport(
    startDate: string, 
    endDate: string, 
    propertyIds?: string[]
  ): Promise<PropertyReport> {
    const response = await api.post('/reports/property', {
      startDate,
      endDate,
      propertyIds,
    });
    return response.data;
  },

  // Report Templates
  async getReportTemplates(): Promise<ReportTemplate[]> {
    const response = await api.get('/report-templates');
    return response.data;
  },

  async getReportTemplate(id: string): Promise<ReportTemplate> {
    const response = await api.get(`/report-templates/${id}`);
    return response.data;
  },

  async createReportTemplate(template: Omit<ReportTemplate, 'id' | 'createdAt' | 'createdBy'>): Promise<ReportTemplate> {
    const response = await api.post('/report-templates', template);
    return response.data;
  },

  async updateReportTemplate(id: string, template: Partial<ReportTemplate>): Promise<ReportTemplate> {
    const response = await api.put(`/report-templates/${id}`, template);
    return response.data;
  },

  async deleteReportTemplate(id: string): Promise<void> {
    await api.delete(`/report-templates/${id}`);
  },

  // Analytics Dashboard
  async getAnalyticsDashboard(startDate?: string, endDate?: string): Promise<AnalyticsDashboard> {
    const params = new URLSearchParams();
    if (startDate) params.append('startDate', startDate);
    if (endDate) params.append('endDate', endDate);
    
    const response = await api.get(`/analytics/dashboard?${params.toString()}`);
    return response.data;
  },

  // Export functions
  async exportReportData(
    reportType: string,
    startDate: string,
    endDate: string,
    format: 'csv' | 'excel' | 'pdf',
    propertyIds?: string[]
  ): Promise<Blob> {
    const response = await api.post(`/reports/export`, {
      reportType,
      startDate,
      endDate,
      format,
      propertyIds,
    }, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Scheduled Reports
  async getScheduledReports(): Promise<any[]> {
    const response = await api.get('/scheduled-reports');
    return response.data;
  },

  async createScheduledReport(schedule: {
    reportType: string;
    frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly';
    recipients: string[];
    filters?: any;
  }): Promise<any> {
    const response = await api.post('/scheduled-reports', schedule);
    return response.data;
  },

  async deleteScheduledReport(id: string): Promise<void> {
    await api.delete(`/scheduled-reports/${id}`);
  },
};
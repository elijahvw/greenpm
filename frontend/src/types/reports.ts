export interface Report {
  id: string;
  title: string;
  type: 'financial' | 'occupancy' | 'maintenance' | 'tenant' | 'property' | 'custom';
  description: string;
  period: {
    startDate: string;
    endDate: string;
  };
  filters: {
    propertyIds?: string[];
    tenantIds?: string[];
    categories?: string[];
    status?: string[];
  };
  data: any;
  generatedAt: string;
  generatedBy: string;
  format: 'pdf' | 'csv' | 'excel' | 'json';
  downloadUrl?: string;
  landlordId: string;
}

export interface FinancialReport extends Report {
  type: 'financial';
  data: {
    totalIncome: number;
    totalExpenses: number;
    netIncome: number;
    profitMargin: number;
    incomeBreakdown: {
      category: string;
      amount: number;
      percentage: number;
    }[];
    expenseBreakdown: {
      category: string;
      amount: number;
      percentage: number;
    }[];
    monthlyTrends: {
      month: string;
      income: number;
      expenses: number;
      netIncome: number;
    }[];
    propertyPerformance: {
      propertyId: string;
      propertyName: string;
      income: number;
      expenses: number;
      netIncome: number;
      roi: number;
    }[];
  };
}

export interface OccupancyReport extends Report {
  type: 'occupancy';
  data: {
    totalUnits: number;
    occupiedUnits: number;
    vacantUnits: number;
    occupancyRate: number;
    averageVacancyDays: number;
    turnoverRate: number;
    propertyOccupancy: {
      propertyId: string;
      propertyName: string;
      totalUnits: number;
      occupiedUnits: number;
      occupancyRate: number;
      averageRent: number;
    }[];
    vacancyTrends: {
      month: string;
      occupancyRate: number;
      vacantUnits: number;
    }[];
  };
}

export interface MaintenanceReport extends Report {
  type: 'maintenance';
  data: {
    totalRequests: number;
    completedRequests: number;
    pendingRequests: number;
    averageResolutionTime: number;
    totalCost: number;
    categoryBreakdown: {
      category: string;
      count: number;
      totalCost: number;
      averageTime: number;
    }[];
    propertyMaintenance: {
      propertyId: string;
      propertyName: string;
      requestCount: number;
      totalCost: number;
      averageTime: number;
    }[];
    monthlyTrends: {
      month: string;
      requestCount: number;
      totalCost: number;
      averageTime: number;
    }[];
  };
}

export interface TenantReport extends Report {
  type: 'tenant';
  data: {
    totalTenants: number;
    activeTenants: number;
    newTenants: number;
    leavingTenants: number;
    averageLeaseLength: number;
    rentCollectionRate: number;
    latePaymentRate: number;
    tenantSatisfaction: number;
    tenantTurnover: {
      month: string;
      newTenants: number;
      leavingTenants: number;
      turnoverRate: number;
    }[];
    paymentHistory: {
      tenantId: string;
      tenantName: string;
      onTimePayments: number;
      latePayments: number;
      totalPayments: number;
      paymentRate: number;
    }[];
  };
}

export interface PropertyReport extends Report {
  type: 'property';
  data: {
    totalProperties: number;
    totalUnits: number;
    averageRent: number;
    totalValue: number;
    averageROI: number;
    propertyPerformance: {
      propertyId: string;
      propertyName: string;
      units: number;
      occupancyRate: number;
      averageRent: number;
      totalIncome: number;
      totalExpenses: number;
      netIncome: number;
      roi: number;
      maintenanceCost: number;
    }[];
    rentTrends: {
      month: string;
      averageRent: number;
      occupancyRate: number;
    }[];
  };
}

export interface ReportTemplate {
  id: string;
  name: string;
  type: Report['type'];
  description: string;
  defaultFilters: Report['filters'];
  defaultPeriod: 'last_month' | 'last_quarter' | 'last_year' | 'ytd' | 'custom';
  isCustom: boolean;
  createdBy: string;
  createdAt: string;
}

export interface CreateReportRequest {
  title: string;
  type: Report['type'];
  description?: string;
  period: {
    startDate: string;
    endDate: string;
  };
  filters?: Report['filters'];
  format: 'pdf' | 'csv' | 'excel' | 'json';
  templateId?: string;
}

export interface AnalyticsDashboard {
  overview: {
    totalIncome: number;
    totalExpenses: number;
    netIncome: number;
    occupancyRate: number;
    totalProperties: number;
    totalTenants: number;
    maintenanceRequests: number;
    rentCollectionRate: number;
  };
  trends: {
    income: { month: string; amount: number }[];
    expenses: { month: string; amount: number }[];
    occupancy: { month: string; rate: number }[];
    maintenance: { month: string; count: number }[];
  };
  topPerformingProperties: {
    propertyId: string;
    propertyName: string;
    netIncome: number;
    roi: number;
    occupancyRate: number;
  }[];
  alerts: {
    type: 'low_occupancy' | 'high_maintenance' | 'overdue_rent' | 'lease_expiring';
    message: string;
    severity: 'low' | 'medium' | 'high';
    propertyId?: string;
    tenantId?: string;
    count?: number;
  }[];
}
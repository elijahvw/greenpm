import axios from 'axios';
import { 
  Transaction, 
  RentPayment, 
  Expense, 
  FinancialReport, 
  FinancialSummary,
  CreateTransactionRequest,
  CreateExpenseRequest,
  UpdateRentPaymentRequest
} from '../types/financial';

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

export const financialService = {
  // Transactions
  async getTransactions(): Promise<Transaction[]> {
    const response = await api.get('/transactions');
    return response.data;
  },

  async getTransaction(id: string): Promise<Transaction> {
    const response = await api.get(`/transactions/${id}`);
    return response.data;
  },

  async createTransaction(transaction: CreateTransactionRequest): Promise<Transaction> {
    const response = await api.post('/transactions', transaction);
    return response.data;
  },

  async updateTransaction(id: string, transaction: Partial<CreateTransactionRequest>): Promise<Transaction> {
    const response = await api.put(`/transactions/${id}`, transaction);
    return response.data;
  },

  async deleteTransaction(id: string): Promise<void> {
    await api.delete(`/transactions/${id}`);
  },

  // Rent Payments
  async getRentPayments(): Promise<RentPayment[]> {
    const response = await api.get('/rent-payments');
    return response.data;
  },

  async getRentPayment(id: string): Promise<RentPayment> {
    const response = await api.get(`/rent-payments/${id}`);
    return response.data;
  },

  async updateRentPayment(payment: UpdateRentPaymentRequest): Promise<RentPayment> {
    const response = await api.put(`/rent-payments/${payment.id}`, payment);
    return response.data;
  },

  async getOverduePayments(): Promise<RentPayment[]> {
    const response = await api.get('/rent-payments?status=overdue');
    return response.data;
  },

  async getPendingPayments(): Promise<RentPayment[]> {
    const response = await api.get('/rent-payments?status=pending');
    return response.data;
  },

  async getRentPaymentsByProperty(propertyId: string): Promise<RentPayment[]> {
    const response = await api.get(`/rent-payments?propertyId=${propertyId}`);
    return response.data;
  },

  async getRentPaymentsByTenant(tenantId: string): Promise<RentPayment[]> {
    const response = await api.get(`/rent-payments?tenantId=${tenantId}`);
    return response.data;
  },

  // Expenses
  async getExpenses(): Promise<Expense[]> {
    const response = await api.get('/expenses');
    return response.data;
  },

  async getExpense(id: string): Promise<Expense> {
    const response = await api.get(`/expenses/${id}`);
    return response.data;
  },

  async createExpense(expense: CreateExpenseRequest): Promise<Expense> {
    const response = await api.post('/expenses', expense);
    return response.data;
  },

  async updateExpense(id: string, expense: Partial<CreateExpenseRequest>): Promise<Expense> {
    const response = await api.put(`/expenses/${id}`, expense);
    return response.data;
  },

  async deleteExpense(id: string): Promise<void> {
    await api.delete(`/expenses/${id}`);
  },

  async getExpensesByProperty(propertyId: string): Promise<Expense[]> {
    const response = await api.get(`/expenses?propertyId=${propertyId}`);
    return response.data;
  },

  async getExpensesByCategory(category: string): Promise<Expense[]> {
    const response = await api.get(`/expenses?category=${category}`);
    return response.data;
  },

  // Upload receipt
  async uploadReceipt(expenseId: string, file: File): Promise<string> {
    const formData = new FormData();
    formData.append('receipt', file);

    const response = await api.post(`/expenses/${expenseId}/receipt`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.receiptUrl;
  },

  // Financial Reports
  async getFinancialReports(): Promise<FinancialReport[]> {
    const response = await api.get('/financial-reports');
    return response.data;
  },

  async generateFinancialReport(
    type: string, 
    startDate: string, 
    endDate: string, 
    propertyIds?: string[]
  ): Promise<FinancialReport> {
    const response = await api.post('/financial-reports/generate', {
      type,
      startDate,
      endDate,
      propertyIds,
    });
    return response.data;
  },

  async getFinancialSummary(startDate?: string, endDate?: string): Promise<FinancialSummary> {
    const params = new URLSearchParams();
    if (startDate) params.append('startDate', startDate);
    if (endDate) params.append('endDate', endDate);
    
    const response = await api.get(`/financial-summary?${params.toString()}`);
    return response.data;
  },

  // Dashboard metrics
  async getDashboardMetrics(): Promise<{
    totalIncome: number;
    totalExpenses: number;
    netIncome: number;
    pendingRent: number;
    overdueRent: number;
    occupancyRate: number;
    rentCollectionRate: number;
  }> {
    const response = await api.get('/financial-metrics');
    return response.data;
  },

  // Export data
  async exportTransactions(startDate: string, endDate: string, format: 'csv' | 'pdf'): Promise<Blob> {
    const response = await api.get(`/transactions/export`, {
      params: { startDate, endDate, format },
      responseType: 'blob',
    });
    return response.data;
  },

  async exportExpenses(startDate: string, endDate: string, format: 'csv' | 'pdf'): Promise<Blob> {
    const response = await api.get(`/expenses/export`, {
      params: { startDate, endDate, format },
      responseType: 'blob',
    });
    return response.data;
  },
};
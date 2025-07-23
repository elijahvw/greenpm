export interface Transaction {
  id: string;
  type: 'income' | 'expense';
  category: string;
  amount: number;
  description: string;
  date: string;
  propertyId?: string;
  tenantId?: string;
  leaseId?: string;
  paymentMethod: 'cash' | 'check' | 'bank_transfer' | 'credit_card' | 'online';
  status: 'pending' | 'completed' | 'failed' | 'cancelled';
  reference: string;
  attachments: string[];
  createdAt: string;
  updatedAt: string;
  landlordId: string;
  
  // Related data (populated when needed)
  property?: {
    id: string;
    name: string;
    address: string;
  };
  tenant?: {
    id: string;
    firstName: string;
    lastName: string;
    email: string;
  };
}

export interface RentPayment {
  id: string;
  leaseId: string;
  tenantId: string;
  propertyId: string;
  amount: number;
  dueDate: string;
  paidDate?: string;
  paymentMethod?: 'cash' | 'check' | 'bank_transfer' | 'credit_card' | 'online';
  status: 'pending' | 'paid' | 'overdue' | 'partial';
  lateFee: number;
  notes: string;
  transactionId?: string;
  createdAt: string;
  updatedAt: string;
  
  // Related data
  lease?: {
    id: string;
    monthlyRent: number;
    startDate: string;
    endDate: string;
  };
  tenant?: {
    id: string;
    firstName: string;
    lastName: string;
    email: string;
    phone: string;
  };
  property?: {
    id: string;
    name: string;
    address: string;
  };
}

export interface Expense {
  id: string;
  propertyId?: string;
  category: string;
  subcategory: string;
  amount: number;
  description: string;
  date: string;
  vendor: string;
  paymentMethod: 'cash' | 'check' | 'bank_transfer' | 'credit_card';
  receiptUrl?: string;
  taxDeductible: boolean;
  recurring: boolean;
  recurringFrequency?: 'monthly' | 'quarterly' | 'yearly';
  status: 'pending' | 'paid' | 'approved' | 'rejected';
  approvedBy?: string;
  notes: string;
  createdAt: string;
  updatedAt: string;
  landlordId: string;
  
  // Related data
  property?: {
    id: string;
    name: string;
    address: string;
  };
}

export interface FinancialReport {
  id: string;
  type: 'income_statement' | 'cash_flow' | 'rent_roll' | 'expense_report' | 'tax_summary';
  title: string;
  period: {
    startDate: string;
    endDate: string;
  };
  propertyIds: string[];
  data: {
    totalIncome: number;
    totalExpenses: number;
    netIncome: number;
    occupancyRate: number;
    rentCollectionRate: number;
    breakdown: {
      category: string;
      amount: number;
      percentage: number;
    }[];
  };
  generatedAt: string;
  landlordId: string;
}

export interface CreateTransactionRequest {
  type: 'income' | 'expense';
  category: string;
  amount: number;
  description: string;
  date: string;
  propertyId?: string;
  tenantId?: string;
  leaseId?: string;
  paymentMethod: 'cash' | 'check' | 'bank_transfer' | 'credit_card' | 'online';
  reference?: string;
}

export interface CreateExpenseRequest {
  propertyId?: string;
  category: string;
  subcategory: string;
  amount: number;
  description: string;
  date: string;
  vendor: string;
  paymentMethod: 'cash' | 'check' | 'bank_transfer' | 'credit_card';
  taxDeductible: boolean;
  recurring: boolean;
  recurringFrequency?: 'monthly' | 'quarterly' | 'yearly';
  notes?: string;
}

export interface UpdateRentPaymentRequest {
  id: string;
  amount?: number;
  paidDate?: string;
  paymentMethod?: 'cash' | 'check' | 'bank_transfer' | 'credit_card' | 'online';
  status?: 'pending' | 'paid' | 'overdue' | 'partial';
  lateFee?: number;
  notes?: string;
}

export interface FinancialSummary {
  totalIncome: number;
  totalExpenses: number;
  netIncome: number;
  monthlyIncome: number;
  monthlyExpenses: number;
  monthlyNetIncome: number;
  outstandingRent: number;
  overduePayments: number;
  pendingRent?: number;
  overdueRent?: number;
  occupancyRate?: number;
  rentCollectionRate?: number;
  incomeByCategory: Record<string, number>;
  expensesByCategory: Record<string, number>;
  incomeGrowth: number;
  expenseGrowth: number;
  monthlyBreakdown?: {
    month: string;
    income: number;
    expenses: number;
    netIncome: number;
  }[];
  expenseCategories?: {
    category: string;
    amount: number;
    percentage: number;
  }[];
}
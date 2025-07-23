export interface SecurityDepositDeduction {
  id: string;
  date: string;
  amount: number;
  description: string;
  category: 'damage' | 'cleaning' | 'unpaid_rent' | 'late_fees' | 'other';
  receipt?: string;
  notes?: string;
}

export interface StateRequirements {
  interestRequired: boolean;
  maxHoldDays: number;
  inspectionRequired: boolean;
  maxInterestRate?: number;
  depositAccountRequired?: boolean;
}

export interface SecurityDeposit {
  id: string;
  leaseId: string;
  tenantId: string;
  propertyId: string;
  
  // Deposit Details
  amount: number;
  dateReceived: string;
  bankAccount: string;
  paymentMethod: 'cash' | 'check' | 'bank_transfer' | 'cashiers_check' | 'money_order';
  referenceNumber: string;
  
  // Interest Tracking
  interestRate?: number;
  interestAccrued?: number;
  interestCalculatedDate?: string;
  
  // Status Tracking
  status: 'unpaid' | 'held' | 'partial_refunded' | 'refunded';
  
  // Deductions
  deductions: SecurityDepositDeduction[];
  totalDeductions?: number;
  
  // Refund Information
  refundDate?: string;
  refundAmount?: number;
  refundMethod?: 'check' | 'bank_transfer' | 'cash';
  refundNotes?: string;
  
  // State/Legal Requirements
  stateRequirements?: StateRequirements;
  
  // General
  notes?: string;
  createdAt?: string;
  updatedAt?: string;
  
  // Related Data (joined from API)
  tenant_name?: string;
  property_address?: string;
  lease_start_date?: string;
  lease_end_date?: string;
}

export interface CreateSecurityDepositRequest {
  leaseId: string;
  tenantId: string;
  propertyId: string;
  amount: number;
  dateReceived: string;
  bankAccount: string;
  paymentMethod: 'cash' | 'check' | 'bank_transfer' | 'cashiers_check' | 'money_order';
  referenceNumber: string;
  interestRate?: number;
  notes?: string;
  stateRequirements?: StateRequirements;
}

export interface UpdateSecurityDepositRequest extends Partial<CreateSecurityDepositRequest> {
  id: string;
  status?: 'unpaid' | 'held' | 'partial_refunded' | 'refunded';
}

export interface AddDeductionRequest {
  date: string;
  amount: number;
  description: string;
  category: 'damage' | 'cleaning' | 'unpaid_rent' | 'late_fees' | 'other';
  receipt?: string;
  notes?: string;
}

export interface ProcessRefundRequest {
  refundDate: string;
  refundMethod: 'check' | 'bank_transfer' | 'cash';
  refundNotes?: string;
}

// Utility type for security deposit summary/reports
export interface SecurityDepositSummary {
  totalDepositsHeld: number;
  totalAmount: number;
  totalInterestAccrued: number;
  totalDeductions: number;
  totalRefunded: number;
  depositsByStatus: {
    unpaid: number;
    held: number;
    partial_refunded: number;
    refunded: number;
  };
  avgDepositAmount: number;
  oldestDeposit?: SecurityDeposit;
  recentRefunds: SecurityDeposit[];
}
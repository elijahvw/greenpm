export interface Lease {
  id: string;
  propertyId?: string;
  property_id?: string; // API uses snake_case
  tenantId?: string;
  tenant_id?: string; // API uses snake_case
  landlordId?: string;
  landlord_id?: string; // API uses snake_case
  
  // Lease Terms - support both camelCase and snake_case
  startDate?: string;
  start_date?: string;
  endDate?: string;
  end_date?: string;
  monthlyRent?: number;
  rent_amount?: number; // API uses rent_amount
  securityDeposit?: number;
  security_deposit?: number; // API uses snake_case
  lateFeePenalty?: number;
  late_fee_penalty?: number; // API uses snake_case
  gracePeriodDays?: number;
  grace_period_days?: number; // API uses snake_case
  
  // Lease Details
  leaseType?: 'fixed' | 'month-to-month' | 'yearly';
  lease_type?: 'fixed' | 'month-to-month' | 'yearly'; // API uses snake_case
  status?: 'active' | 'expired' | 'terminated' | 'pending' | 'draft' | 'renewed';
  renewalOption?: boolean;
  renewal_option?: boolean; // API uses snake_case
  petPolicy?: {
    allowed: boolean;
    deposit: number;
    monthlyFee: number;
    restrictions: string;
  };
  pet_policy?: {
    allowed: boolean;
    deposit: number;
    monthly_fee: number;
    restrictions: string;
  }; // API uses snake_case
  
  // Utilities and Responsibilities
  utilitiesIncluded?: string[];
  utilities_included?: string[]; // API uses snake_case
  tenantResponsibilities?: string[];
  tenant_responsibilities?: string[]; // API uses snake_case
  landlordResponsibilities?: string[];
  landlord_responsibilities?: string[]; // API uses snake_case
  
  // Additional Terms
  specialTerms?: string;
  special_terms?: string; // API uses snake_case
  notes?: string;
  
  // Documents
  leaseDocument?: string; // URL to signed lease document
  lease_document?: string; // API uses snake_case
  attachments?: string[]; // URLs to additional documents
  
  // Timestamps
  createdAt?: string;
  created_at?: string; // API uses snake_case
  updatedAt?: string;
  updated_at?: string; // API uses snake_case
  signedAt?: string;
  signed_at?: string; // API uses snake_case
  
  // Additional API fields
  property_name?: string;
  property_address?: string;
  tenant_name?: string;
  tenant_email?: string;
  tenant_phone?: string;
  landlord_name?: string;
  landlord_email?: string;
  total_payments?: number;
  last_payment_date?: string;
  
  // Related Data (populated when needed)
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
    phone: string;
  };
}

export interface CreateLeaseRequest {
  propertyId: string;
  tenantId: string;
  startDate: string;
  endDate: string;
  monthlyRent: number;
  securityDeposit?: number;
  lateFeePenalty?: number;
  gracePeriodDays?: number;
  leaseType?: 'fixed' | 'month-to-month' | 'yearly';
  renewalOption?: boolean;
  status?: 'active' | 'expired' | 'terminated' | 'pending' | 'draft' | 'renewed';
  petPolicy?: {
    allowed: boolean;
    deposit: number;
    monthlyFee: number;
    restrictions: string;
  };
  utilitiesIncluded?: string[];
  tenantResponsibilities?: string[];
  landlordResponsibilities?: string[];
  specialTerms?: string;
  notes?: string;
}

export interface UpdateLeaseRequest extends Partial<CreateLeaseRequest> {
  id: string;
  status?: 'active' | 'expired' | 'terminated' | 'pending' | 'draft' | 'renewed';
}

export interface LeaseRenewal {
  id: string;
  originalLeaseId: string;
  newStartDate: string;
  newEndDate: string;
  newMonthlyRent: number;
  rentIncrease: number;
  renewalTerms: string;
  status: 'pending' | 'approved' | 'rejected';
  createdAt: string;
}

export interface LeaseTermination {
  id: string;
  leaseId: string;
  terminationDate: string;
  reason: string;
  noticePeriod: number;
  penaltyAmount: number;
  refundableDeposit: number;
  finalInspectionDate?: string;
  status: 'pending' | 'approved' | 'completed';
  createdAt: string;
}
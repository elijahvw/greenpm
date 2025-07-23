export interface Tenant {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth?: string;
  socialSecurityNumber?: string;
  emergencyContact?: {
    name: string;
    phone: string;
    relationship: string;
  };
  employment?: {
    employer: string;
    position: string;
    monthlyIncome: number;
    employmentStartDate: string;
  };
  address?: {
    street: string;
    city: string;
    state: string;
    zipCode: string;
    country: string;
  };
  status?: 'active' | 'inactive' | 'pending' | 'evicted';
  leaseId?: string;
  propertyId?: string;
  moveInDate?: string;
  moveOutDate?: string;
  notes?: string;
  documents: string[];
  createdAt: string;
  updatedAt: string;
  landlordId?: string;
  isActive?: boolean;
  
  // Additional fields from lease data
  currentProperty?: string;
  currentRent?: number;
  leaseStartDate?: string;
  leaseEndDate?: string;
  leaseHistory?: any[];
  paymentHistory?: any[];
}

export interface CreateTenantRequest {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string;
  socialSecurityNumber?: string;
  emergencyContact: {
    name: string;
    phone: string;
    relationship: string;
  };
  employment: {
    employer: string;
    position: string;
    monthlyIncome: number;
    employmentStartDate: string;
  };
  address: {
    street: string;
    city: string;
    state: string;
    zipCode: string;
    country: string;
  };
  notes?: string;
}

export interface UpdateTenantRequest extends Partial<CreateTenantRequest> {
  id: string;
  status?: 'active' | 'inactive' | 'pending' | 'evicted';
}
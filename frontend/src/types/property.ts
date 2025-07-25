export interface Property {
  id: string;
  name?: string;
  title?: string; // API returns title
  address?: string | {
    street: string;
    unit?: string;  // Optional unit/apartment number
    city: string;
    state: string;
    zipCode: string;
    country: string;
  };
  // Individual address fields from API
  street?: string;
  address_line1?: string;
  address_line2?: string;  // Unit/apartment number from API
  city?: string;
  state?: string;
  zipCode?: string;
  zip_code?: string;
  type?: 'apartment' | 'house' | 'condo' | 'townhouse' | 'commercial' | 'studio';
  bedrooms?: number;
  bathrooms?: number;
  squareFeet?: number;
  square_feet?: number; // API uses snake_case
  rentAmount?: number;
  rent_amount?: number; // API uses snake_case
  deposit?: number;
  description?: string;
  amenities?: string[];
  images?: string[];
  status?: 'available' | 'occupied' | 'maintenance' | 'inactive';
  createdAt?: string;
  created_at?: string; // API uses snake_case
  updatedAt?: string;
  updated_at?: string; // API uses snake_case
  landlordId?: string;
  owner_id?: string; // API uses snake_case
  owner_name?: string;
  lease_count?: number;
  current_tenant?: string;
  is_active?: boolean;
  
  // Lease integration fields
  lease_status?: 'vacant' | 'occupied' | 'pending';
  current_lease?: {
    id: string;
    status: string;
    start_date?: string;
    end_date?: string;
    monthly_rent?: number;
    tenant_name?: string;
    tenant_email?: string;
  };
}

export interface CreatePropertyRequest {
  name: string;
  address: {
    street: string;
    unit?: string;  // Optional unit/apartment number
    city: string;
    state: string;
    zipCode: string;
    country: string;
  };
  type: 'apartment' | 'house' | 'condo' | 'townhouse' | 'commercial' | 'studio';
  bedrooms: number;
  bathrooms: number;
  squareFeet: number;
  rentAmount: number;
  deposit: number;
  description: string;
  amenities: string[];
}

export interface UpdatePropertyRequest extends Partial<CreatePropertyRequest> {
  id: string;
}
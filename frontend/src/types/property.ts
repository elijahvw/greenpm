export interface Property {
  id: string;
  name: string;
  address: string | {
    street: string;
    city: string;
    state: string;
    zipCode: string;
    country: string;
  };
  type: 'apartment' | 'house' | 'condo' | 'townhouse' | 'commercial' | 'studio';
  bedrooms: number;
  bathrooms: number;
  squareFeet?: number;
  square_feet?: number; // API uses snake_case
  rentAmount?: number;
  rent_amount?: number; // API uses snake_case
  deposit?: number;
  description: string;
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
}

export interface CreatePropertyRequest {
  name: string;
  address: {
    street: string;
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
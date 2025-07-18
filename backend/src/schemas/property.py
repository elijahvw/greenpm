"""
Green PM - Property Schemas
"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator

from src.models.property import PropertyType, PropertyStatus

class PropertyBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    property_type: PropertyType
    status: PropertyStatus = PropertyStatus.DRAFT
    
    # Address
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=50)
    zip_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(default="US", max_length=50)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    
    # Property details
    bedrooms: int = Field(default=0, ge=0)
    bathrooms: float = Field(default=0, ge=0)
    square_feet: Optional[int] = Field(None, ge=0)
    lot_size: Optional[int] = Field(None, ge=0)
    year_built: Optional[int] = Field(None, ge=1800, le=2100)
    
    # Rental info
    rent_amount: Decimal = Field(..., ge=0)
    security_deposit: Optional[Decimal] = Field(None, ge=0)
    pet_deposit: Optional[Decimal] = Field(None, ge=0)
    application_fee: Optional[Decimal] = Field(None, ge=0)
    
    # Policies
    pets_allowed: bool = False
    smoking_allowed: bool = False
    furnished: bool = False
    utilities_included: Optional[str] = None
    
    # Availability
    available_date: Optional[datetime] = None
    lease_term_months: int = Field(default=12, ge=1, le=60)
    
    # SEO and marketing
    slug: Optional[str] = Field(None, max_length=255)
    featured: bool = False
    virtual_tour_url: Optional[str] = Field(None, max_length=500)

class PropertyCreate(PropertyBase):
    pass

class PropertyUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    property_type: Optional[PropertyType] = None
    status: Optional[PropertyStatus] = None
    
    # Address
    address_line1: Optional[str] = Field(None, min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=50)
    zip_code: Optional[str] = Field(None, min_length=1, max_length=20)
    country: Optional[str] = Field(None, max_length=50)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    
    # Property details
    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[float] = Field(None, ge=0)
    square_feet: Optional[int] = Field(None, ge=0)
    lot_size: Optional[int] = Field(None, ge=0)
    year_built: Optional[int] = Field(None, ge=1800, le=2100)
    
    # Rental info
    rent_amount: Optional[Decimal] = Field(None, ge=0)
    security_deposit: Optional[Decimal] = Field(None, ge=0)
    pet_deposit: Optional[Decimal] = Field(None, ge=0)
    application_fee: Optional[Decimal] = Field(None, ge=0)
    
    # Policies
    pets_allowed: Optional[bool] = None
    smoking_allowed: Optional[bool] = None
    furnished: Optional[bool] = None
    utilities_included: Optional[str] = None
    
    # Availability
    available_date: Optional[datetime] = None
    lease_term_months: Optional[int] = Field(None, ge=1, le=60)
    
    # SEO and marketing
    slug: Optional[str] = Field(None, max_length=255)
    featured: Optional[bool] = None
    virtual_tour_url: Optional[str] = Field(None, max_length=500)

class PropertyResponse(PropertyBase):
    id: int
    uuid: str
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    full_address: str
    is_available: bool
    
    class Config:
        from_attributes = True

class PropertyListResponse(BaseModel):
    properties: List[PropertyResponse]
    total: int
    skip: int
    limit: int
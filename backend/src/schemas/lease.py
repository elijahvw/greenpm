"""
Lease Management Schemas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, validator

class LeaseStatus(str, Enum):
    pending = "pending"
    active = "active"
    renewed = "renewed"
    terminated = "terminated"
    expired = "expired"

class LeaseTerms(BaseModel):
    pet_policy: Optional[str] = None
    smoking_allowed: bool = False
    subletting_allowed: bool = False
    maintenance_responsibility: Optional[str] = None
    utilities_included: Optional[List[str]] = []
    parking_included: bool = False
    additional_terms: Optional[str] = None

class LeaseCreate(BaseModel):
    property_id: str
    tenant_id: str
    start_date: datetime
    end_date: datetime
    monthly_rent: Decimal = Field(..., gt=0)
    security_deposit: Decimal = Field(..., ge=0)
    late_fee_amount: Optional[Decimal] = Field(None, ge=0)
    late_fee_grace_period: Optional[int] = Field(None, ge=0)
    lease_terms: Optional[LeaseTerms] = None
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v

class LeaseUpdate(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    monthly_rent: Optional[Decimal] = None
    security_deposit: Optional[Decimal] = None
    late_fee_amount: Optional[Decimal] = None
    late_fee_grace_period: Optional[int] = None
    lease_terms: Optional[LeaseTerms] = None
    status: Optional[LeaseStatus] = None

class LeaseRenewalRequest(BaseModel):
    new_start_date: datetime
    new_end_date: datetime
    new_monthly_rent: Optional[Decimal] = None
    new_security_deposit: Optional[Decimal] = None
    new_lease_terms: Optional[LeaseTerms] = None
    
    @validator('new_end_date')
    def validate_new_end_date(cls, v, values):
        if 'new_start_date' in values and v <= values['new_start_date']:
            raise ValueError('End date must be after start date')
        return v

class LeaseResponse(BaseModel):
    id: str
    property_id: str
    tenant_id: str
    landlord_id: str
    start_date: datetime
    end_date: datetime
    monthly_rent: Decimal
    security_deposit: Decimal
    late_fee_amount: Optional[Decimal] = None
    late_fee_grace_period: Optional[int] = None
    lease_terms: Optional[LeaseTerms] = None
    status: LeaseStatus
    document_url: Optional[str] = None
    signatures: Optional[Dict[str, Any]] = {}
    fully_signed: bool = False
    signed_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    terminated_at: Optional[datetime] = None
    termination_date: Optional[datetime] = None
    termination_reason: Optional[str] = None
    renewed_from: Optional[str] = None
    renewed_to: Optional[str] = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LeaseList(BaseModel):
    leases: List[LeaseResponse]
    total: int
    skip: int
    limit: int
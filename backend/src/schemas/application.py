"""
Application Management Schemas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator

class ApplicationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    leased = "leased"

class ApplicationCreate(BaseModel):
    property_id: str
    annual_income: float = Field(..., gt=0)
    employment_status: str
    employer_name: str
    employment_duration: Optional[str] = None
    previous_address: Optional[str] = None
    move_in_date: datetime
    emergency_contact_name: str
    emergency_contact_phone: str
    references: Optional[List[Dict[str, Any]]] = []
    pets: Optional[List[Dict[str, Any]]] = []
    additional_notes: Optional[str] = None
    
    @validator('annual_income')
    def validate_income(cls, v):
        if v <= 0:
            raise ValueError('Annual income must be greater than 0')
        return v

class ApplicationUpdate(BaseModel):
    annual_income: Optional[float] = None
    employment_status: Optional[str] = None
    employer_name: Optional[str] = None
    employment_duration: Optional[str] = None
    previous_address: Optional[str] = None
    move_in_date: Optional[datetime] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    references: Optional[List[Dict[str, Any]]] = None
    pets: Optional[List[Dict[str, Any]]] = None
    additional_notes: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    screening_data: Optional[Dict[str, Any]] = None
    landlord_notes: Optional[str] = None

class ScreeningData(BaseModel):
    provider: str
    credit_score: Optional[int] = None
    background_check: Optional[str] = None
    eviction_history: Optional[str] = None
    employment_verification: Optional[str] = None
    income_verification: Optional[str] = None
    rental_history: Optional[str] = None
    report_date: Optional[datetime] = None
    recommendations: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: str
    property_id: str
    applicant_id: str
    annual_income: float
    employment_status: str
    employer_name: str
    employment_duration: Optional[str] = None
    previous_address: Optional[str] = None
    move_in_date: datetime
    emergency_contact_name: str
    emergency_contact_phone: str
    references: Optional[List[Dict[str, Any]]] = []
    pets: Optional[List[Dict[str, Any]]] = []
    additional_notes: Optional[str] = None
    status: ApplicationStatus
    screening_data: Optional[Dict[str, Any]] = None
    screening_status: Optional[str] = None
    landlord_notes: Optional[str] = None
    documents: Optional[Dict[str, str]] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ApplicationList(BaseModel):
    applications: List[ApplicationResponse]
    total: int
    skip: int
    limit: int
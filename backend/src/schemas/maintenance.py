"""
Maintenance Management Schemas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field

class MaintenanceStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"
    closed = "closed"

class MaintenancePriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class MaintenanceCategory(str, Enum):
    plumbing = "plumbing"
    electrical = "electrical"
    hvac = "hvac"
    appliances = "appliances"
    flooring = "flooring"
    painting = "painting"
    landscaping = "landscaping"
    security = "security"
    other = "other"

class MaintenanceRequestCreate(BaseModel):
    property_id: str
    title: str
    description: str
    category: MaintenanceCategory
    priority: MaintenancePriority = MaintenancePriority.medium
    is_emergency: bool = False
    location: Optional[str] = None
    tenant_present_required: bool = False
    preferred_contact_method: Optional[str] = "email"
    additional_notes: Optional[str] = None

class MaintenanceRequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[MaintenanceCategory] = None
    priority: Optional[MaintenancePriority] = None
    is_emergency: Optional[bool] = None
    location: Optional[str] = None
    tenant_present_required: Optional[bool] = None
    preferred_contact_method: Optional[str] = None
    additional_notes: Optional[str] = None
    status: Optional[MaintenanceStatus] = None
    assigned_to: Optional[str] = None
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    resolution_notes: Optional[str] = None

class MaintenanceRequestResponse(BaseModel):
    id: str
    property_id: str
    tenant_id: Optional[str] = None
    landlord_id: str
    title: str
    description: str
    category: MaintenanceCategory
    priority: MaintenancePriority
    is_emergency: bool
    location: Optional[str] = None
    tenant_present_required: bool
    preferred_contact_method: Optional[str] = None
    additional_notes: Optional[str] = None
    status: MaintenanceStatus
    assigned_to: Optional[str] = None
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    resolution_notes: Optional[str] = None
    images: Optional[List[str]] = []
    created_by: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MaintenanceRequestList(BaseModel):
    requests: List[MaintenanceRequestResponse]
    total: int
    skip: int
    limit: int

class WorkOrderCreate(BaseModel):
    contractor_id: Optional[str] = None
    contractor_name: str
    contractor_phone: str
    contractor_email: Optional[str] = None
    scheduled_date: datetime
    estimated_duration: Optional[str] = None
    estimated_cost: Optional[Decimal] = None
    work_description: str
    materials_needed: Optional[str] = None
    special_instructions: Optional[str] = None

class WorkOrderUpdate(BaseModel):
    contractor_id: Optional[str] = None
    contractor_name: Optional[str] = None
    contractor_phone: Optional[str] = None
    contractor_email: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    estimated_duration: Optional[str] = None
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    work_description: Optional[str] = None
    materials_needed: Optional[str] = None
    special_instructions: Optional[str] = None
    status: Optional[str] = None
    completion_notes: Optional[str] = None

class WorkOrderResponse(BaseModel):
    id: str
    maintenance_request_id: str
    contractor_id: Optional[str] = None
    contractor_name: str
    contractor_phone: str
    contractor_email: Optional[str] = None
    scheduled_date: datetime
    estimated_duration: Optional[str] = None
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    work_description: str
    materials_needed: Optional[str] = None
    special_instructions: Optional[str] = None
    status: str
    completion_notes: Optional[str] = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class WorkOrderList(BaseModel):
    work_orders: List[WorkOrderResponse]
    total: int
    skip: int
    limit: int
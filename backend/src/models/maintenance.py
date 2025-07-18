"""
Green PM - Maintenance Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from src.core.database import Base

class MaintenanceStatus(str, Enum):
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class MaintenancePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"

class MaintenanceCategory(str, Enum):
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    HVAC = "hvac"
    APPLIANCES = "appliances"
    FLOORING = "flooring"
    PAINTING = "painting"
    PEST_CONTROL = "pest_control"
    SECURITY = "security"
    LANDSCAPING = "landscaping"
    OTHER = "other"

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"))  # Contractor/maintenance person
    
    # Request details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(MaintenanceCategory), nullable=False)
    priority = Column(SQLEnum(MaintenancePriority), nullable=False, default=MaintenancePriority.MEDIUM)
    status = Column(SQLEnum(MaintenanceStatus), nullable=False, default=MaintenanceStatus.SUBMITTED)
    
    # Location within property
    location = Column(String(255))  # e.g., "Kitchen", "Master Bathroom", "Living Room"
    
    # Access information
    tenant_present_required = Column(Boolean, default=False)
    access_instructions = Column(Text)
    preferred_contact_method = Column(String(20), default="email")
    
    # Scheduling
    preferred_date = Column(DateTime(timezone=True))
    scheduled_date = Column(DateTime(timezone=True))
    completed_date = Column(DateTime(timezone=True))
    
    # Cost estimation
    estimated_cost = Column(Numeric(10, 2))
    actual_cost = Column(Numeric(10, 2))
    
    # Work details
    work_performed = Column(Text)
    parts_used = Column(Text)
    contractor_notes = Column(Text)
    
    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime(timezone=True))
    tenant_satisfaction_rating = Column(Integer)  # 1-5 scale
    tenant_feedback = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    property_rel = relationship("Property", back_populates="maintenance_requests")
    tenant = relationship("User", back_populates="maintenance_requests", foreign_keys=[tenant_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    images = relationship("MaintenanceImage", back_populates="maintenance_request", cascade="all, delete-orphan")
    
    @property
    def is_emergency(self) -> bool:
        return self.priority == MaintenancePriority.EMERGENCY
    
    @property
    def is_completed(self) -> bool:
        return self.status == MaintenanceStatus.COMPLETED
    
    @property
    def days_since_submitted(self) -> int:
        from datetime import datetime
        return (datetime.utcnow() - self.created_at).days
    
    def __repr__(self):
        return f"<MaintenanceRequest(id={self.id}, property_id={self.property_id}, title='{self.title}', status='{self.status}')>"

class MaintenanceImage(Base):
    __tablename__ = "maintenance_images"
    
    id = Column(Integer, primary_key=True, index=True)
    maintenance_request_id = Column(Integer, ForeignKey("maintenance_requests.id"), nullable=False)
    
    # Image info
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    
    # Metadata
    caption = Column(String(255))
    image_type = Column(String(20), default="before")  # "before", "during", "after"
    
    # File info
    file_size = Column(Integer)
    mime_type = Column(String(100))
    width = Column(Integer)
    height = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    maintenance_request = relationship("MaintenanceRequest", back_populates="images")
    
    def __repr__(self):
        return f"<MaintenanceImage(id={self.id}, maintenance_request_id={self.maintenance_request_id}, filename='{self.filename}')>"
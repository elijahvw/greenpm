"""
Green PM - Company Model (Multi-tenant Core Entity)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from src.core.database import Base

class CompanyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    TRIAL = "TRIAL"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Basic info
    name = Column(String(255), nullable=False, index=True)
    subdomain = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(SQLEnum(CompanyStatus), nullable=False, default=CompanyStatus.TRIAL)
    
    # Contact info
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    website = Column(String(255))
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    country = Column(String(50), default="US")
    
    # Branding
    logo_url = Column(String(500))
    primary_color = Column(String(7))  # Hex color
    secondary_color = Column(String(7))  # Hex color
    custom_css = Column(Text)
    
    # Settings
    timezone = Column(String(50), default="UTC")
    currency = Column(String(3), default="USD")
    date_format = Column(String(20), default="MM/DD/YYYY")
    language = Column(String(5), default="en")
    
    # Limits & quotas
    max_properties = Column(Integer, default=10)
    max_users = Column(Integer, default=5)
    max_storage_gb = Column(Integer, default=1)
    max_api_calls_per_month = Column(Integer, default=1000)
    
    # Usage tracking
    current_properties = Column(Integer, default=0)
    current_users = Column(Integer, default=0)
    current_storage_gb = Column(Integer, default=0)
    current_api_calls_this_month = Column(Integer, default=0)
    
    # Suspension info
    suspended_at = Column(DateTime(timezone=True))
    suspended_reason = Column(String(500))
    suspended_by = Column(String(255))  # Platform admin who suspended
    
    # Internal notes
    internal_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="company")
    properties = relationship("Property", back_populates="company")
    leases = relationship("Lease", back_populates="company")
    payments = relationship("Payment", back_populates="company")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="company")
    messages = relationship("Message", back_populates="company")
    applications = relationship("Application", back_populates="company")
    
    # Multi-tenant specific relationships
    plan_assignments = relationship("PlanAssignment", back_populates="company")
    feature_flags = relationship("FeatureFlag", back_populates="company")
    contracts = relationship("Contract", back_populates="company")
    audit_logs = relationship("AuditLog", back_populates="company")
    
    @property
    def is_active(self) -> bool:
        return self.status == CompanyStatus.ACTIVE
    
    @property
    def is_suspended(self) -> bool:
        return self.status == CompanyStatus.SUSPENDED
    
    @property
    def is_trial(self) -> bool:
        return self.status == CompanyStatus.TRIAL
    
    @property
    def full_address(self) -> str:
        parts = [self.address_line1, self.address_line2, self.city, self.state, self.zip_code]
        return ", ".join(filter(None, parts))
    
    @property
    def properties_usage_percent(self) -> float:
        if self.max_properties == 0:
            return 0.0
        return (self.current_properties / self.max_properties) * 100
    
    @property
    def users_usage_percent(self) -> float:
        if self.max_users == 0:
            return 0.0
        return (self.current_users / self.max_users) * 100
    
    @property
    def storage_usage_percent(self) -> float:
        if self.max_storage_gb == 0:
            return 0.0
        return (self.current_storage_gb / self.max_storage_gb) * 100
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', subdomain='{self.subdomain}', status='{self.status}')>"
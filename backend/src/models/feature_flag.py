"""
Green PM - Feature Flag Models (Module Access Control)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from src.core.database import Base

class ModuleKey(str, Enum):
    # Core modules
    PROPERTY_MANAGEMENT = "PROPERTY_MANAGEMENT"
    LEASE_MANAGEMENT = "LEASE_MANAGEMENT"
    TENANT_MANAGEMENT = "TENANT_MANAGEMENT"
    
    # Operations modules
    MAINTENANCE_REQUESTS = "MAINTENANCE_REQUESTS"
    INSPECTIONS = "INSPECTIONS"
    ACCOUNTING = "ACCOUNTING"
    PAYMENTS = "PAYMENTS"
    
    # Communication modules
    MESSAGING = "MESSAGING"
    TENANT_PORTAL = "TENANT_PORTAL"
    NOTIFICATIONS = "NOTIFICATIONS"
    
    # Advanced modules
    REPORTING = "REPORTING"
    ANALYTICS = "ANALYTICS"
    API_ACCESS = "API_ACCESS"
    WEBHOOKS = "WEBHOOKS"
    
    # Integrations
    STRIPE_INTEGRATION = "STRIPE_INTEGRATION"
    TWILIO_INTEGRATION = "TWILIO_INTEGRATION"
    SENDGRID_INTEGRATION = "SENDGRID_INTEGRATION"
    
    # Admin features
    MULTI_USER = "MULTI_USER"
    ROLE_MANAGEMENT = "ROLE_MANAGEMENT"
    AUDIT_LOGS = "AUDIT_LOGS"
    
    # Storage & files
    FILE_UPLOADS = "FILE_UPLOADS"
    DOCUMENT_STORAGE = "DOCUMENT_STORAGE"
    
    # Mobile
    MOBILE_APP = "MOBILE_APP"

class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Feature details
    module_key = Column(SQLEnum(ModuleKey), nullable=False, index=True)
    enabled = Column(Boolean, default=False, nullable=False, index=True)
    
    # Configuration (JSON object with module-specific settings)
    config = Column(JSON, default={})
    
    # Limits (module-specific limits)
    usage_limit = Column(Integer)  # e.g., max API calls, max storage
    current_usage = Column(Integer, default=0)
    
    # Override settings
    override_reason = Column(String(500))  # Why this was manually enabled/disabled
    override_by = Column(String(255))  # Platform admin who made the override
    override_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="feature_flags")
    
    @property
    def is_over_limit(self) -> bool:
        if self.usage_limit is None:
            return False
        return self.current_usage >= self.usage_limit
    
    @property
    def usage_percent(self) -> float:
        if self.usage_limit is None or self.usage_limit == 0:
            return 0.0
        return (self.current_usage / self.usage_limit) * 100
    
    def __repr__(self):
        return f"<FeatureFlag(id={self.id}, company_id={self.company_id}, module='{self.module_key}', enabled={self.enabled})>"

# Helper model for default feature configurations per plan
class PlanFeature(Base):
    __tablename__ = "plan_features"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False, index=True)
    
    # Feature details
    module_key = Column(SQLEnum(ModuleKey), nullable=False, index=True)
    enabled = Column(Boolean, default=False, nullable=False)
    
    # Default configuration for this feature on this plan
    default_config = Column(JSON, default={})
    default_usage_limit = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PlanFeature(id={self.id}, plan_id={self.plan_id}, module='{self.module_key}', enabled={self.enabled})>"
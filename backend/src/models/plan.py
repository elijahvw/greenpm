"""
Green PM - Plan Models (Subscription Management)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from src.core.database import Base

class BillingType(str, Enum):
    FLAT_MONTHLY = "FLAT_MONTHLY"
    PER_PROPERTY = "PER_PROPERTY"
    PER_USER = "PER_USER"
    PER_UNIT = "PER_UNIT"
    CUSTOM = "CUSTOM"

class PlanStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DEPRECATED = "DEPRECATED"

class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Basic info
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(SQLEnum(PlanStatus), nullable=False, default=PlanStatus.ACTIVE)
    
    # Pricing
    billing_type = Column(SQLEnum(BillingType), nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)  # Base monthly price
    per_unit_price = Column(Numeric(10, 2), default=0)  # Additional per-unit cost
    setup_fee = Column(Numeric(10, 2), default=0)
    
    # Limits
    max_properties = Column(Integer, default=0)  # 0 = unlimited
    max_users = Column(Integer, default=0)  # 0 = unlimited
    max_storage_gb = Column(Integer, default=0)  # 0 = unlimited
    max_api_calls_per_month = Column(Integer, default=0)  # 0 = unlimited
    
    # Features (JSON object with feature keys and limits)
    features = Column(JSON, default={})
    
    # Overage pricing
    overage_property_price = Column(Numeric(10, 2), default=0)
    overage_user_price = Column(Numeric(10, 2), default=0)
    overage_storage_price_per_gb = Column(Numeric(10, 2), default=0)
    overage_api_price_per_1000 = Column(Numeric(10, 2), default=0)
    
    # Display
    display_order = Column(Integer, default=0)
    is_popular = Column(Boolean, default=False)
    is_custom = Column(Boolean, default=False)
    
    # Stripe integration
    stripe_price_id = Column(String(255))  # Stripe Price ID
    stripe_product_id = Column(String(255))  # Stripe Product ID
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    plan_assignments = relationship("PlanAssignment", back_populates="plan")
    
    @property
    def is_active(self) -> bool:
        return self.status == PlanStatus.ACTIVE
    
    @property
    def is_unlimited_properties(self) -> bool:
        return self.max_properties == 0
    
    @property
    def is_unlimited_users(self) -> bool:
        return self.max_users == 0
    
    @property
    def is_unlimited_storage(self) -> bool:
        return self.max_storage_gb == 0
    
    def __repr__(self):
        return f"<Plan(id={self.id}, name='{self.name}', billing_type='{self.billing_type}', base_price={self.base_price})>"

class PlanAssignment(Base):
    __tablename__ = "plan_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False, index=True)
    
    # Assignment details
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True))  # NULL = active indefinitely
    active = Column(Boolean, default=True, index=True)
    
    # Custom pricing overrides (for enterprise deals)
    custom_base_price = Column(Numeric(10, 2))
    custom_per_unit_price = Column(Numeric(10, 2))
    custom_limits = Column(JSON, default={})  # Override plan limits
    
    # Billing
    billing_cycle_start = Column(DateTime(timezone=True))
    next_billing_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="plan_assignments")
    plan = relationship("Plan", back_populates="plan_assignments")
    
    @property
    def effective_base_price(self) -> float:
        return float(self.custom_base_price or self.plan.base_price)
    
    @property
    def effective_per_unit_price(self) -> float:
        return float(self.custom_per_unit_price or self.plan.per_unit_price)
    
    @property
    def is_active(self) -> bool:
        return self.active and (self.end_at is None or self.end_at > func.now())
    
    def __repr__(self):
        return f"<PlanAssignment(id={self.id}, company_id={self.company_id}, plan_id={self.plan_id}, active={self.active})>"
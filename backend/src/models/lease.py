"""
Green PM - Lease Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum as SQLEnum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from src.core.database import Base

class LeaseStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"

class LeaseType(str, Enum):
    FIXED_TERM = "fixed_term"
    MONTH_TO_MONTH = "month_to_month"
    WEEK_TO_WEEK = "week_to_week"

class Lease(Base):
    __tablename__ = "leases"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Parties
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    landlord_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Lease details
    lease_type = Column(SQLEnum(LeaseType), nullable=False, default=LeaseType.FIXED_TERM)
    status = Column(SQLEnum(LeaseStatus), nullable=False, default=LeaseStatus.DRAFT)
    
    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    move_in_date = Column(Date)
    move_out_date = Column(Date)
    
    # Financial terms
    monthly_rent = Column(Numeric(10, 2), nullable=False)
    security_deposit = Column(Numeric(10, 2))
    pet_deposit = Column(Numeric(10, 2))
    late_fee = Column(Numeric(10, 2))
    late_fee_grace_days = Column(Integer, default=5)
    
    # Payment terms
    rent_due_day = Column(Integer, default=1)  # Day of month rent is due
    payment_method = Column(String(50))  # "online", "check", "cash", etc.
    
    # Lease terms
    terms_and_conditions = Column(Text)
    special_provisions = Column(Text)
    
    # Signatures
    tenant_signed = Column(Boolean, default=False)
    landlord_signed = Column(Boolean, default=False)
    tenant_signed_date = Column(DateTime(timezone=True))
    landlord_signed_date = Column(DateTime(timezone=True))
    tenant_signature_ip = Column(String(45))
    landlord_signature_ip = Column(String(45))
    
    # Renewal
    auto_renew = Column(Boolean, default=False)
    renewal_notice_days = Column(Integer, default=30)
    parent_lease_id = Column(Integer, ForeignKey("leases.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    property = relationship("Property", back_populates="leases")
    tenant = relationship("User", back_populates="leases", foreign_keys=[tenant_id])
    landlord = relationship("User", foreign_keys=[landlord_id])
    documents = relationship("LeaseDocument", back_populates="lease", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="lease")
    parent_lease = relationship("Lease", remote_side=[id])
    renewal_leases = relationship("Lease", back_populates="parent_lease")
    
    @property
    def is_active(self) -> bool:
        return self.status == LeaseStatus.ACTIVE
    
    @property
    def is_fully_signed(self) -> bool:
        return self.tenant_signed and self.landlord_signed
    
    @property
    def days_until_expiry(self) -> int:
        if not self.end_date:
            return None
        from datetime import date
        return (self.end_date - date.today()).days
    
    def __repr__(self):
        return f"<Lease(id={self.id}, property_id={self.property_id}, tenant_id={self.tenant_id}, status='{self.status}')>"

class LeaseDocument(Base):
    __tablename__ = "lease_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    lease_id = Column(Integer, ForeignKey("leases.id"), nullable=False)
    
    # Document info
    document_type = Column(String(50), nullable=False)  # "lease", "addendum", "notice", etc.
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    url = Column(String(500), nullable=False)
    
    # Metadata
    description = Column(Text)
    version = Column(String(20), default="1.0")
    
    # File info
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # Signatures (for e-signature tracking)
    requires_tenant_signature = Column(Boolean, default=False)
    requires_landlord_signature = Column(Boolean, default=False)
    tenant_signed = Column(Boolean, default=False)
    landlord_signed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    lease = relationship("Lease", back_populates="documents")
    
    def __repr__(self):
        return f"<LeaseDocument(id={self.id}, lease_id={self.lease_id}, title='{self.title}')>"
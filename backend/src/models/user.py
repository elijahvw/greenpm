"""
Green PM - User Model (Multi-tenant Enhanced)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from src.core.database import Base

class UserRole(str, Enum):
    PLATFORM_ADMIN = "PLATFORM_ADMIN"  # Internal staff with access to all companies
    ADMIN = "ADMIN"  # Company admin
    LANDLORD = "LANDLORD"
    TENANT = "TENANT"

class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Multi-tenant support
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)  # NULL for platform admins
    
    # Basic info
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Authentication
    hashed_password = Column(String(255))
    firebase_uid = Column(String(255), unique=True, index=True)
    
    # Role and status
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.TENANT)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.PENDING)
    
    # Profile
    avatar_url = Column(String(500))
    bio = Column(Text)
    date_of_birth = Column(String(20))
    social_security_number = Column(String(20))
    notes = Column(Text)
    move_in_date = Column(String(20))
    move_out_date = Column(String(20))
    
    # Employment Information
    employer = Column(String(255))
    position = Column(String(255))
    monthly_income = Column(Integer)
    employment_start_date = Column(String(20))
    
    # Emergency Contact
    emergency_contact_name = Column(String(255))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relationship = Column(String(100))
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    country = Column(String(50), default="US")
    
    # Verification
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    identity_verified = Column(Boolean, default=False)
    
    # Security
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))
    last_login = Column(DateTime(timezone=True))
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime(timezone=True))
    
    # Preferences
    notification_email = Column(Boolean, default=True)
    notification_sms = Column(Boolean, default=True)
    notification_push = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="users")
    owned_properties = relationship("Property", back_populates="owner", foreign_keys="Property.owner_id")
    leases = relationship("Lease", back_populates="tenant", foreign_keys="Lease.tenant_id")
    payments = relationship("Payment", back_populates="user")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="tenant", foreign_keys="MaintenanceRequest.tenant_id")
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    received_messages = relationship("Message", back_populates="recipient", foreign_keys="Message.recipient_id")
    applications = relationship("Application", back_populates="applicant")
    audit_logs = relationship("AuditLog", back_populates="user", foreign_keys="AuditLog.user_id")
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_landlord(self) -> bool:
        return self.role == UserRole.LANDLORD
    
    @property
    def is_tenant(self) -> bool:
        return self.role == UserRole.TENANT
    
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    @property
    def is_platform_admin(self) -> bool:
        return self.role == UserRole.PLATFORM_ADMIN
    
    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
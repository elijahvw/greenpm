"""
Green PM - Audit Log Model (Multi-tenant Enhanced)
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from src.core.database import Base

class AuditAction(str, Enum):
    # CRUD operations
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    
    # Authentication
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    PASSWORD_RESET = "PASSWORD_RESET"
    
    # Admin operations
    SUSPEND = "SUSPEND"
    UNSUSPEND = "UNSUSPEND"
    IMPERSONATE_START = "IMPERSONATE_START"
    IMPERSONATE_END = "IMPERSONATE_END"
    
    # Billing operations
    PLAN_CHANGE = "PLAN_CHANGE"
    INVOICE_GENERATED = "INVOICE_GENERATED"
    PAYMENT_PROCESSED = "PAYMENT_PROCESSED"
    
    # Feature flags
    FEATURE_ENABLED = "FEATURE_ENABLED"
    FEATURE_DISABLED = "FEATURE_DISABLED"
    
    # System operations
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    BACKUP = "BACKUP"

class AuditSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Multi-tenant support
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)  # NULL for platform-level actions
    
    # Actor (who performed the action)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)  # NULL for system actions
    actor_email = Column(String(255))  # Store email for audit trail even if user is deleted
    actor_role = Column(String(50))
    
    # Impersonation tracking
    impersonated_by_user_id = Column(Integer, ForeignKey("users.id"))  # Platform admin doing impersonation
    is_impersonated_action = Column(Boolean, default=False, index=True)
    
    # Action details
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)  # "user", "property", "lease", "company", etc.
    resource_id = Column(String(50), index=True)  # ID of the affected resource
    resource_name = Column(String(255))  # Human-readable name of the resource
    
    # Request details
    ip_address = Column(String(45), index=True)
    user_agent = Column(String(500))
    request_method = Column(String(10))
    request_path = Column(String(500))
    request_id = Column(String(36))  # Correlation ID for request tracing
    
    # Change details
    old_values = Column(JSON)  # Previous values (for updates)
    new_values = Column(JSON)  # New values (for creates/updates)
    
    # Additional context
    description = Column(Text)
    context_metadata = Column(JSON)  # Additional contextual information
    
    # Severity and categorization
    severity = Column(SQLEnum(AuditSeverity), default=AuditSeverity.LOW, index=True)
    category = Column(String(50), index=True)  # "security", "billing", "data", etc.
    
    # Status
    success = Column(Boolean, default=True, index=True)
    error_message = Column(Text)
    error_code = Column(String(50))
    
    # Compliance and retention
    retention_until = Column(DateTime(timezone=True))  # When this log can be deleted
    is_sensitive = Column(Boolean, default=False)  # Contains PII or sensitive data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    company = relationship("Company", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs", foreign_keys=[user_id])
    impersonated_by = relationship("User", foreign_keys=[impersonated_by_user_id])
    
    @property
    def is_platform_action(self) -> bool:
        """True if this is a platform-level action (not company-specific)"""
        return self.company_id is None
    
    @property
    def is_security_related(self) -> bool:
        """True if this is a security-related action"""
        return self.category == "security" or self.action in [
            AuditAction.LOGIN, AuditAction.LOGIN_FAILED, AuditAction.SUSPEND,
            AuditAction.IMPERSONATE_START, AuditAction.PASSWORD_RESET
        ]
    
    @property
    def display_actor(self) -> str:
        """Human-readable actor description"""
        if self.is_impersonated_action and self.impersonated_by:
            return f"{self.actor_email} (impersonated by platform admin)"
        return self.actor_email or "System"
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, company_id={self.company_id}, action='{self.action}', resource_type='{self.resource_type}', actor='{self.actor_email}')>"
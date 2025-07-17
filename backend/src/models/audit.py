"""
Green PM - Audit Log Model
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # User who performed the action
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Action details
    action = Column(String(100), nullable=False)  # "create", "update", "delete", "login", etc.
    resource_type = Column(String(50), nullable=False)  # "user", "property", "lease", etc.
    resource_id = Column(String(50))  # ID of the affected resource
    
    # Request details
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    request_method = Column(String(10))
    request_path = Column(String(500))
    
    # Change details
    old_values = Column(JSON)  # Previous values (for updates)
    new_values = Column(JSON)  # New values (for creates/updates)
    
    # Additional context
    description = Column(Text)
    metadata = Column(JSON)  # Additional contextual information
    
    # Status
    success = Column(String(10), default=True)  # Whether the action was successful
    error_message = Column(Text)  # Error message if action failed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action='{self.action}', resource_type='{self.resource_type}')>"
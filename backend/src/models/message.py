"""
Green PM - Message Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from src.core.database import Base

class MessageStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class MessageType(str, Enum):
    TEXT = "text"
    EMAIL = "email"
    SMS = "sms"
    SYSTEM = "system"

class MessageThread(Base):
    __tablename__ = "message_threads"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Multi-tenant support
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Thread participants
    participant1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    participant2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Thread context
    property_id = Column(Integer, ForeignKey("properties.id"))
    lease_id = Column(Integer, ForeignKey("leases.id"))
    maintenance_request_id = Column(Integer, ForeignKey("maintenance_requests.id"))
    
    # Thread info
    subject = Column(String(255))
    is_archived = Column(Boolean, default=False)
    
    # Last message info
    last_message_at = Column(DateTime(timezone=True))
    last_message_preview = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="messages")
    participant1 = relationship("User", foreign_keys=[participant1_id])
    participant2 = relationship("User", foreign_keys=[participant2_id])
    property_rel = relationship("Property")
    lease = relationship("Lease")
    maintenance_request = relationship("MaintenanceRequest")
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")
    
    def get_other_participant(self, user_id: int):
        """Get the other participant in the thread"""
        return self.participant2 if self.participant1_id == user_id else self.participant1
    
    def __repr__(self):
        return f"<MessageThread(id={self.id}, participant1_id={self.participant1_id}, participant2_id={self.participant2_id})>"

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Multi-tenant support
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Message relationships
    thread_id = Column(Integer, ForeignKey("message_threads.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message content
    message_type = Column(SQLEnum(MessageType), nullable=False, default=MessageType.TEXT)
    subject = Column(String(255))
    content = Column(Text, nullable=False)
    
    # Message status
    status = Column(SQLEnum(MessageStatus), nullable=False, default=MessageStatus.SENT)
    
    # Delivery tracking
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    
    # External delivery (SMS/Email)
    external_message_id = Column(String(255))  # Twilio/SendGrid message ID
    
    # Attachments
    has_attachments = Column(Boolean, default=False)
    attachment_urls = Column(Text)  # JSON array of URLs
    
    # System messages
    is_system_message = Column(Boolean, default=False)
    system_event_type = Column(String(50))  # "lease_signed", "payment_received", etc.
    
    # Auto-generated messages
    is_automated = Column(Boolean, default=False)
    template_id = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="messages")
    thread = relationship("MessageThread", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages", foreign_keys=[sender_id])
    recipient = relationship("User", back_populates="received_messages", foreign_keys=[recipient_id])
    
    @property
    def is_read(self) -> bool:
        return self.status == MessageStatus.READ
    
    @property
    def is_delivered(self) -> bool:
        return self.status in [MessageStatus.DELIVERED, MessageStatus.READ]
    
    def __repr__(self):
        return f"<Message(id={self.id}, sender_id={self.sender_id}, recipient_id={self.recipient_id}, status='{self.status}')>"
"""
Green PM - Message Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    GENERAL = "general"
    MAINTENANCE = "maintenance"
    PAYMENT = "payment"
    LEASE = "lease"
    SYSTEM = "system"

class MessagePriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class MessageStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"
    DELETED = "deleted"

class MessageThreadCreate(BaseModel):
    subject: str = Field(..., max_length=200)
    property_id: Optional[str] = None
    lease_id: Optional[str] = None
    participant_ids: List[int] = Field(..., min_items=2)
    message_type: MessageType = MessageType.GENERAL
    priority: MessagePriority = MessagePriority.NORMAL

class MessageCreate(BaseModel):
    thread_id: str
    content: str = Field(..., max_length=5000)
    message_type: MessageType = MessageType.GENERAL
    priority: MessagePriority = MessagePriority.NORMAL
    attachments: Optional[List[str]] = None

class MessageUpdate(BaseModel):
    content: Optional[str] = Field(None, max_length=5000)
    is_read: Optional[bool] = None

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    thread_id: str
    sender_id: int
    content: str
    message_type: MessageType
    priority: MessagePriority
    is_read: bool
    read_by: Dict[str, bool] = {}
    attachments: List[str] = []
    created_at: datetime
    updated_at: datetime
    
    # Sender info
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None

class MessageThreadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    subject: str
    property_id: Optional[str] = None
    lease_id: Optional[str] = None
    participant_ids: List[int] = []
    message_type: MessageType
    priority: MessagePriority
    is_archived: bool = False
    last_message_at: Optional[datetime] = None
    unread_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    # Latest message preview
    latest_message: Optional[str] = None
    latest_sender_name: Optional[str] = None
    
    # Property info (if applicable)
    property_address: Optional[str] = None

class MessageList(BaseModel):
    messages: List[MessageResponse]
    total: int
    page: int
    pages: int
    has_next: bool
    has_prev: bool

class MessageThreadList(BaseModel):
    threads: List[MessageThreadResponse]
    total: int
    page: int
    pages: int
    has_next: bool
    has_prev: bool

class QuickMessageCreate(BaseModel):
    recipient_id: int
    subject: str = Field(..., max_length=200)
    content: str = Field(..., max_length=5000)
    property_id: Optional[str] = None
    message_type: MessageType = MessageType.GENERAL
    priority: MessagePriority = MessagePriority.NORMAL

class MessageSearchFilters(BaseModel):
    search: Optional[str] = None
    message_type: Optional[MessageType] = None
    priority: Optional[MessagePriority] = None
    property_id: Optional[str] = None
    sender_id: Optional[int] = None
    unread_only: bool = False
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class BulkMessageAction(BaseModel):
    message_ids: List[str] = Field(..., min_items=1)
    action: str = Field(..., pattern="^(mark_read|mark_unread|archive|delete)$")

class MessageStats(BaseModel):
    total_messages: int
    unread_messages: int
    threads_count: int
    urgent_messages: int
    messages_today: int
    messages_this_week: int

class NotificationPreferences(BaseModel):
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    instant_notifications: bool = True
    digest_frequency: str = Field("daily", pattern="^(instant|hourly|daily|weekly)$")
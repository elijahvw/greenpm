"""
Green PM - Payment Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum as SQLEnum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from src.core.database import Base

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIAL_REFUND = "partial_refund"

class PaymentType(str, Enum):
    RENT = "rent"
    SECURITY_DEPOSIT = "security_deposit"
    PET_DEPOSIT = "pet_deposit"
    APPLICATION_FEE = "application_fee"
    LATE_FEE = "late_fee"
    MAINTENANCE_FEE = "maintenance_fee"
    OTHER = "other"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    ACH = "ach"
    CHECK = "check"
    CASH = "cash"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lease_id = Column(Integer, ForeignKey("leases.id"))
    property_id = Column(Integer, ForeignKey("properties.id"))
    
    # Payment details
    payment_type = Column(SQLEnum(PaymentType), nullable=False)
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    
    # Amounts
    amount = Column(Numeric(10, 2), nullable=False)
    fee_amount = Column(Numeric(10, 2), default=0)
    net_amount = Column(Numeric(10, 2))  # Amount after fees
    
    # Payment period (for rent payments)
    period_start = Column(Date)
    period_end = Column(Date)
    due_date = Column(Date)
    
    # External payment info
    stripe_payment_intent_id = Column(String(255))
    stripe_charge_id = Column(String(255))
    external_transaction_id = Column(String(255))
    
    # Metadata
    description = Column(Text)
    notes = Column(Text)
    receipt_url = Column(String(500))
    
    # Refund info
    refund_amount = Column(Numeric(10, 2))
    refund_reason = Column(Text)
    refunded_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="payments")
    lease = relationship("Lease", back_populates="payments")
    property_rel = relationship("Property")
    
    @property
    def is_completed(self) -> bool:
        return self.status == PaymentStatus.COMPLETED
    
    @property
    def is_overdue(self) -> bool:
        if not self.due_date:
            return False
        from datetime import date
        return self.due_date < date.today() and self.status != PaymentStatus.COMPLETED
    
    def __repr__(self):
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.amount}, status='{self.status}')>"

class PaymentMethodModel(Base):
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Payment method details
    type = Column(SQLEnum(PaymentMethod), nullable=False)
    is_default = Column(Boolean, default=False)
    
    # Card details (encrypted)
    card_last_four = Column(String(4))
    card_brand = Column(String(20))
    card_exp_month = Column(Integer)
    card_exp_year = Column(Integer)
    
    # Bank details (encrypted)
    bank_name = Column(String(100))
    account_last_four = Column(String(4))
    routing_number_last_four = Column(String(4))
    
    # External IDs
    stripe_payment_method_id = Column(String(255))
    
    # Metadata
    nickname = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<PaymentMethodModel(id={self.id}, user_id={self.user_id}, type='{self.type}')>"
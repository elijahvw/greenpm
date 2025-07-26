"""
Green PM - Contract and Billing Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from src.core.database import Base

class RenewalType(str, Enum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"
    NO_RENEWAL = "NO_RENEWAL"

class ContractStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"

class BillingCycle(str, Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"
    CUSTOM = "CUSTOM"

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Contract details
    contract_number = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(SQLEnum(ContractStatus), nullable=False, default=ContractStatus.PENDING)
    
    # Terms
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=False)
    renewal_type = Column(SQLEnum(RenewalType), nullable=False, default=RenewalType.MANUAL)
    auto_renewal_notice_days = Column(Integer, default=30)
    
    # Billing
    billing_cycle = Column(SQLEnum(BillingCycle), nullable=False, default=BillingCycle.MONTHLY)
    currency = Column(String(3), default="USD")
    payment_terms_days = Column(Integer, default=30)  # Net 30
    
    # Payment method
    payment_method = Column(String(50))  # "stripe", "invoice", "check", etc.
    stripe_customer_id = Column(String(255))
    stripe_subscription_id = Column(String(255))
    
    # Contract terms (JSON object with custom terms)
    terms_json = Column(JSON, default={})
    
    # Pricing
    base_amount = Column(Numeric(10, 2), nullable=False)
    setup_fee = Column(Numeric(10, 2), default=0)
    discount_percent = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    
    # Legal
    signed_at = Column(DateTime(timezone=True))
    signed_by_name = Column(String(255))
    signed_by_email = Column(String(255))
    signed_by_ip = Column(String(45))
    contract_pdf_url = Column(String(500))
    
    # Cancellation
    cancelled_at = Column(DateTime(timezone=True))
    cancelled_by = Column(String(255))
    cancellation_reason = Column(Text)
    
    # Internal notes
    internal_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="contracts")
    invoices = relationship("Invoice", back_populates="contract")
    
    @property
    def is_active(self) -> bool:
        return self.status == ContractStatus.ACTIVE
    
    @property
    def is_expired(self) -> bool:
        return self.status == ContractStatus.EXPIRED or (self.end_at and self.end_at < func.now())
    
    @property
    def days_until_expiry(self) -> int:
        if not self.end_at:
            return 0
        delta = self.end_at - func.now()
        return delta.days if delta.days > 0 else 0
    
    @property
    def effective_amount(self) -> float:
        base = float(self.base_amount)
        if self.discount_amount:
            return base - float(self.discount_amount)
        elif self.discount_percent:
            return base * (1 - float(self.discount_percent) / 100)
        return base
    
    def __repr__(self):
        return f"<Contract(id={self.id}, company_id={self.company_id}, number='{self.contract_number}', status='{self.status}')>"

class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, index=True)
    
    # Invoice details
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(SQLEnum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT)
    
    # Amounts
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    # Dates
    issued_at = Column(DateTime(timezone=True), nullable=False)
    due_at = Column(DateTime(timezone=True), nullable=False)
    paid_at = Column(DateTime(timezone=True))
    
    # Billing period
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    
    # Line items (JSON array of invoice line items)
    line_items = Column(JSON, default=[])
    
    # Payment
    payment_method = Column(String(50))
    payment_reference = Column(String(255))  # Transaction ID, check number, etc.
    
    # Stripe integration
    stripe_invoice_id = Column(String(255), unique=True, index=True)
    stripe_payment_intent_id = Column(String(255))
    
    # Files
    pdf_url = Column(String(500))
    
    # Internal notes
    internal_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contract = relationship("Contract", back_populates="invoices")
    
    @property
    def is_paid(self) -> bool:
        return self.status == InvoiceStatus.PAID
    
    @property
    def is_overdue(self) -> bool:
        return self.status == InvoiceStatus.OVERDUE or (
            self.status in [InvoiceStatus.SENT] and 
            self.due_at and 
            self.due_at < func.now()
        )
    
    @property
    def days_overdue(self) -> int:
        if not self.is_overdue or not self.due_at:
            return 0
        delta = func.now() - self.due_at
        return delta.days if delta.days > 0 else 0
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', status='{self.status}', total={self.total_amount})>"
"""
Green PM - Application Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum as SQLEnum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from src.core.database import Base

class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Application status
    status = Column(SQLEnum(ApplicationStatus), nullable=False, default=ApplicationStatus.DRAFT)
    
    # Personal information
    date_of_birth = Column(Date)
    ssn_last_four = Column(String(4))  # Encrypted
    phone_number = Column(String(20))
    emergency_contact_name = Column(String(255))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relationship = Column(String(100))
    
    # Current address
    current_address_line1 = Column(String(255))
    current_address_line2 = Column(String(255))
    current_address_city = Column(String(100))
    current_address_state = Column(String(50))
    current_address_zip = Column(String(20))
    current_landlord_name = Column(String(255))
    current_landlord_phone = Column(String(20))
    current_rent_amount = Column(Numeric(10, 2))
    move_in_date = Column(Date)
    reason_for_moving = Column(Text)
    
    # Employment information
    employer_name = Column(String(255))
    employer_address = Column(String(500))
    employer_phone = Column(String(20))
    job_title = Column(String(255))
    employment_start_date = Column(Date)
    monthly_income = Column(Numeric(10, 2))
    supervisor_name = Column(String(255))
    supervisor_phone = Column(String(20))
    
    # Additional income
    other_income_amount = Column(Numeric(10, 2))
    other_income_source = Column(String(255))
    
    # References
    reference1_name = Column(String(255))
    reference1_phone = Column(String(20))
    reference1_relationship = Column(String(100))
    reference2_name = Column(String(255))
    reference2_phone = Column(String(20))
    reference2_relationship = Column(String(100))
    
    # Pets
    has_pets = Column(Boolean, default=False)
    pet_details = Column(Text)  # JSON string with pet information
    
    # Vehicle information
    vehicle_make = Column(String(50))
    vehicle_model = Column(String(50))
    vehicle_year = Column(Integer)
    vehicle_license_plate = Column(String(20))
    
    # Background check consent
    background_check_consent = Column(Boolean, default=False)
    credit_check_consent = Column(Boolean, default=False)
    
    # Screening results
    credit_score = Column(Integer)
    background_check_status = Column(String(20))  # "pending", "clear", "issues"
    screening_report_url = Column(String(500))
    
    # Application fee
    application_fee_paid = Column(Boolean, default=False)
    application_fee_amount = Column(Numeric(10, 2))
    application_fee_payment_id = Column(Integer, ForeignKey("payments.id"))
    
    # Review notes
    landlord_notes = Column(Text)
    rejection_reason = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True))
    reviewed_at = Column(DateTime(timezone=True))
    
    # Relationships
    property = relationship("Property", back_populates="applications")
    applicant = relationship("User", back_populates="applications")
    documents = relationship("ApplicationDocument", back_populates="application", cascade="all, delete-orphan")
    application_fee_payment = relationship("Payment")
    
    @property
    def is_submitted(self) -> bool:
        return self.status != ApplicationStatus.DRAFT
    
    @property
    def is_approved(self) -> bool:
        return self.status == ApplicationStatus.APPROVED
    
    @property
    def monthly_income_to_rent_ratio(self) -> float:
        if not self.monthly_income or not self.property.rent_amount:
            return 0
        return float(self.monthly_income / self.property.rent_amount)
    
    def __repr__(self):
        return f"<Application(id={self.id}, property_id={self.property_id}, applicant_id={self.applicant_id}, status='{self.status}')>"

class ApplicationDocument(Base):
    __tablename__ = "application_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    
    # Document info
    document_type = Column(String(50), nullable=False)  # "id", "paystub", "bank_statement", etc.
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    url = Column(String(500), nullable=False)
    
    # Metadata
    description = Column(Text)
    is_required = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # File info
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    application = relationship("Application", back_populates="documents")
    
    def __repr__(self):
        return f"<ApplicationDocument(id={self.id}, application_id={self.application_id}, document_type='{self.document_type}')>"
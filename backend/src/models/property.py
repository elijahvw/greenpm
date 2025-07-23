"""
Green PM - Property Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from src.core.database import Base

class PropertyType(str, Enum):
    APARTMENT = "APARTMENT"
    HOUSE = "HOUSE"
    CONDO = "CONDO"
    TOWNHOUSE = "TOWNHOUSE"
    STUDIO = "STUDIO"
    DUPLEX = "DUPLEX"
    COMMERCIAL = "COMMERCIAL"

class PropertyStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"
    DRAFT = "DRAFT"
    ARCHIVED = "ARCHIVED"

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic info
    title = Column(String(255), nullable=False)
    description = Column(Text)
    property_type = Column(SQLEnum(PropertyType), nullable=False)
    status = Column(SQLEnum(PropertyStatus), nullable=False, default=PropertyStatus.DRAFT)
    
    # Address
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255))
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(20), nullable=False)
    country = Column(String(50), default="US")
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    
    # Property details
    bedrooms = Column(Integer, default=0)
    bathrooms = Column(Numeric(3, 1), default=0)
    square_feet = Column(Integer)
    lot_size = Column(Integer)
    year_built = Column(Integer)
    
    # Rental info
    rent_amount = Column(Numeric(10, 2), nullable=False)
    security_deposit = Column(Numeric(10, 2))
    pet_deposit = Column(Numeric(10, 2))
    application_fee = Column(Numeric(10, 2))
    
    # Policies
    pets_allowed = Column(Boolean, default=False)
    smoking_allowed = Column(Boolean, default=False)
    furnished = Column(Boolean, default=False)
    utilities_included = Column(Text)  # JSON string
    
    # Availability
    available_date = Column(DateTime(timezone=True))
    lease_term_months = Column(Integer, default=12)
    
    # SEO and marketing
    slug = Column(String(255), unique=True, index=True)
    featured = Column(Boolean, default=False)
    virtual_tour_url = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="owned_properties", foreign_keys=[owner_id])
    images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")
    amenities = relationship("PropertyAmenity", back_populates="property", cascade="all, delete-orphan")
    leases = relationship("Lease", back_populates="property_rel")
    applications = relationship("Application", back_populates="property")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="property")
    
    @property
    def full_address(self) -> str:
        address = self.address_line1
        if self.address_line2:
            address += f", {self.address_line2}"
        address += f", {self.city}, {self.state} {self.zip_code}"
        return address
    
    @property
    def is_available(self) -> bool:
        return self.status == PropertyStatus.AVAILABLE
    
    def __repr__(self):
        return f"<Property(id={self.id}, title='{self.title}', status='{self.status}')>"

class PropertyImage(Base):
    __tablename__ = "property_images"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    
    # Image info
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    
    # Metadata
    caption = Column(String(255))
    alt_text = Column(String(255))
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    
    # File info
    file_size = Column(Integer)
    mime_type = Column(String(100))
    width = Column(Integer)
    height = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    property = relationship("Property", back_populates="images")
    
    def __repr__(self):
        return f"<PropertyImage(id={self.id}, property_id={self.property_id}, filename='{self.filename}')>"

class PropertyAmenity(Base):
    __tablename__ = "property_amenities"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    
    # Amenity info
    name = Column(String(100), nullable=False)
    category = Column(String(50))  # e.g., "kitchen", "bathroom", "building", "outdoor"
    icon = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    property = relationship("Property", back_populates="amenities")
    
    def __repr__(self):
        return f"<PropertyAmenity(id={self.id}, property_id={self.property_id}, name='{self.name}')>"
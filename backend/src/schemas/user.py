"""
Green PM - User Schemas
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from src.models.user import UserRole, UserStatus

class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.TENANT

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    notification_email: Optional[bool] = None
    notification_sms: Optional[bool] = None
    notification_push: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    uuid: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str]
    role: UserRole
    status: UserStatus
    avatar_url: Optional[str]
    bio: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    country: Optional[str]
    email_verified: bool
    phone_verified: bool
    identity_verified: bool
    two_factor_enabled: bool
    notification_email: bool
    notification_sms: bool
    notification_push: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    page: int
    size: int
    pages: int

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = "US"

class UserPreferencesUpdate(BaseModel):
    notification_email: Optional[bool] = None
    notification_sms: Optional[bool] = None
    notification_push: Optional[bool] = None

class UserStatusUpdate(BaseModel):
    status: UserStatus

class UserRoleUpdate(BaseModel):
    role: UserRole
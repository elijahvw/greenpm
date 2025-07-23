"""
Green PM - Working Authentication API
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import jwt
from datetime import datetime, timedelta
import uuid

from src.core.database_simple import db

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# JWT Settings
JWT_SECRET = "greenpm_secret_key_2024"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Pydantic Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str = "tenant"
    phone: Optional[str] = None
    address: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    phone: Optional[str] = None
    address: Optional[str] = None

def create_access_token(data: Dict[str, Any]) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token_data: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    """Get current user from token"""
    user_id = token_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    users = db.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
    if not users:
        raise HTTPException(status_code=401, detail="User not found")
    
    return users[0]

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """User login"""
    # Find user by email
    users = db.execute_query("SELECT * FROM users WHERE email = ?", (request.email,))
    if not users:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = users[0]
    
    # Verify password
    if not db.verify_password(request.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if user is active
    if not user['is_active']:
        raise HTTPException(status_code=401, detail="Account is deactivated")
    
    # Create access token
    token_data = {
        "user_id": user['id'],
        "email": user['email'],
        "role": user['role']
    }
    access_token = create_access_token(token_data)
    
    # Return token and user info
    user_info = {
        "id": user['id'],
        "email": user['email'],
        "first_name": user['first_name'],
        "last_name": user['last_name'],
        "role": user['role'],
        "is_active": bool(user['is_active']),
        "phone": user.get('phone'),
        "address": user.get('address')
    }
    
    return TokenResponse(
        access_token=access_token,
        user=user_info
    )

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """User registration"""
    # Check if user already exists
    existing_users = db.execute_query("SELECT * FROM users WHERE email = ?", (request.email,))
    if existing_users:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user_id = str(uuid.uuid4())
    password_hash = db.hash_password(request.password)
    
    db.execute_update("""
        INSERT INTO users (id, email, first_name, last_name, password_hash, role, phone, address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, request.email, request.first_name, request.last_name,
          password_hash, request.role, request.phone, request.address))
    
    # Create access token
    token_data = {
        "user_id": user_id,
        "email": request.email,
        "role": request.role
    }
    access_token = create_access_token(token_data)
    
    # Return token and user info
    user_info = {
        "id": user_id,
        "email": request.email,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "role": request.role,
        "is_active": True,
        "phone": request.phone,
        "address": request.address
    }
    
    return TokenResponse(
        access_token=access_token,
        user=user_info
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user['id'],
        email=current_user['email'],
        first_name=current_user['first_name'],
        last_name=current_user['last_name'],
        role=current_user['role'],
        is_active=bool(current_user['is_active']),
        phone=current_user.get('phone'),
        address=current_user.get('address')
    )

@router.post("/logout")
async def logout():
    """User logout"""
    return {"message": "Successfully logged out"}

# Dependency for role-based access
def require_roles(required_role: str):
    """Dependency factory for role-based access"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if current_user['role'] != required_role and current_user['role'] != 'admin':
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# Convenience dependencies
require_admin = require_roles('admin')
require_landlord = require_roles('landlord')
require_tenant = require_roles('tenant')
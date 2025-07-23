#!/usr/bin/env python3
"""
Simple standalone FastAPI app for testing login functionality
"""
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import asyncpg
import asyncio
from src.core.security import SecurityManager

app = FastAPI(title="Simple Green PM Login Test")
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    status: str

class LoginResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str

class PropertyResponse(BaseModel):
    id: int
    uuid: str
    title: str
    address_line1: str
    city: str
    state: str
    zip_code: str
    property_type: str
    status: str
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    square_feet: Optional[int]
    rent_amount: Optional[float]
    description: Optional[str]

@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Simple login endpoint"""
    try:
        # Connect to database
        conn = await asyncpg.connect('postgresql://greenpm_user:greenpm22@34.172.72.85:5432/greenpm_dev')
        
        # Get user
        user_row = await conn.fetchrow('''
            SELECT id, email, hashed_password, role, status, first_name, last_name
            FROM users 
            WHERE email = $1
        ''', request.email)
        
        if not user_row:
            await conn.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        security = SecurityManager()
        if not security.verify_password(request.password, user_row['hashed_password']):
            await conn.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if user_row['status'] != 'ACTIVE':
            await conn.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is not active"
            )
        
        # Generate access token
        access_token = security.create_access_token(
            data={
                "sub": str(user_row['id']),
                "email": user_row['email'],
                "role": user_row['role']
            }
        )
        
        # Update last login
        await conn.execute(
            'UPDATE users SET last_login = NOW() WHERE id = $1',
            user_row['id']
        )
        
        await conn.close()
        
        # Create response
        user_data = UserResponse(
            id=user_row['id'],
            email=user_row['email'],
            first_name=user_row['first_name'],
            last_name=user_row['last_name'],
            role=user_row['role'],
            status=user_row['status']
        )
        
        return LoginResponse(
            user=user_data,
            access_token=access_token,
            token_type="bearer"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        security_manager = SecurityManager()
        payload = security_manager.verify_token(credentials.credentials)
        user_id = int(payload.get("sub"))
        
        # Get user from database
        conn = await asyncpg.connect('postgresql://greenpm_user:greenpm22@34.172.72.85:5432/greenpm_dev')
        user_row = await conn.fetchrow(
            'SELECT id, email, first_name, last_name, role, status FROM users WHERE id = $1',
            user_id
        )
        await conn.close()
        
        if not user_row:
            raise HTTPException(status_code=401, detail="User not found")
        
        return {
            "id": user_row['id'],
            "email": user_row['email'],
            "first_name": user_row['first_name'],
            "last_name": user_row['last_name'],
            "role": user_row['role'],
            "status": user_row['status']
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/properties", response_model=List[PropertyResponse])
async def get_properties(current_user: dict = Depends(get_current_user)):
    """Get properties for current user"""
    try:
        conn = await asyncpg.connect('postgresql://greenpm_user:greenpm22@34.172.72.85:5432/greenpm_dev')
        
        if current_user['role'] == 'LANDLORD':
            # Landlords see their own properties
            properties = await conn.fetch('''
                SELECT id, uuid, title, address_line1, city, state, zip_code,
                       property_type, status, bedrooms, bathrooms, square_feet,
                       rent_amount, description
                FROM properties 
                WHERE owner_id = $1
                ORDER BY created_at DESC
            ''', current_user['id'])
        else:
            # Tenants see available properties
            properties = await conn.fetch('''
                SELECT id, uuid, title, address_line1, city, state, zip_code,
                       property_type, status, bedrooms, bathrooms, square_feet,
                       rent_amount, description
                FROM properties 
                WHERE status = 'AVAILABLE'
                ORDER BY created_at DESC
            ''')
        
        await conn.close()
        
        return [PropertyResponse(**dict(prop)) for prop in properties]
        
    except Exception as e:
        print(f"Properties error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch properties")

@app.get("/")
async def root():
    return {"message": "Simple Green PM Login Test API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
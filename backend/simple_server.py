#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="Green PM API - Simple")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@app.get("/")
async def root():
    return {"message": "Green PM API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/auth/login")
async def login(credentials: LoginRequest):
    """Simple login endpoint for testing"""
    
    # Mock user data - matching demo credentials from login page
    mock_users = {
        "admin@greenpm.com": {
            "id": "1",
            "email": "admin@greenpm.com",
            "first_name": "Master",
            "last_name": "Admin", 
            "role": "admin",
            "password": "GreenPM2024!"
        },
        "landlord@example.com": {
            "id": "2",
            "email": "landlord@example.com",
            "first_name": "Sample",
            "last_name": "Landlord", 
            "role": "landlord",
            "password": "landlord123"
        },
        "tenant@example.com": {
            "id": "3", 
            "email": "tenant@example.com",
            "first_name": "Sample",
            "last_name": "Tenant",
            "role": "tenant", 
            "password": "tenant123"
        }
    }
    
    # Check credentials
    user = mock_users.get(credentials.email)
    if not user or user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Return success response
    user_data = {k: v for k, v in user.items() if k != "password"}
    
    return LoginResponse(
        access_token="mock_token_" + user["id"],
        user=user_data
    )

@app.get("/api/v1/auth/me")
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Mock current user endpoint for token validation"""
    
    # Mock users matching login credentials
    mock_users = {
        "mock_token_1": {
            "id": "1",
            "email": "admin@greenpm.com",
            "first_name": "Master",
            "last_name": "Admin",
            "role": "admin",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "mock_token_2": {
            "id": "2",
            "email": "landlord@example.com",
            "first_name": "Sample",
            "last_name": "Landlord",
            "role": "landlord",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "mock_token_3": {
            "id": "3",
            "email": "tenant@example.com",
            "first_name": "Sample",
            "last_name": "Tenant",
            "role": "tenant",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
    }
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Extract token from "Bearer <token>" format
    try:
        token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    user = mock_users.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return user

@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats():
    """Mock dashboard stats endpoint"""
    return {
        "properties": {
            "total": 12,
            "available": 3,
            "occupied": 8,
            "maintenance": 1
        },
        "leases": {
            "active": 8,
            "expiring_soon": 2,
            "pending": 1,
            "expired": 5
        },
        "tenants": {
            "total": 8,
            "active": 8,
            "pending": 0
        },
        "financial": {
            "monthly_revenue": 24500.00,
            "security_deposits": 18750.00,
            "maintenance_costs": 3200.00,
            "occupancy_rate": 87.5
        },
        "recent_activities": [
            {
                "id": 1,
                "type": "payment",
                "description": "Rent payment received from John Doe",
                "date": "2024-07-20",
                "amount": 2500
            },
            {
                "id": 2,
                "type": "maintenance",
                "description": "AC repair completed at 123 Main St",
                "date": "2024-07-19"
            },
            {
                "id": 3,
                "type": "lease",
                "description": "New lease signed with Jane Smith",
                "date": "2024-07-18"
            }
        ]
    }

@app.get("/api/v1/properties")
async def get_properties():
    """Mock properties endpoint"""
    return [
        {
            "id": "1",
            "name": "Sunset Apartments Unit 1",
            "address": {
                "street": "123 Main Street",
                "city": "San Francisco",
                "state": "CA",
                "zipCode": "94105"
            },
            "type": "apartment",
            "bedrooms": 2,
            "bathrooms": 1,
            "squareFeet": 850,
            "rentAmount": 2500,
            "deposit": 3000,
            "status": "occupied",
            "amenities": ["Parking", "Laundry", "AC"],
            "description": "Beautiful 2BR/1BA apartment with city views",
            "images": [],
            "createdAt": "2024-01-15T00:00:00Z"
        },
        {
            "id": "2", 
            "name": "Oak Grove House",
            "address": {
                "street": "456 Oak Avenue",
                "city": "San Francisco", 
                "state": "CA",
                "zipCode": "94102"
            },
            "type": "house",
            "bedrooms": 3,
            "bathrooms": 2,
            "squareFeet": 1200,
            "rentAmount": 3500,
            "deposit": 4000,
            "status": "available",
            "amenities": ["Garden", "Garage", "Fireplace"],
            "description": "Charming 3BR/2BA house with backyard",
            "images": [],
            "createdAt": "2024-02-01T00:00:00Z"
        }
    ]

@app.get("/api/v1/leases") 
async def get_leases():
    """Mock leases endpoint"""
    return [
        {
            "id": "lease-1",
            "propertyId": "1",
            "property_id": "1", 
            "tenantId": "tenant-1",
            "tenant_id": "tenant-1",
            "tenant_name": "John Doe",
            "property_name": "Sunset Apartments Unit 1",
            "property_address": "123 Main Street, San Francisco, CA 94105",
            "startDate": "2024-01-01",
            "start_date": "2024-01-01",
            "endDate": "2024-12-31", 
            "end_date": "2024-12-31",
            "monthlyRent": 2500,
            "rent_amount": 2500,
            "securityDeposit": 3000,
            "status": "active",
            "leaseType": "fixed",
            "lease_type": "fixed"
        },
        {
            "id": "lease-2",
            "propertyId": "2",
            "property_id": "2",
            "tenantId": "tenant-2", 
            "tenant_id": "tenant-2",
            "tenant_name": "Jane Smith",
            "property_name": "Oak Grove House",
            "property_address": "456 Oak Avenue, San Francisco, CA 94102",
            "startDate": "2024-07-01",
            "start_date": "2024-07-01", 
            "endDate": "2025-06-30",
            "end_date": "2025-06-30",
            "monthlyRent": 3500,
            "rent_amount": 3500,
            "securityDeposit": 4000,
            "status": "pending",
            "leaseType": "fixed",
            "lease_type": "fixed"
        }
    ]

@app.get("/api/v1/security-deposits")
async def get_security_deposits():
    """Mock security deposits endpoint"""
    return [
        {
            "id": "1",
            "tenant_name": "John Doe",
            "property_address": "123 Main St, City, ST 12345",
            "amount": 1500,
            "dateReceived": "2024-01-15",
            "status": "held",
            "referenceNumber": "SD-001",
            "interestAccrued": 15.50,
            "deductions": [
                {"description": "Carpet cleaning", "amount": 150},
                {"description": "Paint touch-up", "amount": 75}
            ]
        },
        {
            "id": "2", 
            "tenant_name": "Jane Smith",
            "property_address": "456 Oak Ave, City, ST 12345",
            "amount": 2000,
            "dateReceived": "2024-02-01",
            "status": "held",
            "referenceNumber": "SD-002", 
            "interestAccrued": 12.25,
            "deductions": []
        }
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
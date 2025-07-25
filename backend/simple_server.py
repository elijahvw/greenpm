#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime

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

# In-memory storage for persistent changes during session
mock_data = {
    "users": {
        1: {
            "id": 1,
            "uuid": "00000000-0000-0000-0000-000000000001",
            "email": "admin@greenpm.com",
            "first_name": "Master",
            "last_name": "Admin",
            "role": "admin",
            "status": "ACTIVE",
            "phone": "555-0001",
            "avatar_url": None,
            "bio": None,
            "address_line1": "123 Admin St",
            "address_line2": None,
            "city": "Admin City",
            "state": "AC",
            "zip_code": "12345",
            "country": "USA",
            "email_verified": True,
            "phone_verified": True,
            "identity_verified": True,
            "two_factor_enabled": False,
            "notification_email": True,
            "notification_sms": True,
            "notification_push": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "last_login": "2024-01-01T00:00:00Z",
            "password": "GreenPM2024!"
        },
        2: {
            "id": 2,
            "uuid": "00000000-0000-0000-0000-000000000002",
            "email": "landlord@example.com",
            "first_name": "Sample",
            "last_name": "Landlord",
            "role": "landlord",
            "status": "ACTIVE",
            "phone": "555-0002",
            "avatar_url": None,
            "bio": None,
            "address_line1": "456 Landlord Ave",
            "address_line2": None,
            "city": "Property City",
            "state": "PC",
            "zip_code": "54321",
            "country": "USA",
            "email_verified": True,
            "phone_verified": True,
            "identity_verified": True,
            "two_factor_enabled": False,
            "notification_email": True,
            "notification_sms": True,
            "notification_push": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "last_login": "2024-01-01T00:00:00Z",
            "password": "landlord123"
        },
        3: {
            "id": 3,
            "uuid": "00000000-0000-0000-0000-000000000003",
            "email": "tenant@example.com",
            "first_name": "Sample",
            "last_name": "Tenant",
            "role": "tenant",
            "status": "ACTIVE",
            "phone": "555-0003",
            "avatar_url": None,
            "bio": None,
            "address_line1": "789 Tenant Blvd",
            "address_line2": "Apt 101",
            "city": "Rental City",
            "state": "RC",
            "zip_code": "98765",
            "country": "USA",
            "email_verified": True,
            "phone_verified": False,
            "identity_verified": False,
            "two_factor_enabled": False,
            "notification_email": True,
            "notification_sms": False,
            "notification_push": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "last_login": "2024-01-01T00:00:00Z",
            "password": "tenant123"
        }
    },
    "properties": {},
    "leases": {},
    "tenants": {},
    "maintenance_requests": {},
    "reports": {}
}

# Token to user ID mapping
token_to_user_id = {
    "mock_token_1": 1,
    "mock_token_2": 2,
    "mock_token_3": 3
}

@app.get("/")
async def root():
    return {"message": "Green PM API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/auth/login")
async def login(credentials: LoginRequest):
    """Simple login endpoint for testing"""
    
    # Find user by email in mock_data
    user = None
    for user_id, user_data in mock_data["users"].items():
        if user_data["email"] == credentials.email:
            user = user_data
            break
    
    if not user or user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Return success response
    user_data = {k: v for k, v in user.items() if k != "password"}
    
    return LoginResponse(
        access_token="mock_token_" + str(user["id"]),
        user=user_data
    )

@app.get("/api/v1/auth/me")
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Mock current user endpoint for token validation"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Extract token from "Bearer <token>" format
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    # Get user ID from token
    user_id = token_to_user_id.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user from mock_data
    user = mock_data["users"].get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Return user data (without password)
    return {k: v for k, v in user.items() if k != "password"}

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

# UPDATE ENDPOINTS

@app.put("/api/v1/properties/{property_id}")
async def update_property(property_id: int, request: dict):
    """Update property - with persistent storage"""
    # Store/update in mock_data
    if property_id not in mock_data["properties"]:
        # Create new property if it doesn't exist
        mock_data["properties"][property_id] = {
            "id": property_id,
            "created_at": datetime.now().isoformat() + "Z"
        }
    
    # Update property data
    property_data = mock_data["properties"][property_id]
    property_data.update(request)
    property_data["updated_at"] = datetime.now().isoformat() + "Z"
    
    return property_data

@app.put("/api/v1/leases/{lease_id}")
async def update_lease(lease_id: int, request: dict):
    """Update lease - with persistent storage"""
    # Store/update in mock_data
    if lease_id not in mock_data["leases"]:
        # Create new lease if it doesn't exist
        mock_data["leases"][lease_id] = {
            "id": lease_id,
            "created_at": datetime.now().isoformat() + "Z"
        }
    
    # Update lease data
    lease_data = mock_data["leases"][lease_id]
    lease_data.update(request)
    lease_data["updated_at"] = datetime.now().isoformat() + "Z"
    
    return lease_data

@app.put("/api/v1/applications/{application_id}")
async def update_application(application_id: int, request: dict):
    """Update application - mock implementation"""
    return {
        "id": application_id,
        **request,
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.put("/api/v1/maintenance/requests/{request_id}")
async def update_maintenance_request(request_id: int, request: dict):
    """Update maintenance request - mock implementation"""
    return {
        "id": request_id,
        **request,
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.put("/api/v1/admin/users/{user_id}")
async def update_user(user_id: int, request: dict):
    """Update user - mock implementation"""
    return {
        "id": user_id,
        **request,
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.put("/api/v1/users/profile")
async def update_profile(request: dict, authorization: Optional[str] = Header(None)):
    """Update user profile - actually persists changes in mock_data"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Extract token from "Bearer <token>" format
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    # Get user ID from token
    user_id = token_to_user_id.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user from mock_data
    user = mock_data["users"].get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Update user data with requested changes
    if "first_name" in request:
        user["first_name"] = request["first_name"]
    if "last_name" in request:
        user["last_name"] = request["last_name"]
    if "phone" in request:
        user["phone"] = request["phone"]
    if "address" in request:
        user["address_line1"] = request["address"]
    if "email" in request:
        user["email"] = request["email"]
    
    # Update timestamp
    user["updated_at"] = datetime.now().isoformat() + "Z"
    
    # Return updated user data (without password)
    return {k: v for k, v in user.items() if k != "password"}

# CREATE ENDPOINTS

@app.post("/api/v1/properties")
async def create_property(request: dict):
    """Create property - mock implementation"""
    import random
    return {
        "id": random.randint(1000, 9999),
        **request,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.post("/api/v1/leases")
async def create_lease(request: dict):
    """Create lease - mock implementation"""
    import random
    return {
        "id": random.randint(1000, 9999),
        **request,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.post("/api/v1/applications")
async def create_application(request: dict):
    """Create application - mock implementation"""
    import random
    return {
        "id": random.randint(1000, 9999),
        **request,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.post("/api/v1/maintenance/requests")
async def create_maintenance_request(request: dict):
    """Create maintenance request - mock implementation"""
    import random
    return {
        "id": random.randint(1000, 9999),
        **request,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.post("/api/v1/payments")
async def create_payment(request: dict):
    """Create payment - mock implementation"""
    import random
    return {
        "id": random.randint(1000, 9999),
        **request,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.post("/api/v1/tenants")
async def create_tenant(request: dict):
    """Create tenant - mock implementation"""
    import random
    return {
        "id": random.randint(1000, 9999),
        **request,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.post("/api/v1/reports")
async def create_report(request: dict):
    """Create report - mock implementation"""
    import random
    return {
        "id": random.randint(1000, 9999),
        **request,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.post("/api/v1/report-templates")
async def create_report_template(request: dict):
    """Create report template - mock implementation"""
    import random
    return {
        "id": random.randint(1000, 9999),
        **request,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

# GET ENDPOINTS FOR ADDITIONAL RESOURCES

@app.get("/api/v1/tenants")
async def get_tenants():
    """Mock tenants endpoint"""
    return [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "555-0001",
            "address": "123 Main St",
            "lease_id": 1,
            "status": "active"
        },
        {
            "id": 2,
            "name": "Jane Smith", 
            "email": "jane.smith@email.com",
            "phone": "555-0002",
            "address": "456 Oak Ave",
            "lease_id": 2,
            "status": "active"
        }
    ]

@app.get("/api/v1/tenants/{tenant_id}")
async def get_tenant(tenant_id: int):
    """Mock single tenant endpoint"""
    return {
        "id": tenant_id,
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "555-0001",
        "address": "123 Main St",
        "lease_id": 1,
        "status": "active"
    }

@app.get("/api/v1/reports")
async def get_reports():
    """Mock reports endpoint"""
    return [
        {
            "id": 1,
            "name": "Monthly Financial Report",
            "type": "financial",
            "status": "completed",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]

@app.get("/api/v1/report-templates")
async def get_report_templates():
    """Mock report templates endpoint"""
    return [
        {
            "id": 1,
            "name": "Monthly Financial Template",
            "type": "financial",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]

@app.get("/api/v1/analytics/dashboard")
async def get_analytics_dashboard():
    """Mock analytics dashboard endpoint"""
    return {
        "total_revenue": 15000,
        "occupancy_rate": 95.5,
        "maintenance_requests": 3,
        "properties_count": 5
    }

# DELETE ENDPOINTS

@app.delete("/api/v1/properties/{property_id}")
async def delete_property(property_id: int):
    """Delete property - mock implementation"""
    return {"message": "Property deleted successfully"}

@app.delete("/api/v1/admin/users/{user_id}")
async def delete_user(user_id: int):
    """Delete user - mock implementation"""
    return {"message": "User deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
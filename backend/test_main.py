"""
Minimal Green PM API for testing property and lease edit functionality
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, Union
import os

app = FastAPI(title="Green PM Test API", version="1.0.0")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "Green PM Test API is running"
    }

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
users = {
    "admin@greenpm.com": {
        "id": "1",
        "email": "admin@greenpm.com",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "is_active": True
    },
    "landlord@example.com": {
        "id": "2",
        "email": "landlord@example.com",
        "first_name": "Landlord",
        "last_name": "User",
        "role": "landlord",
        "is_active": True
    },
    "tenant@example.com": {
        "id": "3",
        "email": "tenant@example.com",
        "first_name": "Tenant",
        "last_name": "User",
        "role": "tenant",
        "is_active": True
    }
}

properties = [
    {
        "id": "1",
        "name": "Test Property 1",
        "address": "123 Main Street, Springfield, IL 62701",
        "type": "apartment",
        "bedrooms": 2,
        "bathrooms": 1,
        "squareFeet": 1200,
        "description": "Beautiful 2-bedroom apartment",
        "status": "available",
        "rentAmount": 1500
    },
    {
        "id": "2", 
        "name": "Test Property 2",
        "address": "456 Oak Avenue, Chicago, IL 60601",
        "type": "house",
        "bedrooms": 3,
        "bathrooms": 2.5,
        "squareFeet": 1800,
        "description": "Spacious family house",
        "status": "occupied",
        "rentAmount": 2200
    }
]

leases = [
    {
        "id": "1",
        "propertyId": "1",
        "property_id": "1",
        "tenantId": "1",
        "tenant_id": "1", 
        "startDate": "2024-01-01",
        "start_date": "2024-01-01",
        "endDate": "2024-12-31",
        "end_date": "2024-12-31",
        "monthlyRent": 1500,
        "rent_amount": 1500,
        "securityDeposit": 1500,
        "security_deposit": 1500,
        "lateFeePenalty": 50,
        "late_fee_penalty": 50,
        "gracePeriodDays": 5,
        "grace_period_days": 5,
        "leaseType": "fixed",
        "lease_type": "fixed",
        "status": "active",
        "renewalOption": True,
        "renewal_option": True,
        "notes": "Standard lease agreement",
        "specialTerms": "No smoking allowed",
        "property_name": "Test Property 1",
        "property_address": "123 Main Street, Springfield, IL 62701",
        "tenant_name": "John Doe",
        "tenant_email": "john.doe@email.com",
        "tenant_phone": "(555) 123-4567"
    },
    {
        "id": "2",
        "propertyId": "2",
        "property_id": "2", 
        "tenantId": "2",
        "tenant_id": "2",
        "startDate": "2024-02-01",
        "start_date": "2024-02-01",
        "endDate": "2025-01-31",
        "end_date": "2025-01-31",
        "monthlyRent": 2200,
        "rent_amount": 2200,
        "securityDeposit": 2200,
        "security_deposit": 2200,
        "lateFeePenalty": 75,
        "late_fee_penalty": 75,
        "gracePeriodDays": 3,
        "grace_period_days": 3,
        "leaseType": "fixed",
        "lease_type": "fixed",
        "status": "active",
        "renewalOption": True,
        "renewal_option": True,
        "notes": "Family-friendly lease",
        "specialTerms": "Pets allowed with deposit",
        "property_name": "Test Property 2",
        "property_address": "456 Oak Avenue, Chicago, IL 60601",
        "tenant_name": "Jane Smith",
        "tenant_email": "jane.smith@email.com",
        "tenant_phone": "(555) 987-6543"
    }
]

# Sample tenant data
tenants = [
    {
        "id": "1",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@email.com",
        "phone": "(555) 123-4567",
        "dateOfBirth": "1990-05-15",
        "emergencyContact": {
            "name": "Jane Doe",
            "phone": "(555) 123-4568",
            "relationship": "Spouse"
        },
        "employmentInfo": {
            "employer": "ABC Corporation",
            "position": "Software Engineer",
            "monthlyIncome": 5000,
            "yearsEmployed": 3
        },
        "status": "active",
        "applicationDate": "2023-12-01",
        "moveInDate": "2024-01-01",
        "notes": "Excellent tenant, always pays on time"
    },
    {
        "id": "2", 
        "firstName": "Jane",
        "lastName": "Smith",
        "email": "jane.smith@email.com",
        "phone": "(555) 987-6543",
        "dateOfBirth": "1985-08-22",
        "emergencyContact": {
            "name": "Robert Smith",
            "phone": "(555) 987-6544",
            "relationship": "Brother"
        },
        "employmentInfo": {
            "employer": "XYZ Marketing",
            "position": "Marketing Manager", 
            "monthlyIncome": 6500,
            "yearsEmployed": 5
        },
        "status": "active",
        "applicationDate": "2023-12-15",
        "moveInDate": "2024-02-01",
        "notes": "Professional tenant with excellent references"
    },
    {
        "id": "3",
        "firstName": "Michael",
        "lastName": "Johnson", 
        "email": "michael.johnson@email.com",
        "phone": "(555) 456-7890",
        "dateOfBirth": "1992-03-10",
        "emergencyContact": {
            "name": "Sarah Johnson",
            "phone": "(555) 456-7891",
            "relationship": "Sister"
        },
        "employmentInfo": {
            "employer": "Tech Solutions Inc",
            "position": "Data Analyst",
            "monthlyIncome": 4200,
            "yearsEmployed": 2
        },
        "status": "prospective",
        "applicationDate": "2024-11-01",
        "notes": "New applicant, background check in progress"
    }
]

# Sample security deposit data
security_deposits = [
    {
        "id": "1",
        "leaseId": "1",
        "tenantId": "1",
        "propertyId": "1", 
        "amount": 1500.00,
        "dateReceived": "2023-12-15",
        "bankAccount": "Security Deposits Account - *1234",
        "paymentMethod": "bank_transfer",
        "referenceNumber": "DEP-2023-001",
        "interestRate": 2.5,
        "interestAccrued": 15.25,
        "status": "held",
        "deductions": [],
        "totalDeductions": 0,
        "notes": "Standard security deposit for lease #1",
        "stateRequirements": {
            "interestRequired": True,
            "maxHoldDays": 21,
            "inspectionRequired": True
        },
        # Related data for frontend display
        "tenant_name": "John Doe",
        "property_address": "123 Main Street, Springfield, IL 62701",
        "lease_start_date": "2024-01-01",
        "lease_end_date": "2024-12-31"
    },
    {
        "id": "2",
        "leaseId": "2", 
        "tenantId": "2",
        "propertyId": "2",
        "amount": 2200.00,
        "dateReceived": "2024-01-15",
        "bankAccount": "Security Deposits Account - *1234", 
        "paymentMethod": "cashiers_check",
        "referenceNumber": "DEP-2024-001",
        "interestRate": 2.5,
        "interestAccrued": 8.50,
        "status": "held",
        "deductions": [],
        "totalDeductions": 0,
        "notes": "Security deposit received via cashier's check",
        "stateRequirements": {
            "interestRequired": True,
            "maxHoldDays": 21,
            "inspectionRequired": True
        },
        # Related data for frontend display
        "tenant_name": "Jane Smith",
        "property_address": "456 Oak Avenue, Chicago, IL 60601",
        "lease_start_date": "2024-02-01",
        "lease_end_date": "2025-01-31"
    }
]

# Pydantic models
class LoginRequest(BaseModel):
    email: str
    password: str

class AddressObject(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = None
    country: Optional[str] = None

class PropertyUpdate(BaseModel):
    id: str
    name: Optional[str] = None
    address: Optional[Union[str, AddressObject]] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = None
    country: Optional[str] = None
    type: Optional[str] = None  # Changed from propertyType
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    squareFeet: Optional[int] = None  # Changed from squareFootage
    yearBuilt: Optional[int] = None
    description: Optional[str] = None
    amenities: Optional[list] = None  # Changed to list
    notes: Optional[str] = None
    rentAmount: Optional[float] = None  # Changed from monthlyRent
    status: Optional[str] = None

class LeaseUpdate(BaseModel):
    id: str
    monthlyRent: Optional[float] = None
    securityDeposit: Optional[float] = None
    lateFeePenalty: Optional[float] = None
    gracePeriodDays: Optional[int] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    leaseType: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    specialTerms: Optional[str] = None

# Valid password combinations for demo
valid_credentials = {
    "admin@greenpm.com": "GreenPM2024!",
    "landlord@example.com": "landlord123", 
    "tenant@example.com": "tenant123"
}

# Auth endpoints
@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
    print(f"🔐 Login attempt - Email: {request.email}, Password: {request.password}")
    print(f"🔐 Available users: {list(users.keys())}")
    
    # Check if user exists and password matches
    if request.email in users and request.email in valid_credentials:
        if valid_credentials[request.email] == request.password:
            user = users[request.email]
            print(f"✅ Login successful for: {request.email}")
            return {
                "access_token": "test-token-123",
                "token_type": "bearer",
                "user": user
            }
        else:
            print(f"❌ Login failed - wrong password for: {request.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
    
    print(f"❌ Login failed - user not found: {request.email}")
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/v1/auth/me")
async def get_current_user():
    # For testing, return the landlord user
    return users["landlord@example.com"]

# Property endpoints
@app.get("/api/v1/properties")
async def get_properties():
    return properties

@app.post("/api/v1/properties")
async def create_property(property_data: dict):
    print(f"🏠 API - Creating property with data:", property_data)
    
    new_property = {
        "id": str(len(properties) + 1),
        "status": "available",  # Default status
        **property_data
    }
    
    properties.append(new_property)
    print(f"✅ API - Property created:", new_property)
    return new_property

@app.get("/api/v1/properties/{property_id}")
async def get_property(property_id: str):
    for prop in properties:
        if prop["id"] == property_id:
            return prop
    raise HTTPException(status_code=404, detail="Property not found")

@app.put("/api/v1/properties/{property_id}")
async def update_property(property_id: str, property_data: PropertyUpdate):
    print(f"🏠 API - Updating property {property_id} with data:", property_data.dict())
    
    for i, prop in enumerate(properties):
        if prop["id"] == property_id:
            # Update only provided fields
            update_dict = property_data.dict(exclude_unset=True)
            for key, value in update_dict.items():
                if key != "id" and value is not None:
                    if key == "address":
                        # Handle address - can be string or object
                        if isinstance(value, dict):
                            # If it's an address object, convert back to string format for storage
                            address_parts = []
                            if value.get("street"):
                                address_parts.append(value["street"])
                            if value.get("city"):
                                address_parts.append(value["city"])
                            if value.get("state") and value.get("zipCode"):
                                address_parts.append(f"{value['state']} {value['zipCode']}")
                            elif value.get("state"):
                                address_parts.append(value["state"])
                            prop["address"] = ", ".join(address_parts)
                        else:
                            prop["address"] = value
                    else:
                        # Direct field mapping
                        prop[key] = value
                        
            properties[i] = prop
            print(f"✅ API - Property updated:", prop)
            return prop
    
    raise HTTPException(status_code=404, detail="Property not found")

# Lease endpoints
@app.get("/api/v1/leases")
async def get_leases():
    return leases

@app.get("/api/v1/leases/{lease_id}")
async def get_lease(lease_id: str):
    for lease in leases:
        if lease["id"] == lease_id:
            return lease
    raise HTTPException(status_code=404, detail="Lease not found")

@app.put("/api/v1/leases/{lease_id}")
async def update_lease(lease_id: str, lease_data: LeaseUpdate):
    print(f"📝 API - Updating lease {lease_id} with data:", lease_data.dict())
    
    for i, lease in enumerate(leases):
        if lease["id"] == lease_id:
            # Update only provided fields
            update_dict = lease_data.dict(exclude_unset=True)
            for key, value in update_dict.items():
                if key != "id" and value is not None:
                    lease[key] = value
                        
            leases[i] = lease
            print(f"✅ API - Lease updated:", lease)
            return lease
    
    raise HTTPException(status_code=404, detail="Lease not found")

@app.post("/api/v1/leases")
async def create_lease(lease_data: dict):
    print(f"📝 API - Creating lease with data:", lease_data)
    
    # Check if there's already an active lease for this property
    property_id = lease_data.get("propertyId")
    if property_id:
        existing_active_lease = next((
            lease for lease in leases 
            if (lease.get("propertyId") == property_id or lease.get("property_id") == property_id) 
            and lease.get("status", "active") == "active"
        ), None)
        
        if existing_active_lease:
            raise HTTPException(
                status_code=400, 
                detail=f"Property already has an active lease (Lease ID: {existing_active_lease['id']}). Only one active lease per property is allowed."
            )
    
    # Find property and tenant info for relationship data
    property_info = next((p for p in properties if p["id"] == lease_data.get("propertyId")), {})
    tenant_info = next((t for t in tenants if t["id"] == lease_data.get("tenantId")), {})
    
    new_lease = {
        "id": str(len(leases) + 1),
        **lease_data,
        # Add relationship data for frontend
        "property_id": lease_data.get("propertyId"),
        "tenant_id": lease_data.get("tenantId"),
        "property_name": property_info.get("name", "Unknown Property"),
        "property_address": property_info.get("address", "Unknown Address"),
        "tenant_name": f"{tenant_info.get('firstName', 'Unknown')} {tenant_info.get('lastName', 'Tenant')}",
        "tenant_email": tenant_info.get("email", ""),
        "tenant_phone": tenant_info.get("phone", ""),
        # Duplicate fields for compatibility
        "rent_amount": lease_data.get("monthlyRent", 0),
        "security_deposit": lease_data.get("securityDeposit", 0),
        "start_date": lease_data.get("startDate", ""),
        "end_date": lease_data.get("endDate", ""),
        "lease_type": lease_data.get("leaseType", "fixed"),
        "late_fee_penalty": lease_data.get("lateFeePenalty", 0),
        "grace_period_days": lease_data.get("gracePeriodDays", 5),
        "renewal_option": lease_data.get("renewalOption", False),
        "status": "active"  # New leases are active by default
    }
    
    leases.append(new_lease)
    print(f"✅ API - Lease created with relationships:", new_lease)
    return new_lease

@app.delete("/api/v1/leases/{lease_id}")
async def delete_lease(lease_id: str):
    print(f"📝 API - Deleting lease {lease_id}")
    
    for i, lease in enumerate(leases):
        if lease["id"] == lease_id:
            deleted_lease = leases.pop(i)
            print(f"✅ API - Lease deleted:", deleted_lease)
            return {"message": "Lease deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Lease not found")

@app.get("/api/v1/leases/expiring")
async def get_expiring_leases(days: int = 30):
    # For demo, return leases ending within the specified days
    from datetime import datetime, timedelta
    
    cutoff_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    expiring = [lease for lease in leases if lease["endDate"] <= cutoff_date]
    
    print(f"📝 API - Found {len(expiring)} expiring leases within {days} days")
    return expiring

# Tenant endpoints
@app.get("/api/v1/tenants")
async def get_tenants():
    return tenants

@app.get("/api/v1/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    for tenant in tenants:
        if tenant["id"] == tenant_id:
            return tenant
    raise HTTPException(status_code=404, detail="Tenant not found")

@app.post("/api/v1/tenants")
async def create_tenant(tenant_data: dict):
    print(f"👤 API - Creating tenant with data:", tenant_data)
    
    new_tenant = {
        "id": str(len(tenants) + 1),
        **tenant_data
    }
    tenants.append(new_tenant)
    print(f"✅ API - Tenant created:", new_tenant)
    return new_tenant

# Security Deposit endpoints
@app.get("/api/v1/security-deposits")
async def get_security_deposits():
    return security_deposits

@app.get("/api/v1/security-deposits/{deposit_id}")
async def get_security_deposit(deposit_id: str):
    for deposit in security_deposits:
        if deposit["id"] == deposit_id:
            return deposit
    raise HTTPException(status_code=404, detail="Security deposit not found")

@app.get("/api/v1/leases/{lease_id}/security-deposit")
async def get_lease_security_deposit(lease_id: str):
    for deposit in security_deposits:
        if deposit["leaseId"] == lease_id:
            return deposit
    raise HTTPException(status_code=404, detail="Security deposit not found for this lease")

@app.post("/api/v1/security-deposits")
async def create_security_deposit(deposit_data: dict):
    print(f"💰 API - Creating security deposit with data:", deposit_data)
    
    # Find property, tenant, and lease info for relationship data
    property_info = next((p for p in properties if p["id"] == deposit_data.get("propertyId")), {})
    tenant_info = next((t for t in tenants if t["id"] == deposit_data.get("tenantId")), {})
    lease_info = next((l for l in leases if l["id"] == deposit_data.get("leaseId")), {})
    
    new_deposit = {
        "id": str(len(security_deposits) + 1),
        "deductions": [],
        "totalDeductions": 0,
        "interestAccrued": 0,
        "status": "held",
        **deposit_data,
        # Add relationship data for frontend
        "tenant_name": f"{tenant_info.get('firstName', 'Unknown')} {tenant_info.get('lastName', 'Tenant')}",
        "property_address": property_info.get("address", "Unknown Address"),
        "lease_start_date": lease_info.get("startDate", deposit_data.get("dateReceived", "")),
        "lease_end_date": lease_info.get("endDate", ""),
    }
    
    security_deposits.append(new_deposit)
    print(f"✅ API - Security deposit created with relationships:", new_deposit)
    return new_deposit

@app.put("/api/v1/security-deposits/{deposit_id}")
async def update_security_deposit(deposit_id: str, deposit_data: dict):
    print(f"💰 API - Updating security deposit {deposit_id} with data:", deposit_data)
    
    for i, deposit in enumerate(security_deposits):
        if deposit["id"] == deposit_id:
            for key, value in deposit_data.items():
                if key != "id" and value is not None:
                    deposit[key] = value
            
            security_deposits[i] = deposit
            print(f"✅ API - Security deposit updated:", deposit)
            return deposit
    
    raise HTTPException(status_code=404, detail="Security deposit not found")

@app.post("/api/v1/security-deposits/{deposit_id}/deductions")
async def add_deduction(deposit_id: str, deduction_data: dict):
    print(f"💰 API - Adding deduction to deposit {deposit_id}:", deduction_data)
    
    for i, deposit in enumerate(security_deposits):
        if deposit["id"] == deposit_id:
            if "deductions" not in deposit:
                deposit["deductions"] = []
            
            new_deduction = {
                "id": str(len(deposit["deductions"]) + 1),
                "date": deduction_data.get("date"),
                "amount": deduction_data.get("amount", 0),
                "description": deduction_data.get("description", ""),
                "category": deduction_data.get("category", "damage"),
                "receipt": deduction_data.get("receipt", ""),
                "notes": deduction_data.get("notes", ""),
            }
            
            deposit["deductions"].append(new_deduction)
            
            # Calculate total deductions (but keep original status)
            total_deductions = sum(d["amount"] for d in deposit["deductions"])
            deposit["totalDeductions"] = total_deductions
            
            # Only calculate refund amount - don't change status automatically
            # Status should only change when refund is actually processed
            original_amount = deposit.get("amount", 0)
            deposit["refundAmount"] = max(0, original_amount - total_deductions)
            
            security_deposits[i] = deposit
            
            print(f"✅ API - Deduction added. Total deductions now: ${total_deductions}")
            print(f"📊 API - Updated deposit:", deposit)
            return deposit
    
    raise HTTPException(status_code=404, detail="Security deposit not found")

@app.post("/api/v1/security-deposits/{deposit_id}/refund")
async def process_refund(deposit_id: str, refund_data: dict):
    print(f"💰 API - Processing refund for deposit {deposit_id}:", refund_data)
    
    for i, deposit in enumerate(security_deposits):
        if deposit["id"] == deposit_id:
            total_deductions = deposit.get("totalDeductions", 0) or sum(d.get("amount", 0) for d in deposit.get("deductions", []))
            original_amount = deposit["amount"]
            interest_accrued = deposit.get("interestAccrued", 0)
            
            # Calculate refund amount (original + interest - deductions)
            refund_amount = max(0, original_amount + interest_accrued - total_deductions)
            
            deposit.update({
                "status": "refunded",
                "refundDate": refund_data.get("refundDate"),
                "refundAmount": refund_amount,
                "refundMethod": refund_data.get("refundMethod", "bank_transfer"),
                "refundNotes": refund_data.get("refundNotes", ""),
                "totalDeductions": total_deductions  # Ensure this is set
            })
            
            security_deposits[i] = deposit
            print(f"✅ API - Refund processed. Amount: ${refund_amount}, Total deductions: ${total_deductions}")
            print(f"📊 API - Final deposit state:", deposit)
            return deposit
    
    raise HTTPException(status_code=404, detail="Security deposit not found")

# Dashboard endpoints
@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats():
    return {
        "total_properties": len(properties),
        "total_leases": len(leases),
        "occupied_properties": len([p for p in properties if p["status"] == "occupied"]),
        "available_properties": len([p for p in properties if p["status"] == "available"]),
        "total_rent": sum(lease["monthlyRent"] for lease in leases),
        "recent_activity": [
            {"type": "lease_signed", "description": "New lease signed for Test Property 1"},
            {"type": "payment_received", "description": "Rent payment received from John Doe"}
        ]
    }

@app.get("/api/v1/dashboard/activity")
async def get_recent_activity():
    return [
        {"type": "lease_signed", "description": "New lease signed for Test Property 1", "date": "2024-01-01"},
        {"type": "payment_received", "description": "Rent payment received from John Doe", "date": "2024-01-02"}
    ]

# Health check
@app.get("/")
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Green PM Test API is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
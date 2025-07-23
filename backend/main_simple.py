#!/usr/bin/env python3
"""
Green PM - Simple Demo Backend with SQLite
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import hashlib
import uuid
from datetime import datetime, timedelta
import sqlite3
from src.core.database_simple import SimpleDatabase

app = FastAPI(title="Green PM API - Demo")

# Initialize simple database
db = SimpleDatabase()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class PropertyCreate(BaseModel):
    name: str
    address: str
    type: str
    bedrooms: int
    bathrooms: int
    square_feet: int
    rent_amount: float
    description: Optional[str] = None

class PropertyResponse(BaseModel):
    id: str
    name: str
    address: str
    type: str
    bedrooms: int
    bathrooms: int
    square_feet: int
    rent_amount: float
    description: Optional[str]
    owner_id: str
    created_at: str

# Auth helper functions
def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user from token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Extract token from "Bearer <token>" format
    try:
        token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    # Simple token validation (in real app, use JWT)
    # For demo, token format: mock_token_<user_id>
    if not token.startswith("mock_token_"):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user from database
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (token.replace("mock_token_", ""),))
        user_row = cursor.fetchone()
        
        if not user_row:
            raise HTTPException(status_code=401, detail="User not found")
        
        return dict(user_row)

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Green PM API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/auth/login")
async def login(credentials: LoginRequest):
    """Login endpoint"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (credentials.email,))
        user_row = cursor.fetchone()
        
        if not user_row:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = dict(user_row)
        
        # Verify password
        if not db.verify_password(credentials.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create token (simple approach for demo)
        token = f"mock_token_{user['id']}"
        
        # Return user data without password
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return LoginResponse(
            access_token=token,
            user=user_data
        )

@app.get("/api/v1/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return {k: v for k, v in current_user.items() if k != 'password_hash'}

@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get dashboard statistics"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get property stats for current user
        if current_user['role'] == 'landlord':
            cursor.execute("SELECT COUNT(*) FROM properties WHERE owner_id = ?", (current_user['id'],))
        else:
            cursor.execute("SELECT COUNT(*) FROM properties")
        total_properties = cursor.fetchone()[0]
        
        # Get lease stats
        cursor.execute("SELECT COUNT(*) FROM leases WHERE status = 'active'")
        active_leases = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM leases WHERE status = 'pending'")
        pending_leases = cursor.fetchone()[0]
        
        # Get tenant stats
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'tenant'")
        total_tenants = cursor.fetchone()[0]
        
        # Get recent payments for revenue
        cursor.execute("""
            SELECT SUM(amount) FROM payments 
            WHERE payment_date >= date('now', '-30 days')
        """)
        monthly_revenue = cursor.fetchone()[0] or 0
        
        return {
            "properties": {
                "total": total_properties,
                "available": max(0, total_properties - active_leases),
                "occupied": active_leases,
                "maintenance": 0
            },
            "leases": {
                "active": active_leases,
                "expiring_soon": 0,
                "pending": pending_leases,
                "expired": 0
            },
            "tenants": {
                "total": total_tenants,
                "active": total_tenants,
                "pending": 0
            },
            "financial": {
                "monthly_revenue": monthly_revenue,
                "security_deposits": active_leases * 1500,  # Estimate
                "maintenance_costs": 500,
                "occupancy_rate": (active_leases / max(1, total_properties)) * 100
            },
            "recent_activities": [
                {
                    "id": 1,
                    "type": "payment",
                    "description": "Rent payment received",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "amount": 1500
                }
            ]
        }

@app.get("/api/v1/properties")
async def get_properties(current_user: dict = Depends(get_current_user)):
    """Get properties for current user"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        if current_user['role'] == 'landlord':
            cursor.execute("""
                SELECT p.*, u.first_name || ' ' || u.last_name as owner_name
                FROM properties p
                JOIN users u ON p.owner_id = u.id
                WHERE p.owner_id = ? AND p.is_active = 1
                ORDER BY p.created_at DESC
            """, (current_user['id'],))
        else:
            cursor.execute("""
                SELECT p.*, u.first_name || ' ' || u.last_name as owner_name
                FROM properties p
                JOIN users u ON p.owner_id = u.id
                WHERE p.is_active = 1
                ORDER BY p.created_at DESC
            """)
        
        properties = []
        for row in cursor.fetchall():
            prop_dict = dict(row)
            # Convert to expected format
            prop_dict['rentAmount'] = prop_dict['rent_amount']
            prop_dict['squareFeet'] = prop_dict['square_feet']
            prop_dict['createdAt'] = prop_dict['created_at']
            prop_dict['status'] = 'available'  # Default status
            prop_dict['amenities'] = []  # Empty for now
            prop_dict['images'] = []  # Empty for now
            properties.append(prop_dict)
        
        return properties

@app.post("/api/v1/properties")
async def create_property(property_data: PropertyCreate, current_user: dict = Depends(get_current_user)):
    """Create a new property"""
    if current_user['role'] != 'landlord' and current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Access denied")
    
    property_id = str(uuid.uuid4())
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO properties (id, owner_id, name, address, type, bedrooms, bathrooms, 
                                  square_feet, rent_amount, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (property_id, current_user['id'], property_data.name, property_data.address,
              property_data.type, property_data.bedrooms, property_data.bathrooms,
              property_data.square_feet, property_data.rent_amount, property_data.description))
        conn.commit()
        
        # Return the created property
        cursor.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
        row = cursor.fetchone()
        
        if row:
            prop_dict = dict(row)
            prop_dict['rentAmount'] = prop_dict['rent_amount']
            prop_dict['squareFeet'] = prop_dict['square_feet']
            prop_dict['createdAt'] = prop_dict['created_at']
            prop_dict['status'] = 'available'
            prop_dict['amenities'] = []
            prop_dict['images'] = []
            return prop_dict
        
        raise HTTPException(status_code=500, detail="Failed to create property")

@app.get("/api/v1/leases")
async def get_leases(current_user: dict = Depends(get_current_user)):
    """Get leases"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        if current_user['role'] == 'landlord':
            cursor.execute("""
                SELECT l.*, p.name as property_name, p.address as property_address,
                       t.first_name || ' ' || t.last_name as tenant_name
                FROM leases l
                JOIN properties p ON l.property_id = p.id
                JOIN users t ON l.tenant_id = t.id
                WHERE p.owner_id = ?
                ORDER BY l.created_at DESC
            """, (current_user['id'],))
        elif current_user['role'] == 'tenant':
            cursor.execute("""
                SELECT l.*, p.name as property_name, p.address as property_address,
                       t.first_name || ' ' || t.last_name as tenant_name
                FROM leases l
                JOIN properties p ON l.property_id = p.id
                JOIN users t ON l.tenant_id = t.id
                WHERE l.tenant_id = ?
                ORDER BY l.created_at DESC
            """, (current_user['id'],))
        else:
            cursor.execute("""
                SELECT l.*, p.name as property_name, p.address as property_address,
                       t.first_name || ' ' || t.last_name as tenant_name
                FROM leases l
                JOIN properties p ON l.property_id = p.id
                JOIN users t ON l.tenant_id = t.id
                ORDER BY l.created_at DESC
            """)
        
        leases = []
        for row in cursor.fetchall():
            lease_dict = dict(row)
            # Add both naming conventions for compatibility
            lease_dict['propertyId'] = lease_dict['property_id']
            lease_dict['tenantId'] = lease_dict['tenant_id']
            lease_dict['startDate'] = lease_dict['start_date']
            lease_dict['endDate'] = lease_dict['end_date']
            lease_dict['monthlyRent'] = lease_dict['rent_amount']
            lease_dict['leaseType'] = 'fixed'
            leases.append(lease_dict)
        
        return leases

@app.get("/api/v1/security-deposits")
async def get_security_deposits(current_user: dict = Depends(get_current_user)):
    """Get security deposits"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        if current_user['role'] == 'landlord':
            cursor.execute("""
                SELECT l.security_deposit as amount, l.start_date as dateReceived,
                       t.first_name || ' ' || t.last_name as tenant_name,
                       p.address as property_address, l.id as lease_id
                FROM leases l
                JOIN properties p ON l.property_id = p.id
                JOIN users t ON l.tenant_id = t.id
                WHERE p.owner_id = ? AND l.security_deposit > 0
                ORDER BY l.created_at DESC
            """, (current_user['id'],))
        else:
            cursor.execute("""
                SELECT l.security_deposit as amount, l.start_date as dateReceived,
                       t.first_name || ' ' || t.last_name as tenant_name,
                       p.address as property_address, l.id as lease_id
                FROM leases l
                JOIN properties p ON l.property_id = p.id
                JOIN users t ON l.tenant_id = t.id
                WHERE l.security_deposit > 0
                ORDER BY l.created_at DESC
            """)
        
        deposits = []
        for row in cursor.fetchall():
            deposit_dict = dict(row)
            deposit_dict['id'] = deposit_dict['lease_id']
            deposit_dict['status'] = 'held'
            deposit_dict['referenceNumber'] = f"SD-{deposit_dict['lease_id'][:8]}"
            deposit_dict['interestAccrued'] = deposit_dict['amount'] * 0.01  # 1% interest
            deposit_dict['deductions'] = []  # Empty for now
            deposits.append(deposit_dict)
        
        return deposits

@app.post("/api/v1/security-deposits/{deposit_id}/deductions")
async def add_deduction(deposit_id: str, deduction: dict, current_user: dict = Depends(get_current_user)):
    """Add deduction to security deposit (mock for now)"""
    # For demo purposes, just return success
    # In real app, this would update the database
    return {"message": "Deduction added successfully", "id": str(uuid.uuid4())}

@app.post("/api/v1/leases")
async def create_lease(lease_data: dict, current_user: dict = Depends(get_current_user)):
    """Create a new lease"""
    if current_user['role'] != 'landlord' and current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Access denied")
    
    lease_id = str(uuid.uuid4())
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO leases (id, property_id, tenant_id, start_date, end_date, 
                              rent_amount, security_deposit, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (lease_id, lease_data['propertyId'], lease_data['tenantId'], 
              lease_data['startDate'], lease_data['endDate'], lease_data['monthlyRent'],
              lease_data.get('securityDeposit', 0), lease_data.get('status', 'pending')))
        conn.commit()
        
        return {"id": lease_id, "message": "Lease created successfully"}

@app.put("/api/v1/leases/{lease_id}")
async def update_lease(lease_id: str, lease_data: dict, current_user: dict = Depends(get_current_user)):
    """Update a lease"""
    if current_user['role'] != 'landlord' and current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Access denied")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Build update query dynamically based on provided fields
        update_fields = []
        params = []
        
        field_mapping = {
            'monthlyRent': 'rent_amount',
            'securityDeposit': 'security_deposit',
            'startDate': 'start_date',
            'endDate': 'end_date',
            'status': 'status'
        }
        
        for key, value in lease_data.items():
            if key in field_mapping:
                update_fields.append(f"{field_mapping[key]} = ?")
                params.append(value)
        
        if update_fields:
            update_fields.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(lease_id)
            
            query = f"UPDATE leases SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        return {"message": "Lease updated successfully"}

@app.post("/api/v1/leases/{lease_id}/renew")
async def renew_lease(lease_id: str, renewal_data: dict, current_user: dict = Depends(get_current_user)):
    """Renew a lease"""
    if current_user['role'] != 'landlord' and current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Access denied")
    
    new_lease_id = str(uuid.uuid4())
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get original lease data
        cursor.execute("SELECT * FROM leases WHERE id = ?", (lease_id,))
        original_lease = cursor.fetchone()
        
        if not original_lease:
            raise HTTPException(status_code=404, detail="Lease not found")
        
        original_lease_dict = dict(original_lease)
        
        # Create new lease with renewal data
        cursor.execute("""
            INSERT INTO leases (id, property_id, tenant_id, start_date, end_date, 
                              rent_amount, security_deposit, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_lease_id, original_lease_dict['property_id'], original_lease_dict['tenant_id'],
              renewal_data['newStartDate'], renewal_data['newEndDate'], 
              renewal_data['newMonthlyRent'], renewal_data.get('newSecurityDeposit', original_lease_dict['security_deposit']),
              'pending'))
        
        # Mark old lease as expired
        cursor.execute("UPDATE leases SET status = 'expired' WHERE id = ?", (lease_id,))
        
        conn.commit()
        
        return {"id": new_lease_id, "message": "Lease renewed successfully"}

@app.post("/api/v1/leases/{lease_id}/terminate")
async def terminate_lease(lease_id: str, termination_data: dict, current_user: dict = Depends(get_current_user)):
    """Terminate a lease"""
    if current_user['role'] != 'landlord' and current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Access denied")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE leases SET status = 'terminated', updated_at = ? 
            WHERE id = ?
        """, (datetime.now().isoformat(), lease_id))
        conn.commit()
        
        return {"message": "Lease terminated successfully"}

@app.delete("/api/v1/properties/{property_id}")
async def delete_property(property_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a property"""
    if current_user['role'] != 'landlord' and current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Access denied")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE properties SET is_active = 0 WHERE id = ?", (property_id,))
        conn.commit()
        
        return {"message": "Property deleted successfully"}

@app.put("/api/v1/properties/{property_id}")
async def update_property(property_id: str, property_data: dict, current_user: dict = Depends(get_current_user)):
    """Update a property"""
    if current_user['role'] != 'landlord' and current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Access denied")
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Build update query based on provided fields
        update_fields = []
        params = []
        
        field_mapping = {
            'name': 'name',
            'address': 'address',
            'type': 'type',
            'bedrooms': 'bedrooms',
            'bathrooms': 'bathrooms',
            'squareFeet': 'square_feet',
            'rentAmount': 'rent_amount',
            'description': 'description'
        }
        
        for key, value in property_data.items():
            if key in field_mapping:
                update_fields.append(f"{field_mapping[key]} = ?")
                params.append(value)
        
        if update_fields:
            update_fields.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(property_id)
            
            query = f"UPDATE properties SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        return {"message": "Property updated successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
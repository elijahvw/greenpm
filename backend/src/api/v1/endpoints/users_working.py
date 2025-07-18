"""
Green PM - Working Users API (Admin Portal)
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from src.core.database_simple import db
from src.api.v1.endpoints.auth_working import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])

# Pydantic Models
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    phone: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    created_at: str
    updated_at: str
    
    # Additional admin fields
    property_count: Optional[int] = None
    lease_count: Optional[int] = None
    last_login: Optional[str] = None

class CompanyResponse(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    subscription_plan: str
    is_active: bool
    created_at: str
    updated_at: str
    
    # Additional fields
    user_count: Optional[int] = None
    property_count: Optional[int] = None
    total_revenue: Optional[float] = None

@router.get("/", response_model=List[UserResponse])
async def get_users(
    role: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Get all users (admin only)"""
    query = """
        SELECT u.*, c.name as company_name
        FROM users u
        LEFT JOIN companies c ON u.company_id = c.id
        WHERE 1=1
    """
    params = []
    
    if role:
        query += " AND u.role = ?"
        params.append(role)
    
    query += " ORDER BY u.created_at DESC"
    
    users = db.execute_query(query, tuple(params))
    
    # Add additional info for each user
    for user in users:
        # Property count for landlords
        if user['role'] == 'landlord':
            property_count = db.execute_query(
                "SELECT COUNT(*) as count FROM properties WHERE owner_id = ? AND is_active = 1",
                (user['id'],)
            )[0]['count']
            user['property_count'] = property_count
        else:
            user['property_count'] = 0
        
        # Lease count for tenants
        if user['role'] == 'tenant':
            lease_count = db.execute_query(
                "SELECT COUNT(*) as count FROM leases WHERE tenant_id = ? AND status = 'active'",
                (user['id'],)
            )[0]['count']
            user['lease_count'] = lease_count
        else:
            user['lease_count'] = 0
        
        # Mock last login (in real app, you'd track this)
        user['last_login'] = None
    
    return users

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Create a new user (admin only)"""
    # Check if user already exists
    existing_users = db.execute_query("SELECT * FROM users WHERE email = ?", (user_data.email,))
    if existing_users:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user_id = str(uuid.uuid4())
    password_hash = db.hash_password(user_data.password)
    
    db.execute_update("""
        INSERT INTO users (id, email, first_name, last_name, password_hash, role, phone, address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, user_data.email, user_data.first_name, user_data.last_name,
        password_hash, user_data.role, user_data.phone, user_data.address
    ))
    
    # Get the created user
    users = db.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
    if not users:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    user_dict = users[0]
    user_dict['property_count'] = 0
    user_dict['lease_count'] = 0
    user_dict['last_login'] = None
    
    return user_dict

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Get a specific user (admin only)"""
    users = db.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_dict = users[0]
    
    # Add additional info
    if user_dict['role'] == 'landlord':
        property_count = db.execute_query(
            "SELECT COUNT(*) as count FROM properties WHERE owner_id = ? AND is_active = 1",
            (user_id,)
        )[0]['count']
        user_dict['property_count'] = property_count
    else:
        user_dict['property_count'] = 0
    
    if user_dict['role'] == 'tenant':
        lease_count = db.execute_query(
            "SELECT COUNT(*) as count FROM leases WHERE tenant_id = ? AND status = 'active'",
            (user_id,)
        )[0]['count']
        user_dict['lease_count'] = lease_count
    else:
        user_dict['lease_count'] = 0
    
    user_dict['last_login'] = None
    
    return user_dict

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Update a user (admin only)"""
    # Get existing user
    users = db.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check for email conflicts
    if user_update.email:
        existing_users = db.execute_query(
            "SELECT * FROM users WHERE email = ? AND id != ?",
            (user_update.email, user_id)
        )
        if existing_users:
            raise HTTPException(status_code=400, detail="Email already in use")
    
    # Build update query
    update_fields = []
    update_values = []
    
    for field, value in user_update.dict(exclude_unset=True).items():
        if field == 'is_active':
            update_fields.append(f"{field} = ?")
            update_values.append(1 if value else 0)
        else:
            update_fields.append(f"{field} = ?")
            update_values.append(value)
    
    if not update_fields:
        return users[0]
    
    update_fields.append("updated_at = ?")
    update_values.append(datetime.utcnow().isoformat())
    update_values.append(user_id)
    
    query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
    db.execute_update(query, tuple(update_values))
    
    # Get updated user
    return await get_user(user_id, current_user)

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Delete a user (admin only)"""
    # Get existing user
    users = db.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_dict = users[0]
    
    # Prevent deleting admin users
    if user_dict['role'] == 'admin':
        raise HTTPException(status_code=400, detail="Cannot delete admin users")
    
    # Check for active leases or properties
    if user_dict['role'] == 'landlord':
        active_properties = db.execute_query(
            "SELECT COUNT(*) as count FROM properties WHERE owner_id = ? AND is_active = 1",
            (user_id,)
        )[0]['count']
        
        if active_properties > 0:
            raise HTTPException(status_code=400, detail="Cannot delete landlord with active properties")
    
    if user_dict['role'] == 'tenant':
        active_leases = db.execute_query(
            "SELECT COUNT(*) as count FROM leases WHERE tenant_id = ? AND status = 'active'",
            (user_id,)
        )[0]['count']
        
        if active_leases > 0:
            raise HTTPException(status_code=400, detail="Cannot delete tenant with active leases")
    
    # Soft delete
    db.execute_update("""
        UPDATE users 
        SET is_active = 0, updated_at = ?
        WHERE id = ?
    """, (datetime.utcnow().isoformat(), user_id))
    
    return {"message": "User deleted successfully"}

@router.get("/stats/overview")
async def get_user_stats(current_user: Dict[str, Any] = Depends(require_admin)):
    """Get user statistics overview (admin only)"""
    # Total users by role
    total_users = db.execute_query("SELECT COUNT(*) as count FROM users WHERE is_active = 1")[0]['count']
    admin_count = db.execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'admin' AND is_active = 1")[0]['count']
    landlord_count = db.execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'landlord' AND is_active = 1")[0]['count']
    tenant_count = db.execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'tenant' AND is_active = 1")[0]['count']
    
    # Total properties
    total_properties = db.execute_query("SELECT COUNT(*) as count FROM properties WHERE is_active = 1")[0]['count']
    
    # Total leases
    active_leases = db.execute_query("SELECT COUNT(*) as count FROM leases WHERE status = 'active'")[0]['count']
    
    # Total revenue (sum of all payments)
    total_revenue = db.execute_query("SELECT SUM(amount) as total FROM payments WHERE status = 'completed'")[0]['total'] or 0
    
    # Recent users (last 30 days)
    recent_users = db.execute_query("""
        SELECT COUNT(*) as count FROM users 
        WHERE created_at >= date('now', '-30 days') AND is_active = 1
    """)[0]['count']
    
    return {
        "total_users": total_users,
        "admin_count": admin_count,
        "landlord_count": landlord_count,
        "tenant_count": tenant_count,
        "total_properties": total_properties,
        "active_leases": active_leases,
        "total_revenue": total_revenue,
        "recent_users": recent_users
    }

@router.get("/companies/", response_model=List[CompanyResponse])
async def get_companies(current_user: Dict[str, Any] = Depends(require_admin)):
    """Get all companies (admin only)"""
    companies = db.execute_query("SELECT * FROM companies ORDER BY created_at DESC")
    
    # Add additional info for each company
    for company in companies:
        # User count
        user_count = db.execute_query(
            "SELECT COUNT(*) as count FROM users WHERE company_id = ? AND is_active = 1",
            (company['id'],)
        )[0]['count']
        company['user_count'] = user_count
        
        # Property count
        property_count = db.execute_query("""
            SELECT COUNT(*) as count FROM properties p
            JOIN users u ON p.owner_id = u.id
            WHERE u.company_id = ? AND p.is_active = 1
        """, (company['id'],))[0]['count']
        company['property_count'] = property_count
        
        # Total revenue
        total_revenue = db.execute_query("""
            SELECT SUM(pay.amount) as total FROM payments pay
            JOIN leases l ON pay.lease_id = l.id
            JOIN users u ON l.tenant_id = u.id
            WHERE u.company_id = ? AND pay.status = 'completed'
        """, (company['id'],))[0]['total'] or 0
        company['total_revenue'] = total_revenue
    
    return companies
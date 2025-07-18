"""
Green PM - Working Leases API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from src.core.database_simple import db
from src.api.v1.endpoints.auth_working import get_current_user, require_admin, require_landlord

router = APIRouter(prefix="/leases", tags=["leases"])

# Pydantic Models
class LeaseBase(BaseModel):
    property_id: str
    tenant_id: str
    start_date: str
    end_date: str
    rent_amount: float
    security_deposit: Optional[float] = None

class LeaseCreate(LeaseBase):
    pass

class LeaseUpdate(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    rent_amount: Optional[float] = None
    security_deposit: Optional[float] = None
    status: Optional[str] = None

class LeaseResponse(LeaseBase):
    id: str
    status: str
    created_at: str
    updated_at: str
    
    # Additional fields
    property_name: Optional[str] = None
    property_address: Optional[str] = None
    tenant_name: Optional[str] = None
    tenant_email: Optional[str] = None
    tenant_phone: Optional[str] = None
    landlord_name: Optional[str] = None
    landlord_email: Optional[str] = None
    total_payments: Optional[float] = None
    last_payment_date: Optional[str] = None

@router.get("/", response_model=List[LeaseResponse])
async def get_leases(
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get leases based on user role"""
    base_query = """
        SELECT l.*, 
               p.name as property_name, p.address as property_address,
               t.first_name || ' ' || t.last_name as tenant_name,
               t.email as tenant_email, t.phone as tenant_phone,
               ll.first_name || ' ' || ll.last_name as landlord_name,
               ll.email as landlord_email
        FROM leases l
        JOIN properties p ON l.property_id = p.id
        JOIN users t ON l.tenant_id = t.id
        JOIN users ll ON p.owner_id = ll.id
        WHERE 1=1
    """
    
    params = []
    
    if current_user['role'] == 'admin':
        # Admin can see all leases
        pass
    elif current_user['role'] == 'landlord':
        # Landlord can see leases for their properties
        base_query += " AND p.owner_id = ?"
        params.append(current_user['id'])
    elif current_user['role'] == 'tenant':
        # Tenant can see only their own leases
        base_query += " AND l.tenant_id = ?"
        params.append(current_user['id'])
    
    if status:
        base_query += " AND l.status = ?"
        params.append(status)
    
    base_query += " ORDER BY l.created_at DESC"
    
    leases = db.execute_query(base_query, tuple(params))
    
    # Add payment info for each lease
    for lease in leases:
        # Total payments
        total_payments = db.execute_query("""
            SELECT SUM(amount) as total FROM payments 
            WHERE lease_id = ? AND status = 'completed'
        """, (lease['id'],))[0]['total'] or 0
        lease['total_payments'] = total_payments
        
        # Last payment date
        last_payment = db.execute_query("""
            SELECT payment_date FROM payments 
            WHERE lease_id = ? AND status = 'completed'
            ORDER BY payment_date DESC LIMIT 1
        """, (lease['id'],))
        lease['last_payment_date'] = last_payment[0]['payment_date'] if last_payment else None
    
    return leases

@router.post("/", response_model=LeaseResponse)
async def create_lease(
    lease_data: LeaseCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new lease"""
    # Check if property exists
    properties = db.execute_query(
        "SELECT * FROM properties WHERE id = ? AND is_active = 1",
        (lease_data.property_id,)
    )
    if not properties:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_dict = properties[0]
    
    # Check permissions
    if current_user['role'] == 'landlord':
        if property_dict['owner_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="You don't own this property")
    elif current_user['role'] == 'tenant':
        raise HTTPException(status_code=403, detail="Tenants cannot create leases")
    
    # Check if tenant exists
    tenants = db.execute_query(
        "SELECT * FROM users WHERE id = ? AND role = 'tenant' AND is_active = 1",
        (lease_data.tenant_id,)
    )
    if not tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Check for overlapping leases
    overlapping_leases = db.execute_query("""
        SELECT COUNT(*) as count FROM leases 
        WHERE property_id = ? AND status = 'active'
        AND (
            (start_date <= ? AND end_date >= ?) OR
            (start_date <= ? AND end_date >= ?) OR
            (start_date >= ? AND end_date <= ?)
        )
    """, (
        lease_data.property_id,
        lease_data.start_date, lease_data.start_date,
        lease_data.end_date, lease_data.end_date,
        lease_data.start_date, lease_data.end_date
    ))[0]['count']
    
    if overlapping_leases > 0:
        raise HTTPException(status_code=400, detail="Property already has an active lease for this period")
    
    # Create lease
    lease_id = str(uuid.uuid4())
    
    db.execute_update("""
        INSERT INTO leases (id, property_id, tenant_id, start_date, end_date, rent_amount, security_deposit)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        lease_id, lease_data.property_id, lease_data.tenant_id,
        lease_data.start_date, lease_data.end_date, lease_data.rent_amount,
        lease_data.security_deposit
    ))
    
    # Get the created lease with all details
    leases = db.execute_query("""
        SELECT l.*, 
               p.name as property_name, p.address as property_address,
               t.first_name || ' ' || t.last_name as tenant_name,
               t.email as tenant_email, t.phone as tenant_phone,
               ll.first_name || ' ' || ll.last_name as landlord_name,
               ll.email as landlord_email
        FROM leases l
        JOIN properties p ON l.property_id = p.id
        JOIN users t ON l.tenant_id = t.id
        JOIN users ll ON p.owner_id = ll.id
        WHERE l.id = ?
    """, (lease_id,))
    
    if not leases:
        raise HTTPException(status_code=500, detail="Failed to create lease")
    
    lease_dict = leases[0]
    lease_dict['total_payments'] = 0
    lease_dict['last_payment_date'] = None
    
    return lease_dict

@router.get("/{lease_id}", response_model=LeaseResponse)
async def get_lease(
    lease_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific lease"""
    leases = db.execute_query("""
        SELECT l.*, 
               p.name as property_name, p.address as property_address,
               t.first_name || ' ' || t.last_name as tenant_name,
               t.email as tenant_email, t.phone as tenant_phone,
               ll.first_name || ' ' || ll.last_name as landlord_name,
               ll.email as landlord_email
        FROM leases l
        JOIN properties p ON l.property_id = p.id
        JOIN users t ON l.tenant_id = t.id
        JOIN users ll ON p.owner_id = ll.id
        WHERE l.id = ?
    """, (lease_id,))
    
    if not leases:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    lease_dict = leases[0]
    
    # Check permissions
    if current_user['role'] == 'tenant':
        if lease_dict['tenant_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user['role'] == 'landlord':
        # Check if landlord owns the property
        properties = db.execute_query(
            "SELECT * FROM properties WHERE id = ? AND owner_id = ?",
            (lease_dict['property_id'], current_user['id'])
        )
        if not properties:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Add payment info
    total_payments = db.execute_query("""
        SELECT SUM(amount) as total FROM payments 
        WHERE lease_id = ? AND status = 'completed'
    """, (lease_id,))[0]['total'] or 0
    lease_dict['total_payments'] = total_payments
    
    # Last payment date
    last_payment = db.execute_query("""
        SELECT payment_date FROM payments 
        WHERE lease_id = ? AND status = 'completed'
        ORDER BY payment_date DESC LIMIT 1
    """, (lease_id,))
    lease_dict['last_payment_date'] = last_payment[0]['payment_date'] if last_payment else None
    
    return lease_dict

@router.put("/{lease_id}", response_model=LeaseResponse)
async def update_lease(
    lease_id: str,
    lease_update: LeaseUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a lease"""
    # Get existing lease
    leases = db.execute_query("SELECT * FROM leases WHERE id = ?", (lease_id,))
    if not leases:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    lease_dict = leases[0]
    
    # Check permissions
    if current_user['role'] == 'tenant':
        raise HTTPException(status_code=403, detail="Tenants cannot update leases")
    elif current_user['role'] == 'landlord':
        # Check if landlord owns the property
        properties = db.execute_query(
            "SELECT * FROM properties WHERE id = ? AND owner_id = ?",
            (lease_dict['property_id'], current_user['id'])
        )
        if not properties:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Build update query
    update_fields = []
    update_values = []
    
    for field, value in lease_update.dict(exclude_unset=True).items():
        update_fields.append(f"{field} = ?")
        update_values.append(value)
    
    if not update_fields:
        return await get_lease(lease_id, current_user)
    
    update_fields.append("updated_at = ?")
    update_values.append(datetime.utcnow().isoformat())
    update_values.append(lease_id)
    
    query = f"UPDATE leases SET {', '.join(update_fields)} WHERE id = ?"
    db.execute_update(query, tuple(update_values))
    
    # Get updated lease
    return await get_lease(lease_id, current_user)

@router.delete("/{lease_id}")
async def delete_lease(
    lease_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a lease"""
    # Get existing lease
    leases = db.execute_query("SELECT * FROM leases WHERE id = ?", (lease_id,))
    if not leases:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    lease_dict = leases[0]
    
    # Check permissions
    if current_user['role'] == 'tenant':
        raise HTTPException(status_code=403, detail="Tenants cannot delete leases")
    elif current_user['role'] == 'landlord':
        # Check if landlord owns the property
        properties = db.execute_query(
            "SELECT * FROM properties WHERE id = ? AND owner_id = ?",
            (lease_dict['property_id'], current_user['id'])
        )
        if not properties:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if lease has payments
    payments = db.execute_query(
        "SELECT COUNT(*) as count FROM payments WHERE lease_id = ?",
        (lease_id,)
    )[0]['count']
    
    if payments > 0:
        raise HTTPException(status_code=400, detail="Cannot delete lease with existing payments")
    
    # Delete the lease
    db.execute_update("DELETE FROM leases WHERE id = ?", (lease_id,))
    
    return {"message": "Lease deleted successfully"}

@router.get("/{lease_id}/payments")
async def get_lease_payments(
    lease_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get payments for a lease"""
    # Check if lease exists and user has access
    await get_lease(lease_id, current_user)
    
    # Get payments
    payments = db.execute_query("""
        SELECT p.*, t.first_name || ' ' || t.last_name as tenant_name
        FROM payments p
        JOIN users t ON p.tenant_id = t.id
        WHERE p.lease_id = ?
        ORDER BY p.payment_date DESC
    """, (lease_id,))
    
    return payments
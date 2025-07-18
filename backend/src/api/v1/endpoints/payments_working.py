"""
Green PM - Working Payments API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from src.core.database_simple import db
from src.api.v1.endpoints.auth_working import get_current_user, require_admin

router = APIRouter(prefix="/payments", tags=["payments"])

# Pydantic Models
class PaymentBase(BaseModel):
    lease_id: str
    amount: float
    payment_date: str
    payment_method: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    payment_date: Optional[str] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None

class PaymentResponse(PaymentBase):
    id: str
    tenant_id: str
    status: str
    created_at: str
    
    # Additional fields
    property_name: Optional[str] = None
    property_address: Optional[str] = None
    tenant_name: Optional[str] = None
    tenant_email: Optional[str] = None
    landlord_name: Optional[str] = None
    landlord_email: Optional[str] = None

@router.get("/", response_model=List[PaymentResponse])
async def get_payments(
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get payments based on user role"""
    base_query = """
        SELECT p.*, 
               pr.name as property_name, pr.address as property_address,
               t.first_name || ' ' || t.last_name as tenant_name,
               t.email as tenant_email,
               ll.first_name || ' ' || ll.last_name as landlord_name,
               ll.email as landlord_email
        FROM payments p
        JOIN leases l ON p.lease_id = l.id
        JOIN properties pr ON l.property_id = pr.id
        JOIN users t ON p.tenant_id = t.id
        JOIN users ll ON pr.owner_id = ll.id
        WHERE 1=1
    """
    
    params = []
    
    if current_user['role'] == 'admin':
        # Admin can see all payments
        pass
    elif current_user['role'] == 'landlord':
        # Landlord can see payments for their properties
        base_query += " AND pr.owner_id = ?"
        params.append(current_user['id'])
    elif current_user['role'] == 'tenant':
        # Tenant can see only their own payments
        base_query += " AND p.tenant_id = ?"
        params.append(current_user['id'])
    
    if status:
        base_query += " AND p.status = ?"
        params.append(status)
    
    base_query += " ORDER BY p.payment_date DESC"
    
    payments = db.execute_query(base_query, tuple(params))
    
    return payments

@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new payment"""
    # Check if lease exists
    leases = db.execute_query("""
        SELECT l.*, p.owner_id
        FROM leases l
        JOIN properties p ON l.property_id = p.id
        WHERE l.id = ?
    """, (payment_data.lease_id,))
    
    if not leases:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    lease_dict = leases[0]
    
    # Check permissions
    if current_user['role'] == 'tenant':
        if lease_dict['tenant_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="You can only create payments for your own leases")
    elif current_user['role'] == 'landlord':
        if lease_dict['owner_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="You can only create payments for your properties")
    
    # Create payment
    payment_id = str(uuid.uuid4())
    
    db.execute_update("""
        INSERT INTO payments (id, lease_id, tenant_id, amount, payment_date, payment_method, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        payment_id, payment_data.lease_id, lease_dict['tenant_id'],
        payment_data.amount, payment_data.payment_date, payment_data.payment_method,
        'completed'
    ))
    
    # Get the created payment with all details
    payments = db.execute_query("""
        SELECT p.*, 
               pr.name as property_name, pr.address as property_address,
               t.first_name || ' ' || t.last_name as tenant_name,
               t.email as tenant_email,
               ll.first_name || ' ' || ll.last_name as landlord_name,
               ll.email as landlord_email
        FROM payments p
        JOIN leases l ON p.lease_id = l.id
        JOIN properties pr ON l.property_id = pr.id
        JOIN users t ON p.tenant_id = t.id
        JOIN users ll ON pr.owner_id = ll.id
        WHERE p.id = ?
    """, (payment_id,))
    
    if not payments:
        raise HTTPException(status_code=500, detail="Failed to create payment")
    
    return payments[0]

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific payment"""
    payments = db.execute_query("""
        SELECT p.*, 
               pr.name as property_name, pr.address as property_address,
               t.first_name || ' ' || t.last_name as tenant_name,
               t.email as tenant_email,
               ll.first_name || ' ' || ll.last_name as landlord_name,
               ll.email as landlord_email
        FROM payments p
        JOIN leases l ON p.lease_id = l.id
        JOIN properties pr ON l.property_id = pr.id
        JOIN users t ON p.tenant_id = t.id
        JOIN users ll ON pr.owner_id = ll.id
        WHERE p.id = ?
    """, (payment_id,))
    
    if not payments:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment_dict = payments[0]
    
    # Check permissions
    if current_user['role'] == 'tenant':
        if payment_dict['tenant_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user['role'] == 'landlord':
        # Check if landlord owns the property
        properties = db.execute_query(
            "SELECT * FROM properties WHERE id = ? AND owner_id = ?",
            (payment_dict['property_id'], current_user['id'])
        )
        if not properties:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return payment_dict

@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: str,
    payment_update: PaymentUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a payment"""
    # Get existing payment
    payments = db.execute_query("SELECT * FROM payments WHERE id = ?", (payment_id,))
    if not payments:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment_dict = payments[0]
    
    # Check permissions
    if current_user['role'] == 'tenant':
        if payment_dict['tenant_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user['role'] == 'landlord':
        # Check if landlord owns the property
        lease_info = db.execute_query("""
            SELECT l.*, p.owner_id
            FROM leases l
            JOIN properties p ON l.property_id = p.id
            WHERE l.id = ?
        """, (payment_dict['lease_id'],))
        
        if not lease_info or lease_info[0]['owner_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Build update query
    update_fields = []
    update_values = []
    
    for field, value in payment_update.dict(exclude_unset=True).items():
        update_fields.append(f"{field} = ?")
        update_values.append(value)
    
    if not update_fields:
        return await get_payment(payment_id, current_user)
    
    update_values.append(payment_id)
    
    query = f"UPDATE payments SET {', '.join(update_fields)} WHERE id = ?"
    db.execute_update(query, tuple(update_values))
    
    # Get updated payment
    return await get_payment(payment_id, current_user)

@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a payment"""
    # Get existing payment
    payments = db.execute_query("SELECT * FROM payments WHERE id = ?", (payment_id,))
    if not payments:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment_dict = payments[0]
    
    # Check permissions
    if current_user['role'] == 'tenant':
        raise HTTPException(status_code=403, detail="Tenants cannot delete payments")
    elif current_user['role'] == 'landlord':
        # Check if landlord owns the property
        lease_info = db.execute_query("""
            SELECT l.*, p.owner_id
            FROM leases l
            JOIN properties p ON l.property_id = p.id
            WHERE l.id = ?
        """, (payment_dict['lease_id'],))
        
        if not lease_info or lease_info[0]['owner_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete the payment
    db.execute_update("DELETE FROM payments WHERE id = ?", (payment_id,))
    
    return {"message": "Payment deleted successfully"}

@router.get("/stats/overview")
async def get_payment_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get payment statistics"""
    base_query = """
        SELECT SUM(amount) as total FROM payments p
        JOIN leases l ON p.lease_id = l.id
        JOIN properties pr ON l.property_id = pr.id
        WHERE p.status = 'completed'
    """
    
    params = []
    
    if current_user['role'] == 'landlord':
        base_query += " AND pr.owner_id = ?"
        params.append(current_user['id'])
    elif current_user['role'] == 'tenant':
        base_query += " AND p.tenant_id = ?"
        params.append(current_user['id'])
    
    # Total revenue
    total_revenue = db.execute_query(base_query, tuple(params))[0]['total'] or 0
    
    # This month's revenue
    this_month_revenue = db.execute_query(
        base_query + " AND p.payment_date >= date('now', 'start of month')",
        tuple(params)
    )[0]['total'] or 0
    
    # Payment count
    count_query = base_query.replace("SUM(amount) as total", "COUNT(*) as count")
    total_payments = db.execute_query(count_query, tuple(params))[0]['count']
    
    # This month's payments
    this_month_payments = db.execute_query(
        count_query + " AND p.payment_date >= date('now', 'start of month')",
        tuple(params)
    )[0]['count']
    
    return {
        "total_revenue": total_revenue,
        "this_month_revenue": this_month_revenue,
        "total_payments": total_payments,
        "this_month_payments": this_month_payments
    }
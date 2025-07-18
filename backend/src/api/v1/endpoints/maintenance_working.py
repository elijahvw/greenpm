"""
Green PM - Working Maintenance API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from src.core.database_simple import db
from src.api.v1.endpoints.auth_working import get_current_user, require_admin

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

# Pydantic Models
class MaintenanceBase(BaseModel):
    property_id: str
    title: str
    description: Optional[str] = None
    priority: str = "medium"  # low, medium, high, urgent

class MaintenanceCreate(MaintenanceBase):
    pass

class MaintenanceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None  # open, in_progress, completed, cancelled

class MaintenanceResponse(MaintenanceBase):
    id: str
    tenant_id: str
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

@router.get("/", response_model=List[MaintenanceResponse])
async def get_maintenance_requests(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get maintenance requests based on user role"""
    base_query = """
        SELECT m.*, 
               p.name as property_name, p.address as property_address,
               t.first_name || ' ' || t.last_name as tenant_name,
               t.email as tenant_email, t.phone as tenant_phone,
               l.first_name || ' ' || l.last_name as landlord_name,
               l.email as landlord_email
        FROM maintenance_requests m
        JOIN properties p ON m.property_id = p.id
        JOIN users t ON m.tenant_id = t.id
        JOIN users l ON p.owner_id = l.id
        WHERE 1=1
    """
    
    params = []
    
    if current_user['role'] == 'admin':
        # Admin can see all maintenance requests
        pass
    elif current_user['role'] == 'landlord':
        # Landlord can see requests for their properties
        base_query += " AND p.owner_id = ?"
        params.append(current_user['id'])
    elif current_user['role'] == 'tenant':
        # Tenant can see only their own requests
        base_query += " AND m.tenant_id = ?"
        params.append(current_user['id'])
    
    if status:
        base_query += " AND m.status = ?"
        params.append(status)
    
    if priority:
        base_query += " AND m.priority = ?"
        params.append(priority)
    
    base_query += " ORDER BY m.created_at DESC"
    
    requests = db.execute_query(base_query, tuple(params))
    
    return requests

@router.post("/", response_model=MaintenanceResponse)
async def create_maintenance_request(
    request_data: MaintenanceCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new maintenance request"""
    # Check if property exists
    properties = db.execute_query(
        "SELECT * FROM properties WHERE id = ? AND is_active = 1",
        (request_data.property_id,)
    )
    if not properties:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_dict = properties[0]
    
    # Check permissions
    if current_user['role'] == 'tenant':
        # Tenant can only create requests for properties they're leasing
        leases = db.execute_query("""
            SELECT * FROM leases 
            WHERE property_id = ? AND tenant_id = ? AND status = 'active'
        """, (request_data.property_id, current_user['id']))
        
        if not leases:
            raise HTTPException(status_code=403, detail="You don't have access to this property")
    
    elif current_user['role'] == 'landlord':
        # Landlord can create requests for their own properties
        if property_dict['owner_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="You don't own this property")
    
    # Create maintenance request
    request_id = str(uuid.uuid4())
    
    # For landlord/admin, we need to specify tenant_id
    tenant_id = current_user['id']
    if current_user['role'] != 'tenant':
        # For demo purposes, use the first active tenant of the property
        tenant_leases = db.execute_query("""
            SELECT tenant_id FROM leases 
            WHERE property_id = ? AND status = 'active'
            LIMIT 1
        """, (request_data.property_id,))
        
        if tenant_leases:
            tenant_id = tenant_leases[0]['tenant_id']
        else:
            raise HTTPException(status_code=400, detail="No active tenant found for this property")
    
    db.execute_update("""
        INSERT INTO maintenance_requests (id, property_id, tenant_id, title, description, priority)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        request_id, request_data.property_id, tenant_id,
        request_data.title, request_data.description, request_data.priority
    ))
    
    # Get the created request with all details
    requests = db.execute_query("""
        SELECT m.*, 
               p.name as property_name, p.address as property_address,
               t.first_name || ' ' || t.last_name as tenant_name,
               t.email as tenant_email, t.phone as tenant_phone,
               l.first_name || ' ' || l.last_name as landlord_name,
               l.email as landlord_email
        FROM maintenance_requests m
        JOIN properties p ON m.property_id = p.id
        JOIN users t ON m.tenant_id = t.id
        JOIN users l ON p.owner_id = l.id
        WHERE m.id = ?
    """, (request_id,))
    
    if not requests:
        raise HTTPException(status_code=500, detail="Failed to create maintenance request")
    
    return requests[0]

@router.get("/{request_id}", response_model=MaintenanceResponse)
async def get_maintenance_request(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a specific maintenance request"""
    requests = db.execute_query("""
        SELECT m.*, 
               p.name as property_name, p.address as property_address,
               t.first_name || ' ' || t.last_name as tenant_name,
               t.email as tenant_email, t.phone as tenant_phone,
               l.first_name || ' ' || l.last_name as landlord_name,
               l.email as landlord_email
        FROM maintenance_requests m
        JOIN properties p ON m.property_id = p.id
        JOIN users t ON m.tenant_id = t.id
        JOIN users l ON p.owner_id = l.id
        WHERE m.id = ?
    """, (request_id,))
    
    if not requests:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    
    request_dict = requests[0]
    
    # Check permissions
    if current_user['role'] == 'tenant':
        if request_dict['tenant_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user['role'] == 'landlord':
        # Check if landlord owns the property
        properties = db.execute_query(
            "SELECT * FROM properties WHERE id = ? AND owner_id = ?",
            (request_dict['property_id'], current_user['id'])
        )
        if not properties:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return request_dict

@router.put("/{request_id}", response_model=MaintenanceResponse)
async def update_maintenance_request(
    request_id: str,
    request_update: MaintenanceUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a maintenance request"""
    # Get existing request
    requests = db.execute_query("SELECT * FROM maintenance_requests WHERE id = ?", (request_id,))
    if not requests:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    
    request_dict = requests[0]
    
    # Check permissions
    if current_user['role'] == 'tenant':
        if request_dict['tenant_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Access denied")
        # Tenants can only update title, description, and priority
        if request_update.status is not None:
            raise HTTPException(status_code=403, detail="Tenants cannot update status")
    elif current_user['role'] == 'landlord':
        # Check if landlord owns the property
        properties = db.execute_query(
            "SELECT * FROM properties WHERE id = ? AND owner_id = ?",
            (request_dict['property_id'], current_user['id'])
        )
        if not properties:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Build update query
    update_fields = []
    update_values = []
    
    for field, value in request_update.dict(exclude_unset=True).items():
        update_fields.append(f"{field} = ?")
        update_values.append(value)
    
    if not update_fields:
        return await get_maintenance_request(request_id, current_user)
    
    update_fields.append("updated_at = ?")
    update_values.append(datetime.utcnow().isoformat())
    update_values.append(request_id)
    
    query = f"UPDATE maintenance_requests SET {', '.join(update_fields)} WHERE id = ?"
    db.execute_update(query, tuple(update_values))
    
    # Get updated request
    return await get_maintenance_request(request_id, current_user)

@router.delete("/{request_id}")
async def delete_maintenance_request(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a maintenance request"""
    # Get existing request
    requests = db.execute_query("SELECT * FROM maintenance_requests WHERE id = ?", (request_id,))
    if not requests:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    
    request_dict = requests[0]
    
    # Check permissions
    if current_user['role'] == 'tenant':
        if request_dict['tenant_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user['role'] == 'landlord':
        # Check if landlord owns the property
        properties = db.execute_query(
            "SELECT * FROM properties WHERE id = ? AND owner_id = ?",
            (request_dict['property_id'], current_user['id'])
        )
        if not properties:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete the request
    db.execute_update("DELETE FROM maintenance_requests WHERE id = ?", (request_id,))
    
    return {"message": "Maintenance request deleted successfully"}

@router.get("/stats/overview")
async def get_maintenance_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get maintenance statistics"""
    base_query = """
        SELECT COUNT(*) as count FROM maintenance_requests m
        JOIN properties p ON m.property_id = p.id
        WHERE 1=1
    """
    
    params = []
    
    if current_user['role'] == 'landlord':
        base_query += " AND p.owner_id = ?"
        params.append(current_user['id'])
    elif current_user['role'] == 'tenant':
        base_query += " AND m.tenant_id = ?"
        params.append(current_user['id'])
    
    # Total requests
    total_requests = db.execute_query(base_query, tuple(params))[0]['count']
    
    # By status
    open_requests = db.execute_query(base_query + " AND m.status = 'open'", tuple(params))[0]['count']
    in_progress_requests = db.execute_query(base_query + " AND m.status = 'in_progress'", tuple(params))[0]['count']
    completed_requests = db.execute_query(base_query + " AND m.status = 'completed'", tuple(params))[0]['count']
    
    # By priority
    high_priority = db.execute_query(base_query + " AND m.priority = 'high'", tuple(params))[0]['count']
    urgent_priority = db.execute_query(base_query + " AND m.priority = 'urgent'", tuple(params))[0]['count']
    
    return {
        "total_requests": total_requests,
        "open_requests": open_requests,
        "in_progress_requests": in_progress_requests,
        "completed_requests": completed_requests,
        "high_priority": high_priority,
        "urgent_priority": urgent_priority
    }
"""
Green PM - Working Properties API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from src.core.database_simple import db
from src.api.v1.endpoints.auth_working import get_current_user, require_admin, require_landlord

router = APIRouter(prefix="/properties", tags=["properties"])

# Pydantic Models
class PropertyBase(BaseModel):
    name: str
    address: str
    type: str
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    square_feet: Optional[int] = None
    rent_amount: Optional[float] = None
    description: Optional[str] = None

class PropertyCreate(PropertyBase):
    pass

class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    square_feet: Optional[int] = None
    rent_amount: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class PropertyResponse(PropertyBase):
    id: str
    owner_id: str
    is_active: bool
    created_at: str
    updated_at: str
    
    # Additional fields for detailed view
    owner_name: Optional[str] = None
    lease_count: Optional[int] = None
    current_tenant: Optional[str] = None

@router.get("/", response_model=List[PropertyResponse])
async def get_properties(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get properties based on user role"""
    if current_user['role'] == 'admin':
        # Admin can see all properties
        query = """
            SELECT p.*, u.first_name || ' ' || u.last_name as owner_name
            FROM properties p
            LEFT JOIN users u ON p.owner_id = u.id
            WHERE p.is_active = 1
            ORDER BY p.created_at DESC
        """
        properties = db.execute_query(query)
    elif current_user['role'] == 'landlord':
        # Landlord can see only their properties
        query = """
            SELECT p.*, u.first_name || ' ' || u.last_name as owner_name
            FROM properties p
            LEFT JOIN users u ON p.owner_id = u.id
            WHERE p.owner_id = ? AND p.is_active = 1
            ORDER BY p.created_at DESC
        """
        properties = db.execute_query(query, (current_user['id'],))
    else:
        # Tenant can see properties they're leasing
        query = """
            SELECT p.*, u.first_name || ' ' || u.last_name as owner_name
            FROM properties p
            LEFT JOIN users u ON p.owner_id = u.id
            INNER JOIN leases l ON p.id = l.property_id
            WHERE l.tenant_id = ? AND l.status = 'active' AND p.is_active = 1
            ORDER BY p.created_at DESC
        """
        properties = db.execute_query(query, (current_user['id'],))
    
    # Add lease count for each property
    for prop in properties:
        lease_count = db.execute_query(
            "SELECT COUNT(*) as count FROM leases WHERE property_id = ?", 
            (prop['id'],)
        )[0]['count']
        prop['lease_count'] = lease_count
        
        # Get current tenant
        current_tenant = db.execute_query("""
            SELECT u.first_name || ' ' || u.last_name as tenant_name
            FROM leases l
            JOIN users u ON l.tenant_id = u.id
            WHERE l.property_id = ? AND l.status = 'active'
            LIMIT 1
        """, (prop['id'],))
        
        prop['current_tenant'] = current_tenant[0]['tenant_name'] if current_tenant else None
    
    return properties

@router.post("/", response_model=PropertyResponse)
async def create_property(
    property_data: PropertyCreate,
    current_user: Dict[str, Any] = Depends(require_landlord)
):
    """Create a new property (landlord only)"""
    property_id = str(uuid.uuid4())
    
    db.execute_update("""
        INSERT INTO properties (id, owner_id, name, address, type, bedrooms, bathrooms, square_feet, rent_amount, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        property_id, current_user['id'], property_data.name, property_data.address,
        property_data.type, property_data.bedrooms, property_data.bathrooms,
        property_data.square_feet, property_data.rent_amount, property_data.description
    ))
    
    # Get the created property
    properties = db.execute_query("SELECT * FROM properties WHERE id = ?", (property_id,))
    if not properties:
        raise HTTPException(status_code=500, detail="Failed to create property")
    
    property_dict = properties[0]
    property_dict['owner_name'] = f"{current_user['first_name']} {current_user['last_name']}"
    property_dict['lease_count'] = 0
    property_dict['current_tenant'] = None
    
    return property_dict

@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get a specific property"""
    # Get property with owner info
    properties = db.execute_query("""
        SELECT p.*, u.first_name || ' ' || u.last_name as owner_name
        FROM properties p
        LEFT JOIN users u ON p.owner_id = u.id
        WHERE p.id = ? AND p.is_active = 1
    """, (property_id,))
    
    if not properties:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_dict = properties[0]
    
    # Check permissions
    if current_user['role'] == 'tenant':
        # Tenant can only see properties they're leasing
        leases = db.execute_query("""
            SELECT * FROM leases 
            WHERE property_id = ? AND tenant_id = ? AND status = 'active'
        """, (property_id, current_user['id']))
        
        if not leases:
            raise HTTPException(status_code=403, detail="Access denied")
    
    elif current_user['role'] == 'landlord':
        # Landlord can only see their own properties
        if property_dict['owner_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Add additional info
    lease_count = db.execute_query(
        "SELECT COUNT(*) as count FROM leases WHERE property_id = ?", 
        (property_id,)
    )[0]['count']
    property_dict['lease_count'] = lease_count
    
    # Get current tenant
    current_tenant = db.execute_query("""
        SELECT u.first_name || ' ' || u.last_name as tenant_name
        FROM leases l
        JOIN users u ON l.tenant_id = u.id
        WHERE l.property_id = ? AND l.status = 'active'
        LIMIT 1
    """, (property_id,))
    
    property_dict['current_tenant'] = current_tenant[0]['tenant_name'] if current_tenant else None
    
    return property_dict

@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: str,
    property_update: PropertyUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a property"""
    # Get existing property
    properties = db.execute_query("SELECT * FROM properties WHERE id = ? AND is_active = 1", (property_id,))
    if not properties:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_dict = properties[0]
    
    # Check permissions
    if current_user['role'] == 'landlord' and property_dict['owner_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Access denied")
    elif current_user['role'] == 'tenant':
        raise HTTPException(status_code=403, detail="Tenants cannot update properties")
    
    # Build update query
    update_fields = []
    update_values = []
    
    for field, value in property_update.dict(exclude_unset=True).items():
        if field == 'is_active':
            update_fields.append(f"{field} = ?")
            update_values.append(1 if value else 0)
        else:
            update_fields.append(f"{field} = ?")
            update_values.append(value)
    
    if not update_fields:
        return property_dict
    
    update_fields.append("updated_at = ?")
    update_values.append(datetime.utcnow().isoformat())
    update_values.append(property_id)
    
    query = f"UPDATE properties SET {', '.join(update_fields)} WHERE id = ?"
    db.execute_update(query, tuple(update_values))
    
    # Get updated property
    return await get_property(property_id, current_user)

@router.delete("/{property_id}")
async def delete_property(
    property_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a property (soft delete)"""
    # Get existing property
    properties = db.execute_query("SELECT * FROM properties WHERE id = ? AND is_active = 1", (property_id,))
    if not properties:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_dict = properties[0]
    
    # Check permissions
    if current_user['role'] == 'landlord' and property_dict['owner_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Access denied")
    elif current_user['role'] == 'tenant':
        raise HTTPException(status_code=403, detail="Tenants cannot delete properties")
    
    # Check if property has active leases
    active_leases = db.execute_query("""
        SELECT COUNT(*) as count FROM leases 
        WHERE property_id = ? AND status = 'active'
    """, (property_id,))[0]['count']
    
    if active_leases > 0:
        raise HTTPException(status_code=400, detail="Cannot delete property with active leases")
    
    # Soft delete
    db.execute_update("""
        UPDATE properties 
        SET is_active = 0, updated_at = ?
        WHERE id = ?
    """, (datetime.utcnow().isoformat(), property_id))
    
    return {"message": "Property deleted successfully"}

@router.get("/{property_id}/leases")
async def get_property_leases(
    property_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get leases for a property"""
    # Check if property exists and user has access
    await get_property(property_id, current_user)
    
    # Get leases with tenant info
    leases = db.execute_query("""
        SELECT l.*, u.first_name || ' ' || u.last_name as tenant_name,
               u.email as tenant_email, u.phone as tenant_phone
        FROM leases l
        JOIN users u ON l.tenant_id = u.id
        WHERE l.property_id = ?
        ORDER BY l.created_at DESC
    """, (property_id,))
    
    return leases

@router.get("/{property_id}/maintenance")
async def get_property_maintenance(
    property_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get maintenance requests for a property"""
    # Check if property exists and user has access
    await get_property(property_id, current_user)
    
    # Get maintenance requests with tenant info
    maintenance_requests = db.execute_query("""
        SELECT m.*, u.first_name || ' ' || u.last_name as tenant_name,
               u.email as tenant_email, u.phone as tenant_phone
        FROM maintenance_requests m
        JOIN users u ON m.tenant_id = u.id
        WHERE m.property_id = ?
        ORDER BY m.created_at DESC
    """, (property_id,))
    
    return maintenance_requests
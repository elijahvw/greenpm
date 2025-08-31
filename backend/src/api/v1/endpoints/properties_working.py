"""
Green PM - Properties Endpoints (Working Version)
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import uuid
from datetime import datetime

from src.core.database_simple import db
from src.api.v1.endpoints.auth_working import get_current_user

router = APIRouter()

class PropertyAddress(BaseModel):
    street: str
    unit: Optional[str] = None
    city: str
    state: str
    zipCode: str
    country: str

class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[PropertyAddress] = None
    type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    squareFeet: Optional[int] = None
    rentAmount: Optional[float] = None
    deposit: Optional[float] = None
    description: Optional[str] = None
    amenities: Optional[List[str]] = None

class PropertyCreate(BaseModel):
    name: str
    address: PropertyAddress
    type: str
    bedrooms: int
    bathrooms: float
    squareFeet: int
    rentAmount: float
    deposit: float
    description: Optional[str] = None
    amenities: Optional[List[str]] = []

@router.get("/")
async def get_properties(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get properties for current user"""
    try:
        user_id = current_user["id"]
        user_role = current_user["role"]
        
        # Query properties based on user role
        if user_role == 'landlord':
            # Landlords see only their properties
            properties_data = db.execute_query("""
                SELECT p.id, p.name, p.description, p.rent_amount, p.bedrooms, p.bathrooms,
                       p.square_feet, p.address, p.type, p.created_at, p.updated_at, p.owner_id
                FROM properties p
                WHERE p.owner_id = ? AND p.is_active = 1
                ORDER BY p.created_at DESC
            """, (user_id,))
        else:
            # Admin sees all properties
            properties_data = db.execute_query("""
                SELECT p.id, p.name, p.description, p.rent_amount, p.bedrooms, p.bathrooms,
                       p.square_feet, p.address, p.type, p.created_at, p.updated_at, p.owner_id
                FROM properties p
                WHERE p.is_active = 1
                ORDER BY p.created_at DESC
            """)
        
        properties = []
        for row in properties_data:
            property_id = row["id"] if isinstance(row, dict) else row[0]
            
            # Get current lease for this property
            lease_data = db.execute_query("""
                SELECT l.id, l.tenant_id, l.start_date, l.end_date, l.monthly_rent,
                       l.status, l.created_at, l.updated_at,
                       u.first_name, u.last_name, u.email
                FROM leases l
                LEFT JOIN users u ON l.tenant_id = u.id
                WHERE l.property_id = ? AND l.status = 'active'
                ORDER BY l.created_at DESC
                LIMIT 1
            """, (property_id,))
            
            current_lease = None
            if lease_data:
                lease_row = lease_data[0]
                current_lease = {
                    "id": lease_row[0],
                    "tenant_id": lease_row[1],
                    "start_date": lease_row[2],
                    "end_date": lease_row[3],
                    "monthly_rent": float(lease_row[4]) if lease_row[4] else None,
                    "status": lease_row[5],
                    "created_at": lease_row[6],
                    "updated_at": lease_row[7],
                    "tenant_name": f"{lease_row[8]} {lease_row[9]}" if lease_row[8] and lease_row[9] else None,
                    "tenant_email": lease_row[10]
                }
            
            # Determine status based on lease
            status = "occupied" if current_lease else "vacant"
            
            # Parse address (it's stored as a single string)
            address_parts = (row[7] or "").split(", ")
            street = address_parts[0] if address_parts else ""
            city = address_parts[1] if len(address_parts) > 1 else ""
            state_zip = address_parts[2] if len(address_parts) > 2 else ""
            
            property_dict = {
                "id": row[0],
                "name": row[1],
                "title": row[1],
                "description": row[2] or "",
                "type": row[8] or "apartment",  # Using actual type from database
                "bedrooms": row[4] or 0,
                "bathrooms": float(row[5]) if row[5] else 0.0,
                "squareFeet": row[6] or 0,
                "rentAmount": float(row[3]) if row[3] else 0.0,
                "deposit": 0.0,  # Not stored in simple schema
                "address": {
                    "street": street,
                    "unit": "",
                    "city": city,
                    "state": state_zip.split()[0] if state_zip else "",
                    "zipCode": state_zip.split()[1] if len(state_zip.split()) > 1 else "",
                    "country": "US"
                },
                "status": status,
                "amenities": [],  # Empty for now
                "images": [],     # Empty for now
                "currentLease": current_lease,
                "created_at": row[9],
                "updated_at": row[10],
                "owner_id": row[11]
            }
            properties.append(property_dict)
        
        return properties
        
    except Exception as e:
        print(f"❌ Error fetching properties: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch properties: {str(e)}")

@router.get("/{property_id}")
async def get_property(
    property_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get a single property by ID"""
    try:
        # Get property data
        property_data = db.execute_query("""
            SELECT p.id, p.name, p.description, p.rent_amount, p.bedrooms, p.bathrooms,
                   p.square_feet, p.address, p.type, p.created_at, p.updated_at, p.owner_id
            FROM properties p
            WHERE p.id = ? AND p.is_active = 1
        """, (property_id,))
        
        if not property_data:
            raise HTTPException(status_code=404, detail="Property not found")
        
        row = property_data[0]
        
        # Get current lease
        lease_data = db.execute_query("""
            SELECT l.id, l.tenant_id, l.start_date, l.end_date, l.monthly_rent,
                   l.status, l.created_at, l.updated_at,
                   u.first_name, u.last_name, u.email
            FROM leases l
            LEFT JOIN users u ON l.tenant_id = u.id
            WHERE l.property_id = ? AND l.status = 'active'
            ORDER BY l.created_at DESC
            LIMIT 1
        """, (property_id,))
        
        current_lease = None
        if lease_data:
            lease_row = lease_data[0]
            current_lease = {
                "id": lease_row[0],
                "tenant_id": lease_row[1],
                "start_date": lease_row[2],
                "end_date": lease_row[3],
                "monthly_rent": float(lease_row[4]) if lease_row[4] else None,
                "status": lease_row[5],
                "tenant_name": f"{lease_row[8]} {lease_row[9]}" if lease_row[8] and lease_row[9] else None,
                "tenant_email": lease_row[10]
            }
        
        status = "occupied" if current_lease else "vacant"
        
        # Parse address (it's stored as a single string)
        address_parts = (row[7] or "").split(", ")
        street = address_parts[0] if address_parts else ""
        city = address_parts[1] if len(address_parts) > 1 else ""
        state_zip = address_parts[2] if len(address_parts) > 2 else ""
        
        property_dict = {
            "id": row[0],
            "name": row[1],
            "title": row[1],
            "description": row[2] or "",
            "type": row[8] or "apartment",
            "bedrooms": row[4] or 0,
            "bathrooms": float(row[5]) if row[5] else 0.0,
            "squareFeet": row[6] or 0,
            "rentAmount": float(row[3]) if row[3] else 0.0,
            "deposit": 0.0,
            "address": {
                "street": street,
                "unit": "",
                "city": city,
                "state": state_zip.split()[0] if state_zip else "",
                "zipCode": state_zip.split()[1] if len(state_zip.split()) > 1 else "",
                "country": "US"
            },
            "status": status,
            "amenities": [],
            "images": [],
            "currentLease": current_lease,
            "created_at": row[9],
            "updated_at": row[10],
            "owner_id": row[11]
        }
        
        return property_dict
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch property: {str(e)}")

@router.post("/")
async def create_property(
    property_data: PropertyCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new property"""
    try:
        property_id = str(uuid.uuid4())
        user_id = current_user["id"]
        
        # Insert property
        db.execute_update("""
            INSERT INTO properties (
                id, title, description, rent_amount, bedrooms, bathrooms,
                square_feet, address_line1, address_line2, city, state, 
                zip_code, owner_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            property_id,
            property_data.name,
            property_data.description or "",
            property_data.rentAmount,
            property_data.bedrooms,
            property_data.bathrooms,
            property_data.squareFeet,
            property_data.address.street,
            property_data.address.unit,
            property_data.address.city,
            property_data.address.state,
            property_data.address.zipCode,
            user_id,
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat()
        ))
        
        # Get the created property
        return await get_property(property_id, current_user)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create property: {str(e)}")

@router.put("/{property_id}")
async def update_property(
    property_id: str,
    property_data: PropertyUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update an existing property"""
    try:
        # Check if property exists and belongs to user (if landlord)
        existing = db.execute_query("""
            SELECT id, owner_id FROM properties WHERE id = ?
        """, (property_id,))
        
        if not existing:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Check ownership for landlords
        if current_user["role"] == "landlord" and existing[0][1] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to update this property")
        
        # Build update query dynamically based on provided fields
        updates = []
        params = []
        
        if property_data.name is not None:
            updates.append("title = ?")
            params.append(property_data.name)
        
        if property_data.description is not None:
            updates.append("description = ?")
            params.append(property_data.description)
        
        if property_data.rentAmount is not None:
            updates.append("rent_amount = ?")
            params.append(property_data.rentAmount)
        
        if property_data.bedrooms is not None:
            updates.append("bedrooms = ?")
            params.append(property_data.bedrooms)
        
        if property_data.bathrooms is not None:
            updates.append("bathrooms = ?")
            params.append(property_data.bathrooms)
        
        if property_data.squareFeet is not None:
            updates.append("square_feet = ?")
            params.append(property_data.squareFeet)
        
        if property_data.address is not None:
            updates.append("address_line1 = ?")
            params.append(property_data.address.street)
            updates.append("address_line2 = ?")
            params.append(property_data.address.unit)
            updates.append("city = ?")
            params.append(property_data.address.city)
            updates.append("state = ?")
            params.append(property_data.address.state)
            updates.append("zip_code = ?")
            params.append(property_data.address.zipCode)
        
        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.utcnow().isoformat())
            params.append(property_id)
            
            query = f"UPDATE properties SET {', '.join(updates)} WHERE id = ?"
            db.execute_update(query, params)
        
        # Return updated property
        return await get_property(property_id, current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update property: {str(e)}")

@router.delete("/{property_id}")
async def delete_property(
    property_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a property"""
    try:
        print(f"🗑️ DELETE PROPERTY - Attempting to delete property {property_id}")
        
        # Check if property exists and belongs to user (if landlord)
        existing = db.execute_query("""
            SELECT id, name, owner_id FROM properties WHERE id = ? AND is_active = 1
        """, (property_id,))
        
        if not existing:
            print(f"❌ Property {property_id} not found")
            raise HTTPException(status_code=404, detail="Property not found")
        
        property_row = existing[0]
        
        # Check ownership for landlords
        if current_user["role"] == "landlord" and property_row[2] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this property")
        
        print(f"✅ Found property {property_id}: {property_row[1]}")
        
        # Check if property has active leases
        active_leases = db.execute_query("""
            SELECT COUNT(*) FROM leases WHERE property_id = ? AND status = 'active'
        """, (property_id,))
        
        if active_leases and active_leases[0][0] > 0:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete property with active leases. Please terminate leases first."
            )
        
        # Use soft delete - mark property as inactive instead of hard delete
        # This preserves referential integrity with leases, maintenance requests, etc.
        db.execute_update("""
            UPDATE properties SET is_active = 0, updated_at = ? WHERE id = ?
        """, (datetime.utcnow().isoformat(), property_id))
        
        print(f"🗑️ Successfully deleted property {property_id}")
        
        return {"message": "Property deleted successfully", "property_id": property_id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting property {property_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete property: {str(e)}")

# Additional endpoints for property images (simplified)
@router.post("/{property_id}/images")
async def upload_property_images(
    property_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Upload property images (placeholder)"""
    return {"message": "Image upload not implemented in demo", "imageUrls": []}

@router.get("/{property_id}/images")
async def get_property_images(
    property_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get property images (placeholder)"""
    return []

@router.delete("/{property_id}/images/{image_id}")
async def delete_property_image(
    property_id: str,
    image_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete property image (placeholder)"""
    return {"message": "Image deletion not implemented in demo"}
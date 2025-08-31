"""
Green PM - Simplified Properties Endpoints for Demo
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import uuid
from datetime import datetime

from src.core.database_simple import db
from src.api.v1.endpoints.auth_working import get_current_user

router = APIRouter()

def get_value(row, key):
    """Helper to get value from dictionary row"""
    return row.get(key) if isinstance(row, dict) else None

@router.get("/")
async def get_properties(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get properties for current user"""
    try:
        user_id = current_user["id"]
        user_role = current_user["role"]
        
        # Get properties data
        if user_role == 'landlord':
            properties_data = db.execute_query("""
                SELECT id, name, description, rent_amount, bedrooms, bathrooms,
                       square_feet, address, type, created_at, updated_at, owner_id
                FROM properties
                WHERE owner_id = ? AND is_active = 1
                ORDER BY created_at DESC
            """, (user_id,))
        else:
            properties_data = db.execute_query("""
                SELECT id, name, description, rent_amount, bedrooms, bathrooms,
                       square_feet, address, type, created_at, updated_at, owner_id
                FROM properties
                WHERE is_active = 1
                ORDER BY created_at DESC
            """)
        
        properties = []
        for row in properties_data:
            # Parse address
            address_str = get_value(row, "address") or ""
            address_parts = address_str.split(", ")
            street = address_parts[0] if address_parts else ""
            city = address_parts[1] if len(address_parts) > 1 else ""
            state_zip = address_parts[2] if len(address_parts) > 2 else ""
            
            # Get lease status (simplified - check if any lease exists)
            property_id = get_value(row, "id")
            lease_data = db.execute_query("""
                SELECT COUNT(*) as count FROM leases WHERE property_id = ? AND status = 'active'
            """, (property_id,))
            
            is_occupied = False
            if lease_data:
                count = get_value(lease_data[0], "count") or get_value(lease_data[0], "COUNT(*)")
                is_occupied = (count or 0) > 0
            
            property_dict = {
                "id": get_value(row, "id"),
                "name": get_value(row, "name"),
                "title": get_value(row, "name"),
                "description": get_value(row, "description") or "",
                "type": get_value(row, "type") or "apartment",
                "bedrooms": get_value(row, "bedrooms") or 0,
                "bathrooms": float(get_value(row, "bathrooms") or 0),
                "squareFeet": get_value(row, "square_feet") or 0,
                "rentAmount": float(get_value(row, "rent_amount") or 0),
                "deposit": 0.0,
                "address": {
                    "street": street,
                    "unit": "",
                    "city": city,
                    "state": state_zip.split()[0] if state_zip else "",
                    "zipCode": state_zip.split()[1] if len(state_zip.split()) > 1 else "",
                    "country": "US"
                },
                "status": "occupied" if is_occupied else "vacant",
                "amenities": [],
                "images": [],
                "currentLease": None,  # Simplified for demo
                "created_at": get_value(row, "created_at"),
                "updated_at": get_value(row, "updated_at"),
                "owner_id": get_value(row, "owner_id")
            }
            properties.append(property_dict)
        
        return properties
        
    except Exception as e:
        print(f"❌ Error fetching properties: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch properties: {str(e)}")

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
        property_name = get_value(property_row, "name")
        property_owner = get_value(property_row, "owner_id")
        
        # Check ownership for landlords
        if current_user["role"] == "landlord" and property_owner != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this property")
        
        print(f"✅ Found property {property_id}: {property_name}")
        
        # Check if property has active leases
        active_leases = db.execute_query("""
            SELECT COUNT(*) as count FROM leases WHERE property_id = ? AND status = 'active'
        """, (property_id,))
        
        if active_leases:
            count = get_value(active_leases[0], "count") or get_value(active_leases[0], "COUNT(*)")
            if (count or 0) > 0:
                raise HTTPException(
                    status_code=400, 
                    detail="Cannot delete property with active leases. Please terminate leases first."
                )
        
        # Use soft delete - mark property as inactive
        db.execute_update("""
            UPDATE properties SET is_active = 0, updated_at = ? WHERE id = ?
        """, (datetime.utcnow().isoformat(), property_id))
        
        print(f"🗑️ Successfully deleted property {property_id}")
        
        return {"message": "Property deleted successfully", "property_id": property_id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting property {property_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to delete property: {str(e)}")

# Placeholder endpoints for other property operations
@router.get("/{property_id}")
async def get_property(property_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get a single property by ID"""
    return {"message": "Individual property view not implemented in demo"}

@router.post("/")
async def create_property(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Create a new property"""
    return {"message": "Property creation not implemented in demo"}

@router.put("/{property_id}")
async def update_property(property_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Update an existing property"""
    return {"message": "Property update not implemented in demo"}

@router.post("/{property_id}/images")
async def upload_property_images(property_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Upload property images"""
    return {"message": "Image upload not implemented in demo", "imageUrls": []}

@router.get("/{property_id}/images")
async def get_property_images(property_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get property images"""
    return []

@router.delete("/{property_id}/images/{image_id}")
async def delete_property_image(property_id: str, image_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Delete property image"""
    return {"message": "Image deletion not implemented in demo"}
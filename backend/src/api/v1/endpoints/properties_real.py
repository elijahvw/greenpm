"""
Green PM - Properties Endpoints with Real PostgreSQL Database
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel, validator, Field
from typing import Union, Dict, Any
from datetime import datetime
import uuid
import json

from src.core.database import get_db

router = APIRouter()

class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None  # Frontend might send 'name' instead of 'title'
    description: Optional[str] = None
    rent_amount: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_feet: Optional[int] = None
    address_line1: Optional[str] = None
    street: Optional[str] = None  # Frontend might send 'street' instead of 'address_line1'
    address: Optional[Union[str, Dict[str, Any]]] = None  # Can be string or object
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    zipCode: Optional[str] = None  # Frontend might send camelCase
    
    @validator('rent_amount', pre=True)
    def parse_rent_amount(cls, v):
        if v is None or v == "":
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None
    
    @validator('bedrooms', pre=True)
    def parse_bedrooms(cls, v):
        if v is None or v == "":
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None
    
    @validator('bathrooms', pre=True)
    def parse_bathrooms(cls, v):
        if v is None or v == "":
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None
            
    @validator('square_feet', pre=True)
    def parse_square_feet(cls, v):
        if v is None or v == "":
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None
    
    class Config:
        extra = "allow"  # Allow extra fields to prevent validation errors

@router.get("/")
async def get_properties(db: AsyncSession = Depends(get_db)):
    """Get properties from real PostgreSQL database"""
    try:
        result = await db.execute(text("""
            SELECT id, title, description, rent_amount, bedrooms, bathrooms, 
                   square_feet, address_line1, city, state, zip_code, created_at, updated_at
            FROM properties 
            ORDER BY created_at DESC
        """))
        
        properties = []
        for row in result.fetchall():
            properties.append({
                "id": row.id,
                "title": row.title or "",
                "name": row.title or "",  # Frontend expects 'name'
                "description": row.description or "",
                "rent_amount": float(row.rent_amount) if row.rent_amount else 0.0,
                "bedrooms": row.bedrooms or 0,
                "bathrooms": row.bathrooms or 0,
                "square_feet": row.square_feet or 0,
                "address_line1": row.address_line1 or "",
                "street": row.address_line1 or "",  # Frontend expects 'street'
                "address": row.address_line1 or "",  # Alternative address field
                "city": row.city or "",
                "state": row.state or "",
                "zip_code": row.zip_code or "",
                "zipCode": row.zip_code or "",  # Frontend might expect camelCase
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                # Common frontend fields
                "type": "apartment",
                "status": "available",
                "is_active": True,
            })
        
        return properties
    except Exception as e:
        print(f"Database error in get_properties: {e}")
        # Return empty list if table doesn't exist or other DB error
        return []

@router.put("/{property_id}")
async def update_property(
    property_id: int,
    update_data: PropertyUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update property in real PostgreSQL database"""
    try:
        # Debug logging
        print(f"Updating property {property_id} with data: {update_data.dict()}")
        # Build update query dynamically based on provided fields
        update_fields = []
        values = {"property_id": property_id, "updated_at": datetime.now()}
        
        # Handle title (prefer 'title' over 'name')
        title_value = update_data.title or update_data.name
        if title_value is not None:
            update_fields.append("title = :title")
            values["title"] = title_value
            
        if update_data.description is not None:
            update_fields.append("description = :description")
            values["description"] = update_data.description
            
        if update_data.rent_amount is not None:
            update_fields.append("rent_amount = :rent_amount")
            values["rent_amount"] = float(update_data.rent_amount)
            
        if update_data.bedrooms is not None:
            update_fields.append("bedrooms = :bedrooms")
            values["bedrooms"] = update_data.bedrooms
            
        if update_data.bathrooms is not None:
            update_fields.append("bathrooms = :bathrooms")
            values["bathrooms"] = update_data.bathrooms
            
        if update_data.square_feet is not None:
            update_fields.append("square_feet = :square_feet")
            values["square_feet"] = update_data.square_feet
            
        # Handle address fields - can come from multiple sources
        address_line1_value = None
        city_value = None
        state_value = None
        zip_value = None
        
        # Extract from address object if it exists
        if update_data.address is not None and isinstance(update_data.address, dict):
            address_obj = update_data.address
            address_line1_value = address_obj.get('street')
            city_value = address_obj.get('city')
            state_value = address_obj.get('state')
            zip_value = address_obj.get('zipCode') or address_obj.get('zip_code')
        
        # Override with direct fields if provided
        if update_data.address_line1 is not None:
            address_line1_value = update_data.address_line1
        elif update_data.street is not None:
            address_line1_value = update_data.street
        elif isinstance(update_data.address, str):
            address_line1_value = update_data.address
            
        if update_data.city is not None:
            city_value = update_data.city
        if update_data.state is not None:
            state_value = update_data.state
        if update_data.zip_code is not None:
            zip_value = update_data.zip_code
        elif update_data.zipCode is not None:
            zip_value = update_data.zipCode
        
        # Apply updates
        if address_line1_value is not None:
            update_fields.append("address_line1 = :address_line1")
            values["address_line1"] = address_line1_value
            
        if city_value is not None:
            update_fields.append("city = :city")
            values["city"] = city_value
            
        if state_value is not None:
            update_fields.append("state = :state")
            values["state"] = state_value
            
        if zip_value is not None and zip_value != "":
            update_fields.append("zip_code = :zip_code")
            values["zip_code"] = zip_value

        if not update_fields:
            # No fields to update
            raise HTTPException(status_code=400, detail="No fields provided for update")

        # Add updated_at to all updates
        update_fields.append("updated_at = :updated_at")
        
        query = f"""
            UPDATE properties 
            SET {', '.join(update_fields)}
            WHERE id = :property_id
            RETURNING id, title, description, rent_amount, bedrooms, bathrooms, 
                      square_feet, address_line1, city, state, zip_code, created_at, updated_at
        """
        
        result = await db.execute(text(query), values)
        await db.commit()
        
        row = result.fetchone()
        if not row:
            # If property doesn't exist, create it
            insert_values = {
                "id": property_id,
                "uuid": str(uuid.uuid4()),
                "title": update_data.title or "New Property",
                "description": update_data.description or "Property description",
                "rent_amount": float(update_data.rent_amount) if update_data.rent_amount else 2500.0,
                "bedrooms": update_data.bedrooms or 2,
                "bathrooms": update_data.bathrooms or 1,
                "square_feet": update_data.square_feet or 850,
                "address_line1": update_data.address_line1 or "123 Main Street",
                "city": update_data.city or "San Francisco",
                "state": update_data.state or "CA",
                "zip_code": update_data.zip_code or "94105",
                "owner_id": 1,  # Default owner
                "property_type": "APARTMENT",
                "status": "AVAILABLE",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            await db.execute(text("""
                INSERT INTO properties (id, uuid, owner_id, title, description, property_type, 
                                      status, rent_amount, bedrooms, bathrooms, square_feet, 
                                      address_line1, city, state, zip_code, created_at, updated_at)
                VALUES (:id, :uuid, :owner_id, :title, :description, :property_type, 
                        :status, :rent_amount, :bedrooms, :bathrooms, :square_feet, 
                        :address_line1, :city, :state, :zip_code, :created_at, :updated_at)
            """), insert_values)
            await db.commit()
            
            return {
                "id": insert_values["id"],
                "title": insert_values["title"],
                "name": insert_values["title"],  # Frontend expects 'name'
                "description": insert_values["description"],
                "rent_amount": insert_values["rent_amount"],
                "bedrooms": insert_values["bedrooms"],
                "bathrooms": insert_values["bathrooms"],
                "square_feet": insert_values["square_feet"],
                "address_line1": insert_values["address_line1"],
                "street": insert_values["address_line1"],  # Frontend expects 'street'
                "address": insert_values["address_line1"],  # Alternative address field
                "city": insert_values["city"],
                "state": insert_values["state"],
                "zip_code": insert_values["zip_code"],
                "zipCode": insert_values["zip_code"],  # Frontend might expect camelCase
                "created_at": insert_values["created_at"].isoformat(),
                "updated_at": insert_values["updated_at"].isoformat(),
                # Common frontend fields
                "type": "apartment",
                "status": "available",
                "is_active": True,
            }
        
        return {
            "id": row.id,
            "title": row.title or "",
            "name": row.title or "",  # Frontend expects 'name'
            "description": row.description or "",
            "rent_amount": float(row.rent_amount) if row.rent_amount else 0.0,
            "bedrooms": row.bedrooms or 0,
            "bathrooms": row.bathrooms or 0,
            "square_feet": row.square_feet or 0,
            "address_line1": row.address_line1 or "",
            "street": row.address_line1 or "",  # Frontend expects 'street'
            "address": row.address_line1 or "",  # Alternative address field
            "city": row.city or "",
            "state": row.state or "",
            "zip_code": row.zip_code or "",
            "zipCode": row.zip_code or "",  # Frontend might expect camelCase
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            # Common frontend fields
            "type": "apartment",
            "status": "available",
            "is_active": True,
        }
        
    except Exception as e:
        print(f"Database error in update_property: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update property: {str(e)}")

@router.get("/{property_id}")
async def get_single_property(property_id: int, db: AsyncSession = Depends(get_db)):
    """Get single property by ID"""
    try:
        result = await db.execute(text("""
            SELECT id, title, description, rent_amount, bedrooms, bathrooms, 
                   square_feet, address_line1, city, state, zip_code, created_at, updated_at
            FROM properties WHERE id = :property_id
        """), {"property_id": property_id})
        
        row = result.fetchone()
        if row:
            return {
                "id": row.id,
                "title": row.title or "",
                "name": row.title or "",  # Frontend expects 'name'
                "description": row.description or "",
                "rent_amount": float(row.rent_amount) if row.rent_amount else 0.0,
                "bedrooms": row.bedrooms or 0,
                "bathrooms": row.bathrooms or 0,
                "square_feet": row.square_feet or 0,
                "address_line1": row.address_line1 or "",
                "street": row.address_line1 or "",  # Frontend expects 'street'
                "address": row.address_line1 or "",  # Alternative address field
                "city": row.city or "",
                "state": row.state or "",
                "zip_code": row.zip_code or "",
                "zipCode": row.zip_code or "",  # Frontend might expect camelCase
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                # Common frontend fields
                "type": "apartment",
                "status": "available",
                "is_active": True,
            }
        else:
            raise HTTPException(status_code=404, detail="Property not found")
    except Exception as e:
        print(f"Database error in get_single_property: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get property: {str(e)}")

@router.post("/seed")
async def seed_properties(db: AsyncSession = Depends(get_db)):
    """Create test properties in database"""
    try:
        # Create sample properties
        properties = [
            {
                "id": 1,
                "uuid": str(uuid.uuid4()),
                "owner_id": 1,
                "title": "Downtown Apartment",
                "description": "Modern 2-bedroom apartment in downtown",
                "property_type": "APARTMENT",
                "status": "AVAILABLE",
                "rent_amount": 2500.0,
                "bedrooms": 2,
                "bathrooms": 1,
                "square_feet": 850,
                "address_line1": "123 Main Street",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94105",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 2,
                "uuid": str(uuid.uuid4()),
                "owner_id": 1,
                "title": "Suburban House",
                "description": "Spacious 3-bedroom house with garden",
                "property_type": "HOUSE", 
                "status": "AVAILABLE",
                "rent_amount": 3200.0,
                "bedrooms": 3,
                "bathrooms": 2,
                "square_feet": 1200,
                "address_line1": "456 Oak Avenue",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94110",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        
        for prop in properties:
            await db.execute(text("""
                INSERT INTO properties (id, uuid, owner_id, title, description, property_type, 
                                      status, rent_amount, bedrooms, bathrooms, square_feet, 
                                      address_line1, city, state, zip_code, created_at, updated_at)
                VALUES (:id, :uuid, :owner_id, :title, :description, :property_type, 
                        :status, :rent_amount, :bedrooms, :bathrooms, :square_feet, 
                        :address_line1, :city, :state, :zip_code, :created_at, :updated_at)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    rent_amount = EXCLUDED.rent_amount,
                    updated_at = EXCLUDED.updated_at
            """), prop)
        
        await db.commit()
        return {"message": "Properties seeded successfully", "count": len(properties)}
    except Exception as e:
        print(f"Database error in seed_properties: {e}")
        return {"message": f"Error seeding properties: {e}", "count": 0}

@router.post("/debug/{property_id}")
async def debug_update_property(
    property_id: int,
    update_data: PropertyUpdate
):
    """Debug endpoint to see exactly what data is being sent"""
    return {
        "property_id": property_id,
        "received_data": update_data.dict(),
        "title": update_data.title,
        "name": update_data.name,
        "address_line1": update_data.address_line1,
        "street": update_data.street,
        "address": update_data.address,
        "city": update_data.city,
        "state": update_data.state,
        "zip_code": update_data.zip_code,
        "zipCode": update_data.zipCode,
        "rent_amount": update_data.rent_amount,
    }

@router.put("/raw/{property_id}")
async def raw_update_property(
    property_id: int,
    request: Request
):
    """Raw endpoint to capture exactly what frontend sends"""
    try:
        body = await request.body()
        raw_data = json.loads(body.decode('utf-8'))
        print(f"Raw data received for property {property_id}: {raw_data}")
        return {
            "property_id": property_id,
            "raw_body": raw_data,
            "message": "Data captured successfully"
        }
    except Exception as e:
        print(f"Error parsing raw data: {e}")
        return {
            "property_id": property_id,
            "error": str(e),
            "body": body.decode('utf-8') if 'body' in locals() else "Unable to decode"
        }
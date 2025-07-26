"""
Green PM - User Management Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

from src.core.database import get_db
from src.dependencies.auth import get_current_user
from src.models.user import User
from src.schemas.user import UserResponse, UserUpdate
from src.services.user_service import UserService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/tenants")
async def get_tenants(db: AsyncSession = Depends(get_db)):
    """Get all tenants from database"""
    try:
        query = text("""
            SELECT id, first_name, last_name, email, phone, status, created_at, updated_at,
                   date_of_birth, social_security_number, notes, move_in_date, move_out_date,
                   employer, position, monthly_income, employment_start_date,
                   emergency_contact_name, emergency_contact_phone, emergency_contact_relationship,
                   address_line1, city, state, zip_code, country
            FROM users 
            WHERE role = 'TENANT' 
            ORDER BY first_name, last_name
        """)
        
        result = await db.execute(query)
        tenant_rows = result.fetchall()
        
        tenants = []
        for row in tenant_rows:
            tenant_data = {
                "id": str(row.id),
                "firstName": row.first_name or "",
                "first_name": row.first_name or "",
                "lastName": row.last_name or "",
                "last_name": row.last_name or "",
                "email": row.email or "",
                "phone": row.phone or "",
                "role": "tenant",
                "status": row.status.lower() if row.status else "active",
                "created_at": row.created_at.isoformat() if row.created_at else "",
                "updated_at": row.updated_at.isoformat() if row.updated_at else "",
                "dateOfBirth": row.date_of_birth or "",
                "socialSecurityNumber": row.social_security_number or "",
                "notes": row.notes or "",
                "moveInDate": row.move_in_date or "",
                "moveOutDate": row.move_out_date or ""
            }
            
            # Add employment information if available
            if any([row.employer, row.position, row.monthly_income, row.employment_start_date]):
                tenant_data["employment"] = {
                    "employer": row.employer or "",
                    "position": row.position or "",
                    "monthlyIncome": row.monthly_income or 0,
                    "employmentStartDate": row.employment_start_date or ""
                }
            
            # Add emergency contact if available
            if any([row.emergency_contact_name, row.emergency_contact_phone, row.emergency_contact_relationship]):
                tenant_data["emergencyContact"] = {
                    "name": row.emergency_contact_name or "",
                    "phone": row.emergency_contact_phone or "",
                    "relationship": row.emergency_contact_relationship or ""
                }
            
            # Add address information if available
            if any([row.address_line1, row.city, row.state, row.zip_code, row.country]):
                tenant_data["address"] = {
                    "street": row.address_line1 or "",
                    "city": row.city or "",
                    "state": row.state or "",
                    "zipCode": row.zip_code or "",
                    "country": row.country or "US"
                }
            
            tenants.append(tenant_data)
        
        logger.info(f"Found {len(tenants)} tenants in database")
        return tenants
        
    except Exception as e:
        logger.error(f"Error fetching tenants: {e}")
        # Return empty list if database query fails
        return []

@router.post("/tenants")
async def create_tenant(
    tenant_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Create a new tenant in the database"""
    try:
        logger.info(f"Creating tenant with data: {tenant_data}")
        
        # Extract tenant data
        first_name = tenant_data.get("firstName") or tenant_data.get("first_name") or ""
        last_name = tenant_data.get("lastName") or tenant_data.get("last_name") or ""
        email = tenant_data.get("email") or ""
        phone = tenant_data.get("phone") or ""
        
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        # Check if email already exists
        email_check = await db.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": email}
        )
        
        if email_check.fetchone():
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Create tenant
        create_query = text("""
            INSERT INTO users (first_name, last_name, email, phone, role, status, hashed_password, created_at)
            VALUES (:first_name, :last_name, :email, :phone, 'TENANT', 'ACTIVE', 'temp_hash', NOW())
            RETURNING id, first_name, last_name, email, phone, created_at, updated_at
        """)
        
        result = await db.execute(create_query, {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone
        })
        
        new_tenant = result.fetchone()
        await db.commit()
        
        return {
            "id": str(new_tenant.id),
            "firstName": new_tenant.first_name,
            "first_name": new_tenant.first_name,
            "lastName": new_tenant.last_name,
            "last_name": new_tenant.last_name,
            "email": new_tenant.email,
            "phone": new_tenant.phone or "",
            "role": "tenant",
            "status": "active",
            "created_at": new_tenant.created_at.isoformat() if new_tenant.created_at else "",
            "updated_at": new_tenant.updated_at.isoformat() if new_tenant.updated_at else "",
            "message": "Tenant created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create tenant error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create tenant: {str(e)}")

@router.get("/tenants/{tenant_id}")
async def get_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a single tenant by ID"""
    try:
        query = text("""
            SELECT id, first_name, last_name, email, phone, status, created_at, updated_at,
                   date_of_birth, social_security_number, notes, move_in_date, move_out_date,
                   employer, position, monthly_income, employment_start_date,
                   emergency_contact_name, emergency_contact_phone, emergency_contact_relationship,
                   address_line1, city, state, zip_code, country
            FROM users 
            WHERE id = :tenant_id AND role = 'TENANT'
        """)
        
        result = await db.execute(query, {"tenant_id": int(tenant_id)})
        tenant_row = result.fetchone()
        
        if not tenant_row:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Build comprehensive tenant response
        tenant_data = {
            "id": str(tenant_row.id),
            "firstName": tenant_row.first_name or "",
            "first_name": tenant_row.first_name or "",
            "lastName": tenant_row.last_name or "",
            "last_name": tenant_row.last_name or "",
            "email": tenant_row.email or "",
            "phone": tenant_row.phone or "",
            "role": "tenant",
            "status": tenant_row.status.lower() if tenant_row.status else "active",
            "created_at": tenant_row.created_at.isoformat() if tenant_row.created_at else "",
            "updated_at": tenant_row.updated_at.isoformat() if tenant_row.updated_at else "",
            "dateOfBirth": tenant_row.date_of_birth or "",
            "socialSecurityNumber": tenant_row.social_security_number or "",
            "notes": tenant_row.notes or "",
            "moveInDate": tenant_row.move_in_date or "",
            "moveOutDate": tenant_row.move_out_date or ""
        }
        
        # Add employment information if available
        if any([tenant_row.employer, tenant_row.position, tenant_row.monthly_income, tenant_row.employment_start_date]):
            tenant_data["employment"] = {
                "employer": tenant_row.employer or "",
                "position": tenant_row.position or "",
                "monthlyIncome": tenant_row.monthly_income or 0,
                "employmentStartDate": tenant_row.employment_start_date or ""
            }
        
        # Add emergency contact if available
        if any([tenant_row.emergency_contact_name, tenant_row.emergency_contact_phone, tenant_row.emergency_contact_relationship]):
            tenant_data["emergencyContact"] = {
                "name": tenant_row.emergency_contact_name or "",
                "phone": tenant_row.emergency_contact_phone or "",
                "relationship": tenant_row.emergency_contact_relationship or ""
            }
        
        # Add address information if available
        if any([tenant_row.address_line1, tenant_row.city, tenant_row.state, tenant_row.zip_code, tenant_row.country]):
            tenant_data["address"] = {
                "street": tenant_row.address_line1 or "",
                "city": tenant_row.city or "",
                "state": tenant_row.state or "",
                "zipCode": tenant_row.zip_code or "",
                "country": tenant_row.country or "US"
            }
        
        return tenant_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get tenant error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tenant: {str(e)}")

@router.put("/tenants/{tenant_id}")
async def update_tenant(
    tenant_id: str,
    tenant_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Update a tenant in the database"""
    try:
        logger.info(f"Updating tenant {tenant_id} with data: {tenant_data}")
        
        # Extract basic data
        first_name = tenant_data.get("firstName") or tenant_data.get("first_name")
        last_name = tenant_data.get("lastName") or tenant_data.get("last_name")
        email = tenant_data.get("email")
        phone = tenant_data.get("phone")
        date_of_birth = tenant_data.get("dateOfBirth")
        notes = tenant_data.get("notes")
        status = tenant_data.get("status")
        move_in_date = tenant_data.get("moveInDate")
        move_out_date = tenant_data.get("moveOutDate")
        
        # Extract employment data
        employment = tenant_data.get("employment", {})
        employer = employment.get("employer") if employment else None
        position = employment.get("position") if employment else None
        monthly_income = employment.get("monthlyIncome") if employment else None
        employment_start_date = employment.get("employmentStartDate") if employment else None
        
        # Extract emergency contact data
        emergency_contact = tenant_data.get("emergencyContact", {})
        emergency_contact_name = emergency_contact.get("name") if emergency_contact else None
        emergency_contact_phone = emergency_contact.get("phone") if emergency_contact else None
        emergency_contact_relationship = emergency_contact.get("relationship") if emergency_contact else None
        
        # Extract address data
        address = tenant_data.get("address", {})
        address_line1 = address.get("street") if address else None
        city = address.get("city") if address else None
        state = address.get("state") if address else None
        zip_code = address.get("zipCode") if address else None
        country = address.get("country") if address else None
        
        # Build update query
        update_fields = []
        params = {"tenant_id": int(tenant_id)}
        
        # Basic fields
        if first_name:
            update_fields.append("first_name = :first_name")
            params["first_name"] = first_name
            
        if last_name:
            update_fields.append("last_name = :last_name")
            params["last_name"] = last_name
            
        if email:
            update_fields.append("email = :email")
            params["email"] = email
            
        if phone:
            update_fields.append("phone = :phone")
            params["phone"] = phone
            
        if date_of_birth:
            update_fields.append("date_of_birth = :date_of_birth")
            params["date_of_birth"] = date_of_birth
            
        if notes:
            update_fields.append("notes = :notes")
            params["notes"] = notes
            
        if status:
            update_fields.append("status = :status")
            params["status"] = status.upper()
            
        if move_in_date:
            update_fields.append("move_in_date = :move_in_date")
            params["move_in_date"] = move_in_date
            
        if move_out_date:
            update_fields.append("move_out_date = :move_out_date")
            params["move_out_date"] = move_out_date
        
        # Employment fields
        if employer:
            update_fields.append("employer = :employer")
            params["employer"] = employer
            
        if position:
            update_fields.append("position = :position")
            params["position"] = position
            
        if monthly_income:
            update_fields.append("monthly_income = :monthly_income")
            params["monthly_income"] = monthly_income
            
        if employment_start_date:
            update_fields.append("employment_start_date = :employment_start_date")
            params["employment_start_date"] = employment_start_date
        
        # Emergency contact fields
        if emergency_contact_name:
            update_fields.append("emergency_contact_name = :emergency_contact_name")
            params["emergency_contact_name"] = emergency_contact_name
            
        if emergency_contact_phone:
            update_fields.append("emergency_contact_phone = :emergency_contact_phone")
            params["emergency_contact_phone"] = emergency_contact_phone
            
        if emergency_contact_relationship:
            update_fields.append("emergency_contact_relationship = :emergency_contact_relationship")
            params["emergency_contact_relationship"] = emergency_contact_relationship
        
        # Address fields
        if address_line1:
            update_fields.append("address_line1 = :address_line1")
            params["address_line1"] = address_line1
            
        if city:
            update_fields.append("city = :city")
            params["city"] = city
            
        if state:
            update_fields.append("state = :state")
            params["state"] = state
            
        if zip_code:
            update_fields.append("zip_code = :zip_code")
            params["zip_code"] = zip_code
            
        if country:
            update_fields.append("country = :country")
            params["country"] = country
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update the tenant (only update existing columns to avoid SQL errors)
        safe_update_fields = []
        safe_params = {"tenant_id": int(tenant_id)}
        
        # Include all fields that now exist in the database schema
        basic_fields = [
            "first_name", "last_name", "email", "phone", "status", 
            "address_line1", "city", "state", "zip_code", "country",
            "date_of_birth", "social_security_number", "notes", 
            "move_in_date", "move_out_date", "employer", "position", 
            "monthly_income", "employment_start_date", "emergency_contact_name", 
            "emergency_contact_phone", "emergency_contact_relationship"
        ]
        for field in update_fields:
            field_name = field.split(" = ")[0]
            if field_name in basic_fields:
                safe_update_fields.append(field)
                param_name = field.split(":")[1]
                safe_params[param_name] = params[param_name]
        
        if not safe_update_fields:
            # If no safe fields to update, just return current data
            get_query = text("""
                SELECT id, first_name, last_name, email, phone, status, created_at, updated_at
                FROM users 
                WHERE id = :tenant_id AND role = 'TENANT'
            """)
            result = await db.execute(get_query, {"tenant_id": int(tenant_id)})
            current_tenant = result.fetchone()
            
            if not current_tenant:
                raise HTTPException(status_code=404, detail="Tenant not found")
                
            return {
                "id": str(current_tenant.id),
                "firstName": current_tenant.first_name,
                "first_name": current_tenant.first_name,
                "lastName": current_tenant.last_name,
                "last_name": current_tenant.last_name,
                "email": current_tenant.email,
                "phone": current_tenant.phone,
                "role": "tenant",
                "status": current_tenant.status.lower() if current_tenant.status else "active",
                "message": "Tenant data retrieved (no database changes made)"
            }
        
        # Update the tenant with safe fields
        update_query = text(f"""
            UPDATE users 
            SET {', '.join(safe_update_fields)}, updated_at = NOW()
            WHERE id = :tenant_id AND role = 'TENANT'
            RETURNING id, first_name, last_name, email, phone, status
        """)
        
        result = await db.execute(update_query, safe_params)
        updated_tenant = result.fetchone()
        
        if not updated_tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        await db.commit()
        
        return {
            "id": str(updated_tenant.id),
            "firstName": updated_tenant.first_name,
            "first_name": updated_tenant.first_name,
            "lastName": updated_tenant.last_name,
            "last_name": updated_tenant.last_name,
            "email": updated_tenant.email,
            "phone": updated_tenant.phone,
            "role": "tenant",
            "status": "active",
            "message": "Tenant updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update tenant error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update tenant: {str(e)}")

@router.delete("/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a tenant from the database"""
    try:
        logger.info(f"Deleting tenant {tenant_id}")
        
        # Check if tenant has any active leases
        lease_check_query = text("""
            SELECT COUNT(*) as lease_count
            FROM leases 
            WHERE tenant_id = :tenant_id AND status IN ('ACTIVE', 'PENDING')
        """)
        
        lease_result = await db.execute(lease_check_query, {"tenant_id": int(tenant_id)})
        lease_count = lease_result.fetchone().lease_count
        
        if lease_count > 0:
            lease_word = "lease" if lease_count == 1 else "leases"
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete tenant. They have {lease_count} active/pending {lease_word}. Please terminate their {lease_word} first."
            )
        
        # Delete the tenant
        delete_query = text("""
            DELETE FROM users 
            WHERE id = :tenant_id AND role = 'TENANT'
            RETURNING id
        """)
        
        result = await db.execute(delete_query, {"tenant_id": int(tenant_id)})
        deleted_tenant = result.fetchone()
        
        if not deleted_tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        await db.commit()
        
        return {
            "message": "Tenant deleted successfully",
            "tenant_id": tenant_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete tenant error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete tenant: {str(e)}")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    user_service = UserService(db)
    updated_user = await user_service.update_user(current_user.id, user_update)
    return updated_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    user_service = UserService(db)
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
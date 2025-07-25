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
async def get_tenants():
    """Get all tenants - simplified for testing"""
    return [
        {
            "id": "tenant1",
            "firstName": "John",
            "first_name": "John",
            "lastName": "Doe",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "555-0101",
            "role": "tenant",
            "status": "active"
        },
        {
            "id": "tenant2",
            "firstName": "Jane",
            "first_name": "Jane",
            "lastName": "Smith",
            "last_name": "Smith",
            "email": "jane@example.com",
            "phone": "555-0102",
            "role": "tenant",
            "status": "active"
        },
        {
            "id": "tenant3",
            "firstName": "Bob",
            "first_name": "Bob",
            "lastName": "Johnson",
            "last_name": "Johnson",
            "email": "bob@example.com",
            "phone": "555-0103",
            "role": "tenant",
            "status": "active"
        }
    ]

@router.put("/tenants/{tenant_id}")
async def update_tenant(
    tenant_id: str,
    tenant_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Update a tenant in the database"""
    try:
        logger.info(f"Updating tenant {tenant_id} with data: {tenant_data}")
        
        # Extract the data
        first_name = tenant_data.get("firstName") or tenant_data.get("first_name")
        last_name = tenant_data.get("lastName") or tenant_data.get("last_name")
        email = tenant_data.get("email")
        phone = tenant_data.get("phone")
        
        # Build update query
        update_fields = []
        params = {"tenant_id": int(tenant_id)}
        
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
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update the tenant
        update_query = text(f"""
            UPDATE users 
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE id = :tenant_id AND role = 'TENANT'
            RETURNING id, first_name, last_name, email, phone
        """)
        
        result = await db.execute(update_query, params)
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
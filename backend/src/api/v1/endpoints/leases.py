"""
Green PM - Lease Management Endpoints (PostgreSQL)
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import date, datetime
import logging

from src.core.database import get_db
from src.models.lease import Lease, LeaseStatus
from src.models.property import Property
from src.models.user import User
# from src.schemas.lease import LeaseCreate, LeaseUpdate, LeaseResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["leases"])

@router.get("/test-validation/{property_id}")
async def test_validation_query(property_id: int, db: AsyncSession = Depends(get_db)):
    """Test endpoint to check validation query"""
    try:
        from sqlalchemy import text
        logger.info(f"Testing validation query for property {property_id}")
        
        active_check_query = text("""
            SELECT id FROM leases 
            WHERE property_id = :property_id 
            AND status::text = 'ACTIVE'
        """)
        active_result = await db.execute(active_check_query, {"property_id": property_id})
        existing_active = active_result.fetchone()
        
        return {
            "property_id": property_id,
            "existing_active_lease": existing_active[0] if existing_active else None,
            "validation_would_block": bool(existing_active)
        }
    except Exception as e:
        logger.error(f"Test validation error: {e}")
        return {"error": str(e)}

@router.get("/properties")
async def get_properties_for_leases(db: AsyncSession = Depends(get_db)):
    """Get all properties for lease creation dropdown - shows all properties regardless of occupancy status"""
    try:
        from sqlalchemy import text
        logger.info("Getting all properties for lease creation")
        
        # Get all properties - don't filter by occupancy status
        properties_query = text("""
            SELECT id, title, description, rent_amount, bedrooms, bathrooms, 
                   square_feet, address_line1, address_line2, city, state, zip_code
            FROM properties 
            ORDER BY title ASC
        """)
        
        result = await db.execute(properties_query)
        properties = []
        
        for row in result.fetchall():
            # Format address
            address_parts = [row.address_line1]
            if row.address_line2:
                address_parts.append(row.address_line2)
            if row.city:
                address_parts.append(row.city)
            if row.state:
                address_parts.append(row.state)
            if row.zip_code:
                address_parts.append(row.zip_code)
            
            full_address = ", ".join(filter(None, address_parts))
            
            properties.append({
                "id": str(row.id),
                "title": row.title or "Untitled Property",
                "description": row.description or "",
                "address": full_address,
                "rent_amount": float(row.rent_amount or 0),
                "bedrooms": int(row.bedrooms or 0),
                "bathrooms": float(row.bathrooms or 0),
                "square_feet": int(row.square_feet or 0),
                # Include both camelCase and snake_case for frontend compatibility
                "rentAmount": float(row.rent_amount or 0),
                "squareFeet": int(row.square_feet or 0)
            })
        
        logger.info(f"Returning {len(properties)} properties for lease creation")
        return properties
        
    except Exception as e:
        logger.error(f"Get properties for leases error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get properties: {str(e)}")

@router.get("/")
async def get_leases(db: AsyncSession = Depends(get_db)):
    """Get all leases from PostgreSQL database"""
    try:
        # Use raw SQL to avoid SQLAlchemy relationship issues
        from sqlalchemy import text
        
        # Get leases with property and tenant info using raw SQL join
        query = text("""
            SELECT 
                l.id, l.property_id, l.tenant_id, l.landlord_id,
                l.start_date, l.end_date, l.monthly_rent, l.security_deposit, 
                l.late_fee, l.late_fee_grace_days, l.status,
                l.created_at, l.updated_at,
                p.title as property_title, p.address_line1, p.city,
                u.first_name, u.last_name, u.email
            FROM leases l
            LEFT JOIN properties p ON l.property_id = p.id
            LEFT JOIN users u ON l.tenant_id = u.id
            ORDER BY l.created_at DESC
        """)
        
        result = await db.execute(query)
        lease_rows = result.fetchall()
        
        logger.info(f"Found {len(lease_rows)} leases in PostgreSQL database")
        
        # Format leases for frontend compatibility
        formatted_leases = []
        for row in lease_rows:
            # Build property address
            address_parts = []
            if row.address_line1:
                address_parts.append(row.address_line1)
            if row.city:
                address_parts.append(row.city)
            property_address = ", ".join(address_parts) if address_parts else "Unknown Address"
            
            # Build tenant name
            tenant_name = f"{row.first_name or ''} {row.last_name or ''}".strip()
            if not tenant_name:
                tenant_name = "Unknown Tenant"
            
            formatted_lease = {
                "id": str(row.id),
                "propertyId": str(row.property_id),
                "property_id": str(row.property_id),
                "tenantId": str(row.tenant_id),
                "tenant_id": str(row.tenant_id),
                "startDate": row.start_date.isoformat() if row.start_date else "",
                "start_date": row.start_date.isoformat() if row.start_date else "",
                "endDate": row.end_date.isoformat() if row.end_date else "",
                "end_date": row.end_date.isoformat() if row.end_date else "",
                "monthlyRent": float(row.monthly_rent or 0),
                "monthly_rent": float(row.monthly_rent or 0),
                "rent_amount": float(row.monthly_rent or 0),
                "securityDeposit": float(row.security_deposit or 0),
                "security_deposit": float(row.security_deposit or 0),
                "lateFeePenalty": float(row.late_fee or 0),
                "late_fee_penalty": float(row.late_fee or 0),
                "gracePeriodDays": int(row.late_fee_grace_days or 5),
                "grace_period_days": int(row.late_fee_grace_days or 5),
                "status": row.status if row.status else "pending",
                "propertyTitle": row.property_title or "Unknown Property",
                "property_title": row.property_title or "Unknown Property",
                "property_name": row.property_title or "Unknown Property",
                "propertyAddress": property_address,
                "property_address": property_address,
                "tenantName": tenant_name,
                "tenant_name": tenant_name,
                "tenantEmail": row.email or "unknown@example.com",
                "tenant_email": row.email or "unknown@example.com",
                "created_at": row.created_at.isoformat() if row.created_at else "",
                "updated_at": row.updated_at.isoformat() if row.updated_at else ""
            }
            formatted_leases.append(formatted_lease)
        
        logger.info(f"Returning {len(formatted_leases)} formatted leases from PostgreSQL")
        return formatted_leases
        
    except Exception as e:
        logger.error(f"Get leases error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch leases: {str(e)}")

@router.post("/")
async def create_lease(lease_data: dict, db: AsyncSession = Depends(get_db)):
    """Create a new lease in PostgreSQL database"""
    try:
        from sqlalchemy import text
        logger.info(f"Creating lease in PostgreSQL: {lease_data}")
        
        # Extract data with both camelCase and snake_case support
        property_id = int(lease_data.get("propertyId") or lease_data.get("property_id"))
        tenant_id = lease_data.get("tenantId") or lease_data.get("tenant_id")
        start_date = lease_data.get("startDate") or lease_data.get("start_date")
        end_date = lease_data.get("endDate") or lease_data.get("end_date")
        monthly_rent = float(lease_data.get("monthlyRent") or lease_data.get("monthly_rent", 0))
        security_deposit = float(lease_data.get("securityDeposit") or lease_data.get("security_deposit", 0))
        late_fee = float(lease_data.get("lateFeePenalty") or lease_data.get("late_fee_penalty") or lease_data.get("late_fee_amount", 0))
        late_fee_grace_days = int(lease_data.get("gracePeriodDays") or lease_data.get("grace_period_days") or lease_data.get("late_fee_grace_period", 5))
        
        # Look up tenant details from database (convert tenant_id to int)
        tenant_query = text("SELECT id, first_name, last_name, email FROM users WHERE id = :tenant_id")
        tenant_result = await db.execute(tenant_query, {"tenant_id": int(tenant_id)})
        tenant_row = tenant_result.fetchone()
        
        if not tenant_row:
            raise HTTPException(status_code=404, detail=f"Tenant with ID {tenant_id} not found")
        
        tenant_first_name = tenant_row.first_name or "Unknown"
        tenant_last_name = tenant_row.last_name or "Tenant"
        tenant_email = tenant_row.email
        
        # Get status (default to PENDING) - database uses uppercase enum values
        status = lease_data.get("status", "PENDING").upper()
        logger.info(f"Lease status: {status}")
        
        # Validate: Only one active lease per property
        if status == "ACTIVE":
            logger.info(f"Checking for existing active leases on property {property_id}")
            try:
                active_check_query = text("""
                    SELECT id FROM leases 
                    WHERE property_id = :property_id 
                    AND status::text = 'ACTIVE'
                """)
                active_result = await db.execute(active_check_query, {"property_id": property_id})
                existing_active = active_result.fetchone()
                logger.info(f"Existing active lease check result: {existing_active}")
                
                if existing_active:
                    logger.info(f"Found existing active lease {existing_active[0]}, raising validation error")
                    await db.rollback()  # Ensure clean state
                    raise HTTPException(
                        status_code=400, 
                        detail="This property already has an active lease. Only one active lease per property is allowed. Please terminate the existing lease first."
                    )
            except HTTPException:
                # Re-raise HTTP exceptions (our validation errors)
                raise
            except Exception as validation_error:
                logger.error(f"Validation query error: {validation_error}")
                # Continue without validation if query fails
                logger.warning("Continuing lease creation without validation due to query error")
        
        # Verify property exists
        property_check = await db.execute(text("SELECT id, title FROM properties WHERE id = :prop_id"), {"prop_id": property_id})
        property_row = property_check.fetchone()
        if not property_row:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # We already have the tenant details from the earlier query
        # tenant_id is already set from the lookup above
        
        # Create lease using raw SQL
        create_lease_query = text("""
            INSERT INTO leases (
                property_id, tenant_id, landlord_id, start_date, end_date,
                monthly_rent, security_deposit, late_fee, late_fee_grace_days,
                lease_type, status, created_at, updated_at
            ) VALUES (
                :property_id, :tenant_id, 1, :start_date, :end_date,
                :monthly_rent, :security_deposit, :late_fee, :late_fee_grace_days,
                'FIXED_TERM', :status, NOW(), NOW()
            ) RETURNING id
        """)
        
        from datetime import datetime
        
        lease_result = await db.execute(create_lease_query, {
            "property_id": property_id,
            "tenant_id": int(tenant_id),
            "start_date": datetime.fromisoformat(start_date).date() if start_date else None,
            "end_date": datetime.fromisoformat(end_date).date() if end_date else None,
            "monthly_rent": monthly_rent,
            "security_deposit": security_deposit,
            "late_fee": late_fee,
            "late_fee_grace_days": late_fee_grace_days,
            "status": status
        })
        
        lease_id = lease_result.fetchone()[0]
        await db.commit()
        
        # Get the created lease with property and tenant info
        get_lease_query = text("""
            SELECT 
                l.id, l.property_id, l.tenant_id, l.start_date, l.end_date,
                l.monthly_rent, l.security_deposit, l.late_fee, l.late_fee_grace_days,
                l.status, l.created_at, l.updated_at,
                p.title as property_title, p.address_line1, p.city,
                u.first_name, u.last_name, u.email
            FROM leases l
            LEFT JOIN properties p ON l.property_id = p.id
            LEFT JOIN users u ON l.tenant_id = u.id
            WHERE l.id = :lease_id
        """)
        
        result = await db.execute(get_lease_query, {"lease_id": lease_id})
        row = result.fetchone()
        
        # Build response
        address_parts = []
        if row.address_line1:
            address_parts.append(row.address_line1)
        if row.city:
            address_parts.append(row.city)
        property_address = ", ".join(address_parts) if address_parts else "Unknown Address"
        
        tenant_name = f"{row.first_name or ''} {row.last_name or ''}".strip()
        if not tenant_name:
            tenant_name = "Unknown Tenant"
        
        response = {
            "id": str(row.id),
            "propertyId": str(row.property_id),
            "property_id": str(row.property_id),
            "tenantId": str(row.tenant_id),
            "tenant_id": str(row.tenant_id),
            "startDate": row.start_date.isoformat() if row.start_date else "",
            "start_date": row.start_date.isoformat() if row.start_date else "",
            "endDate": row.end_date.isoformat() if row.end_date else "",
            "end_date": row.end_date.isoformat() if row.end_date else "",
            "monthlyRent": float(row.monthly_rent or 0),
            "monthly_rent": float(row.monthly_rent or 0),
            "rent_amount": float(row.monthly_rent or 0),
            "securityDeposit": float(row.security_deposit or 0),
            "security_deposit": float(row.security_deposit or 0),
            "lateFeePenalty": float(row.late_fee or 0),
            "late_fee_penalty": float(row.late_fee or 0),
            "gracePeriodDays": int(row.late_fee_grace_days or 5),
            "grace_period_days": int(row.late_fee_grace_days or 5),
            "status": row.status if row.status else "pending",
            "propertyTitle": row.property_title or "Unknown Property",
            "property_title": row.property_title or "Unknown Property",
            "property_name": row.property_title or "Unknown Property",
            "propertyAddress": property_address,
            "property_address": property_address,
            "tenantName": tenant_name,
            "tenant_name": tenant_name,
            "tenantEmail": row.email or "unknown@example.com",
            "tenant_email": row.email or "unknown@example.com",
            "created_at": row.created_at.isoformat() if row.created_at else "",
            "updated_at": row.updated_at.isoformat() if row.updated_at else ""
        }
        
        logger.info(f"Created lease in PostgreSQL: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Create lease error: {e}")
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create lease: {str(e)}")

@router.put("/{lease_id}")
async def update_lease(lease_id: str, lease_data: dict, db: AsyncSession = Depends(get_db)):
    """Update lease in PostgreSQL database"""
    try:
        from sqlalchemy import text
        from datetime import datetime
        logger.info(f"Updating lease {lease_id} in PostgreSQL: {lease_data}")
        
        # Check if lease exists
        check_query = text("SELECT id FROM leases WHERE id = :lease_id")
        result = await db.execute(check_query, {"lease_id": int(lease_id)})
        lease_row = result.fetchone()
        
        if not lease_row:
            raise HTTPException(status_code=404, detail="Lease not found")
        
        # Extract update data with both camelCase and snake_case support
        update_fields = []
        params = {"lease_id": int(lease_id)}
        
        if "status" in lease_data or "status" in lease_data:
            status = lease_data.get("status", lease_data.get("status", "")).upper()
            
            # Validate: Only one active lease per property
            if status == "ACTIVE":
                # Get property_id for this lease
                get_property_query = text("SELECT property_id FROM leases WHERE id = :lease_id")
                prop_result = await db.execute(get_property_query, {"lease_id": int(lease_id)})
                prop_row = prop_result.fetchone()
                
                if prop_row:
                    property_id = prop_row[0]
                    
                    # Check for other active leases on same property
                    active_check_query = text("""
                        SELECT id FROM leases 
                        WHERE property_id = :property_id 
                        AND status::text = 'ACTIVE'
                        AND id != :lease_id
                    """)
                    active_result = await db.execute(active_check_query, {
                        "property_id": property_id,
                        "lease_id": int(lease_id)
                    })
                    
                    existing_active = active_result.fetchone()
                    if existing_active:
                        raise HTTPException(
                            status_code=400, 
                            detail="This property already has an active lease. Only one active lease per property is allowed. Please terminate the existing lease first."
                        )
            
            update_fields.append("status = :status")
            params["status"] = status
            
        if "monthlyRent" in lease_data or "monthly_rent" in lease_data:
            monthly_rent = float(lease_data.get("monthlyRent", lease_data.get("monthly_rent", 0)))
            update_fields.append("monthly_rent = :monthly_rent")
            params["monthly_rent"] = monthly_rent
            
        if "securityDeposit" in lease_data or "security_deposit" in lease_data:
            security_deposit = float(lease_data.get("securityDeposit", lease_data.get("security_deposit", 0)))
            update_fields.append("security_deposit = :security_deposit")
            params["security_deposit"] = security_deposit
            
        if "lateFeePenalty" in lease_data or "late_fee_penalty" in lease_data or "late_fee" in lease_data:
            late_fee = float(lease_data.get("lateFeePenalty", lease_data.get("late_fee_penalty", lease_data.get("late_fee", 0))))
            update_fields.append("late_fee = :late_fee")
            params["late_fee"] = late_fee
            
        if "gracePeriodDays" in lease_data or "grace_period_days" in lease_data or "late_fee_grace_days" in lease_data:
            grace_days = int(lease_data.get("gracePeriodDays", lease_data.get("grace_period_days", lease_data.get("late_fee_grace_days", 5))))
            update_fields.append("late_fee_grace_days = :grace_days")
            params["grace_days"] = grace_days
            
        if "startDate" in lease_data or "start_date" in lease_data:
            start_date_str = lease_data.get("startDate", lease_data.get("start_date"))
            if start_date_str:
                start_date = datetime.fromisoformat(start_date_str).date()
                update_fields.append("start_date = :start_date")
                params["start_date"] = start_date
                
        if "endDate" in lease_data or "end_date" in lease_data:
            end_date_str = lease_data.get("endDate", lease_data.get("end_date"))
            if end_date_str:
                end_date = datetime.fromisoformat(end_date_str).date()
                update_fields.append("end_date = :end_date")
                params["end_date"] = end_date
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        # Add updated timestamp
        update_fields.append("updated_at = NOW()")
        
        # Build and execute update query
        update_query = text(f"""
            UPDATE leases 
            SET {', '.join(update_fields)}
            WHERE id = :lease_id
        """)
        
        await db.execute(update_query, params)
        await db.commit()
        
        # Get the updated lease with property and tenant info
        get_lease_query = text("""
            SELECT 
                l.id, l.property_id, l.tenant_id, l.start_date, l.end_date,
                l.monthly_rent, l.security_deposit, l.late_fee, l.late_fee_grace_days,
                l.status, l.created_at, l.updated_at,
                p.title as property_title, p.address_line1, p.city,
                u.first_name, u.last_name, u.email
            FROM leases l
            LEFT JOIN properties p ON l.property_id = p.id
            LEFT JOIN users u ON l.tenant_id = u.id
            WHERE l.id = :lease_id
        """)
        
        result = await db.execute(get_lease_query, {"lease_id": int(lease_id)})
        row = result.fetchone()
        
        # Build response
        address_parts = []
        if row.address_line1:
            address_parts.append(row.address_line1)
        if row.city:
            address_parts.append(row.city)
        property_address = ", ".join(address_parts) if address_parts else "Unknown Address"
        
        tenant_name = f"{row.first_name or ''} {row.last_name or ''}".strip()
        if not tenant_name:
            tenant_name = "Unknown Tenant"
        
        response = {
            "id": str(row.id),
            "propertyId": str(row.property_id),
            "property_id": str(row.property_id),
            "tenantId": str(row.tenant_id),
            "tenant_id": str(row.tenant_id),
            "startDate": row.start_date.isoformat() if row.start_date else "",
            "start_date": row.start_date.isoformat() if row.start_date else "",
            "endDate": row.end_date.isoformat() if row.end_date else "",
            "end_date": row.end_date.isoformat() if row.end_date else "",
            "monthlyRent": float(row.monthly_rent or 0),
            "monthly_rent": float(row.monthly_rent or 0),
            "rent_amount": float(row.monthly_rent or 0),
            "securityDeposit": float(row.security_deposit or 0),
            "security_deposit": float(row.security_deposit or 0),
            "lateFeePenalty": float(row.late_fee or 0),
            "late_fee_penalty": float(row.late_fee or 0),
            "gracePeriodDays": int(row.late_fee_grace_days or 5),
            "grace_period_days": int(row.late_fee_grace_days or 5),
            "status": row.status if row.status else "pending",
            "propertyTitle": row.property_title or "Unknown Property",
            "property_title": row.property_title or "Unknown Property",
            "property_name": row.property_title or "Unknown Property",
            "propertyAddress": property_address,
            "property_address": property_address,
            "tenantName": tenant_name,
            "tenant_name": tenant_name,
            "tenantEmail": row.email or "unknown@example.com",
            "tenant_email": row.email or "unknown@example.com",
            "created_at": row.created_at.isoformat() if row.created_at else "",
            "updated_at": row.updated_at.isoformat() if row.updated_at else ""
        }
        
        logger.info(f"Updated lease in PostgreSQL: {response}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update lease error: {e}")
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update lease: {str(e)}")

@router.get("/{lease_id}")
async def get_lease(lease_id: str, db: AsyncSession = Depends(get_db)):
    """Get single lease by ID"""
    try:
        from sqlalchemy import text
        logger.info(f"Fetching lease {lease_id} from PostgreSQL")
        
        query = text("""
            SELECT 
                l.id, l.property_id, l.tenant_id, l.start_date, l.end_date,
                l.monthly_rent, l.security_deposit, l.late_fee, l.late_fee_grace_days,
                l.status, l.created_at, l.updated_at,
                p.title as property_title, p.address_line1, p.city,
                u.first_name, u.last_name, u.email
            FROM leases l
            LEFT JOIN properties p ON l.property_id = p.id
            LEFT JOIN users u ON l.tenant_id = u.id
            WHERE l.id = :lease_id
        """)
        
        result = await db.execute(query, {"lease_id": int(lease_id)})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Lease not found")
        
        # Build address
        address_parts = []
        if row.address_line1:
            address_parts.append(row.address_line1)
        if row.city:
            address_parts.append(row.city)
        property_address = ", ".join(address_parts) if address_parts else "Unknown Address"
        
        # Build tenant name
        tenant_name = f"{row.first_name or ''} {row.last_name or ''}".strip()
        if not tenant_name:
            tenant_name = "Unknown Tenant"
        
        response = {
            "id": str(row.id),
            "propertyId": str(row.property_id),
            "property_id": str(row.property_id),
            "tenantId": str(row.tenant_id),
            "tenant_id": str(row.tenant_id),
            "startDate": row.start_date.isoformat() if row.start_date else "",
            "start_date": row.start_date.isoformat() if row.start_date else "",
            "endDate": row.end_date.isoformat() if row.end_date else "",
            "end_date": row.end_date.isoformat() if row.end_date else "",
            "monthlyRent": float(row.monthly_rent or 0),
            "monthly_rent": float(row.monthly_rent or 0),
            "rent_amount": float(row.monthly_rent or 0),
            "securityDeposit": float(row.security_deposit or 0),
            "security_deposit": float(row.security_deposit or 0),
            "lateFeePenalty": float(row.late_fee or 0),
            "late_fee_penalty": float(row.late_fee or 0),
            "gracePeriodDays": int(row.late_fee_grace_days or 5),
            "grace_period_days": int(row.late_fee_grace_days or 5),
            "status": row.status if row.status else "pending",
            "propertyTitle": row.property_title or "Unknown Property",
            "property_title": row.property_title or "Unknown Property",
            "property_name": row.property_title or "Unknown Property",
            "propertyAddress": property_address,
            "property_address": property_address,
            "tenantName": tenant_name,
            "tenant_name": tenant_name,
            "tenantEmail": row.email or "unknown@example.com",
            "tenant_email": row.email or "unknown@example.com",
            "created_at": row.created_at.isoformat() if row.created_at else "",
            "updated_at": row.updated_at.isoformat() if row.updated_at else ""
        }
        
        logger.info(f"Retrieved lease from PostgreSQL: {response}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get lease error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get lease: {str(e)}")

@router.delete("/{lease_id}")
async def delete_lease(lease_id: str, db: AsyncSession = Depends(get_db)):
    """Delete lease from PostgreSQL database"""
    try:
        from sqlalchemy import text
        logger.info(f"Attempting to delete lease: {lease_id}")
        
        # Check if lease exists
        check_query = text("SELECT id FROM leases WHERE id = :lease_id")
        result = await db.execute(check_query, {"lease_id": int(lease_id)})
        lease_row = result.fetchone()
        
        if not lease_row:
            raise HTTPException(status_code=404, detail="Lease not found")
        
        # Delete the lease
        delete_query = text("DELETE FROM leases WHERE id = :lease_id")
        await db.execute(delete_query, {"lease_id": int(lease_id)})
        await db.commit()
        
        logger.info(f"Successfully deleted lease: {lease_id}")
        return {"message": "Lease deleted successfully", "lease_id": lease_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting lease {lease_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete lease: {str(e)}")

@router.post("/{lease_id}/renew")
async def renew_lease(lease_id: str, renewal_data: dict, db: AsyncSession = Depends(get_db)):
    """Renew an existing lease with new terms"""
    try:
        from sqlalchemy import text
        from src.services.payment_service import PaymentService
        
        logger.info(f"Renewing lease {lease_id} with data: {renewal_data}")
        
        # Get the original lease
        get_lease_query = text("""
            SELECT 
                l.id, l.property_id, l.tenant_id, l.start_date, l.end_date,
                l.monthly_rent, l.security_deposit, l.late_fee, l.late_fee_grace_days,
                l.status, l.created_at, l.updated_at,
                p.title as property_title, p.address_line1, p.city,
                u.first_name, u.last_name, u.email
            FROM leases l
            LEFT JOIN properties p ON l.property_id = p.id
            LEFT JOIN users u ON l.tenant_id = u.id
            WHERE l.id = :lease_id
        """)
        
        result = await db.execute(get_lease_query, {"lease_id": int(lease_id)})
        original_lease = result.fetchone()
        
        if not original_lease:
            raise HTTPException(status_code=404, detail="Original lease not found")
        
        # Extract renewal data
        new_start_date = datetime.fromisoformat(renewal_data.get("newStartDate")).date()
        new_end_date = datetime.fromisoformat(renewal_data.get("newEndDate")).date()
        new_monthly_rent = float(renewal_data.get("newMonthlyRent", original_lease.monthly_rent))
        new_security_deposit = float(renewal_data.get("newSecurityDeposit", 0))  # Usually 0 for renewals
        renewal_type = renewal_data.get("renewalType", "fixed")
        notes = renewal_data.get("notes", "")
        
        # Create the renewed lease
        create_query = text("""
            INSERT INTO leases (
                property_id, tenant_id, start_date, end_date, monthly_rent, 
                security_deposit, late_fee, late_fee_grace_days, status, 
                created_at, updated_at
            ) VALUES (
                :property_id, :tenant_id, :start_date, :end_date, :monthly_rent,
                :security_deposit, :late_fee, :grace_days, 'active',
                NOW(), NOW()
            ) RETURNING id
        """)
        
        renewal_params = {
            "property_id": original_lease.property_id,
            "tenant_id": original_lease.tenant_id,
            "start_date": new_start_date,
            "end_date": new_end_date,
            "monthly_rent": new_monthly_rent,
            "security_deposit": new_security_deposit,
            "late_fee": original_lease.late_fee,
            "grace_days": original_lease.late_fee_grace_days or 5
        }
        
        result = await db.execute(create_query, renewal_params)
        new_lease_id = result.fetchone()[0]
        
        # Update the original lease status to 'renewed'
        update_original_query = text("""
            UPDATE leases 
            SET status = 'expired', 
                updated_at = NOW()
            WHERE id = :lease_id
        """)
        
        await db.execute(update_original_query, {"lease_id": int(lease_id)})
        await db.commit()
        
        # Generate payment schedule for the new lease
        payment_service = PaymentService()
        
        # Create a lease object for the payment service
        class RenewalLease:
            def __init__(self):
                self.id = str(new_lease_id)
                self.start_date = new_start_date
                self.end_date = new_end_date
                self.rent_amount = new_monthly_rent
                self.security_deposit = new_security_deposit
                self.late_fee_penalty = original_lease.late_fee
                self.grace_period_days = original_lease.late_fee_grace_days or 5
        
        renewal_lease_obj = RenewalLease()
        payment_schedule = payment_service.generate_payment_schedule(renewal_lease_obj)
        
        # Get the new lease details for response
        get_new_lease_query = text("""
            SELECT 
                l.id, l.property_id, l.tenant_id, l.start_date, l.end_date,
                l.monthly_rent, l.security_deposit, l.late_fee, l.late_fee_grace_days,
                l.status, l.created_at, l.updated_at,
                p.title as property_title, p.address_line1, p.city,
                u.first_name, u.last_name, u.email
            FROM leases l
            LEFT JOIN properties p ON l.property_id = p.id
            LEFT JOIN users u ON l.tenant_id = u.id
            WHERE l.id = :lease_id
        """)
        
        result = await db.execute(get_new_lease_query, {"lease_id": new_lease_id})
        new_lease = result.fetchone()
        
        # Build response
        address_parts = []
        if new_lease.address_line1:
            address_parts.append(new_lease.address_line1)
        if new_lease.city:
            address_parts.append(new_lease.city)
        property_address = ", ".join(address_parts) if address_parts else "Unknown Address"
        
        tenant_name = f"{new_lease.first_name or ''} {new_lease.last_name or ''}".strip()
        if not tenant_name:
            tenant_name = "Unknown Tenant"
        
        response = {
            "id": str(new_lease.id),
            "originalLeaseId": lease_id,
            "propertyId": str(new_lease.property_id),
            "property_id": str(new_lease.property_id),
            "tenantId": str(new_lease.tenant_id),
            "tenant_id": str(new_lease.tenant_id),
            "startDate": new_lease.start_date.isoformat() if new_lease.start_date else "",
            "start_date": new_lease.start_date.isoformat() if new_lease.start_date else "",
            "endDate": new_lease.end_date.isoformat() if new_lease.end_date else "",
            "end_date": new_lease.end_date.isoformat() if new_lease.end_date else "",
            "monthlyRent": float(new_lease.monthly_rent or 0),
            "monthly_rent": float(new_lease.monthly_rent or 0),
            "rent_amount": float(new_lease.monthly_rent or 0),
            "securityDeposit": float(new_lease.security_deposit or 0),
            "security_deposit": float(new_lease.security_deposit or 0),
            "lateFeePenalty": float(new_lease.late_fee or 0),
            "late_fee_penalty": float(new_lease.late_fee or 0),
            "gracePeriodDays": int(new_lease.late_fee_grace_days or 5),
            "grace_period_days": int(new_lease.late_fee_grace_days or 5),
            "status": new_lease.status,
            "propertyTitle": new_lease.property_title or "Unknown Property",
            "property_title": new_lease.property_title or "Unknown Property",
            "property_name": new_lease.property_title or "Unknown Property",
            "propertyAddress": property_address,
            "property_address": property_address,
            "tenantName": tenant_name,
            "tenant_name": tenant_name,
            "tenantEmail": new_lease.email or "unknown@example.com",
            "tenant_email": new_lease.email or "unknown@example.com",
            "created_at": new_lease.created_at.isoformat() if new_lease.created_at else "",
            "updated_at": new_lease.updated_at.isoformat() if new_lease.updated_at else "",
            "renewalType": renewal_type,
            "notes": f"Renewed from lease {lease_id}. {notes}",
            "paymentSchedule": payment_schedule
        }
        
        logger.info(f"Successfully renewed lease {lease_id} -> {new_lease_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error renewing lease {lease_id}: {e}")
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to renew lease: {str(e)}")

@router.post("/{lease_id}/documents")
async def upload_lease_documents(
    lease_id: str, 
    documents: List[UploadFile],
    db: AsyncSession = Depends(get_db)
):
    """Upload documents for a lease"""
    try:
        from fastapi import File, UploadFile, Form
        from src.services.storage_service import StorageService
        
        logger.info(f"Uploading documents for lease {lease_id}")
        
        if not documents:
            raise HTTPException(status_code=400, detail="No documents provided")
        
        # Check if lease exists
        check_lease_query = text("SELECT id FROM leases WHERE id = :lease_id")
        result = await db.execute(check_lease_query, {"lease_id": int(lease_id)})
        lease_row = result.fetchone()
        
        if not lease_row:
            raise HTTPException(status_code=404, detail="Lease not found")
        
        storage_service = StorageService()
        uploaded_urls = []
        
        # Upload each document to the DOCUMENTS_BUCKET
        for document in documents:
            if not isinstance(document, UploadFile):
                continue
                
            # Define the storage path for lease documents
            storage_path = f"leases/{lease_id}/documents"
            
            try:
                document_url = await storage_service.upload_document(
                    file=document,
                    path=storage_path,
                    user_id=lease_id,  # Using lease_id as user context
                    bucket_type="documents"  # Use documents bucket
                )
                uploaded_urls.append({
                    "filename": document.filename,
                    "url": document_url,
                    "type": "lease_document"
                })
                
            except Exception as upload_error:
                logger.error(f"Failed to upload document {document.filename}: {upload_error}")
                # Continue with other documents
                continue
        
        if not uploaded_urls:
            raise HTTPException(status_code=500, detail="Failed to upload any documents")
        
        # Store document references in database (optional)
        # You might want to create a documents table to track uploads
        
        logger.info(f"Successfully uploaded {len(uploaded_urls)} documents for lease {lease_id}")
        return {
            "message": f"Successfully uploaded {len(uploaded_urls)} documents",
            "lease_id": lease_id,
            "documents": uploaded_urls
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading documents for lease {lease_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to upload documents: {str(e)}")

@router.get("/{lease_id}/documents")
async def get_lease_documents(lease_id: str, db: AsyncSession = Depends(get_db)):
    """Get signed URLs for lease documents"""
    try:
        from src.services.storage_service import StorageService
        
        logger.info(f"Getting documents for lease {lease_id}")
        
        # Check if lease exists
        check_lease_query = text("SELECT id FROM leases WHERE id = :lease_id")
        result = await db.execute(check_lease_query, {"lease_id": int(lease_id)})
        lease_row = result.fetchone()
        
        if not lease_row:
            raise HTTPException(status_code=404, detail="Lease not found")
        
        storage_service = StorageService()
        
        # In a real implementation, you'd query a documents table
        # For now, we'll return the structure that would be expected
        documents = []
        
        # Generate signed URLs for accessing documents
        # This is a placeholder - you'd typically get document paths from your database
        storage_path = f"leases/{lease_id}/documents"
        
        return {
            "lease_id": lease_id,
            "documents": documents,
            "upload_info": {
                "bucket": "documents",
                "path": storage_path,
                "supported_formats": ["pdf", "doc", "docx", "txt", "jpg", "jpeg", "png"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting documents for lease {lease_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}")

@router.delete("/{lease_id}/documents")
async def delete_lease_document(lease_id: str, document_data: dict, db: AsyncSession = Depends(get_db)):
    """Delete a lease document"""
    try:
        from src.services.storage_service import StorageService
        
        logger.info(f"Deleting document for lease {lease_id}: {document_data}")
        
        # Check if lease exists
        check_lease_query = text("SELECT id FROM leases WHERE id = :lease_id")
        result = await db.execute(check_lease_query, {"lease_id": int(lease_id)})
        lease_row = result.fetchone()
        
        if not lease_row:
            raise HTTPException(status_code=404, detail="Lease not found")
        
        document_url = document_data.get("documentUrl")
        if not document_url:
            raise HTTPException(status_code=400, detail="Document URL is required")
        
        storage_service = StorageService()
        success = await storage_service.delete_document(document_url)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found or could not be deleted")
        
        logger.info(f"Successfully deleted document for lease {lease_id}")
        return {"message": "Document deleted successfully", "lease_id": lease_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document for lease {lease_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.get("/{lease_id}/documents/{document_id}/signed-url")
async def get_document_signed_url(lease_id: str, document_id: str, db: AsyncSession = Depends(get_db)):
    """Get a signed URL for accessing a specific document"""
    try:
        from src.services.storage_service import StorageService
        
        logger.info(f"Getting signed URL for document {document_id} in lease {lease_id}")
        
        # Check if lease exists
        check_lease_query = text("SELECT id FROM leases WHERE id = :lease_id")
        result = await db.execute(check_lease_query, {"lease_id": int(lease_id)})
        lease_row = result.fetchone()
        
        if not lease_row:
            raise HTTPException(status_code=404, detail="Lease not found")
        
        storage_service = StorageService()
        blob_name = f"leases/{lease_id}/documents/{document_id}"
        
        signed_url = storage_service.get_signed_url(blob_name, expiration_minutes=60)
        
        if not signed_url:
            raise HTTPException(status_code=404, detail="Document not found or could not generate signed URL")
        
        return {
            "lease_id": lease_id,
            "document_id": document_id,
            "signed_url": signed_url,
            "expires_in_minutes": 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting signed URL for document {document_id} in lease {lease_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get signed URL: {str(e)}")
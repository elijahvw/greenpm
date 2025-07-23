"""
Green PM - Dashboard Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
import logging

from src.core.database import get_db
from src.core.security import SecurityManager

logger = logging.getLogger(__name__)
router = APIRouter()
bearer_scheme = HTTPBearer()

class DashboardStats(BaseModel):
    total_properties: int
    active_leases: int
    pending_applications: int
    open_maintenance: int
    total_rent_collected: float
    overdue_payments: int

class TenantDashboardStats(BaseModel):
    current_lease: Optional[dict]
    next_payment_due: Optional[str]
    payment_amount: Optional[float]
    maintenance_requests: int
    messages_unread: int

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> tuple[int, str]:
    """Get current user ID and role from JWT token"""
    try:
        security_manager = SecurityManager()
        payload = security_manager.verify_token(credentials.credentials)
        user_id = int(payload.get("sub"))
        role = payload.get("role")
        
        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return user_id, role
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/stats")
async def get_dashboard_stats(
    user_info: tuple[int, str] = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics for current user"""
    try:
        user_id, role = user_info
        
        if role == 'LANDLORD':
            # Get landlord stats - simplified queries
            
            # Count properties
            prop_result = await db.execute(
                text("SELECT COUNT(*) as count FROM properties WHERE owner_id = :user_id"),
                {"user_id": user_id}
            )
            total_properties = prop_result.fetchone().count or 0
            
            # For now, return basic stats with property count and zeros for others
            # TODO: Fix enum values and implement proper counting
            return DashboardStats(
                total_properties=total_properties,
                active_leases=0,  # TODO: Fix enum values
                pending_applications=0,  # TODO: Fix enum values  
                open_maintenance=0,  # TODO: Fix enum values
                total_rent_collected=0.0,
                overdue_payments=0
            )
            
        elif role == 'TENANT':
            # Get tenant stats
            lease_result = await db.execute(
                text("""
                    SELECT l.id, l.rent_amount, l.start_date, l.end_date,
                           p.title as property_title, p.address_line1
                    FROM leases l
                    JOIN properties p ON l.property_id = p.id
                    WHERE l.tenant_id = :user_id AND l.status = 'ACTIVE'
                    LIMIT 1
                """),
                {"user_id": user_id}
            )
            
            lease_row = lease_result.fetchone()
            current_lease = None
            if lease_row:
                current_lease = {
                    "id": lease_row.id,
                    "rent_amount": float(lease_row.rent_amount),
                    "start_date": lease_row.start_date.isoformat() if lease_row.start_date else None,
                    "end_date": lease_row.end_date.isoformat() if lease_row.end_date else None,
                    "property_title": lease_row.property_title,
                    "address": lease_row.address_line1
                }
            
            # Get maintenance requests count
            maintenance_result = await db.execute(
                text("""
                    SELECT COUNT(*) as count
                    FROM maintenance_requests m
                    JOIN leases l ON m.property_id = l.property_id
                    WHERE l.tenant_id = :user_id AND m.status IN ('OPEN', 'IN_PROGRESS')
                """),
                {"user_id": user_id}
            )
            
            maintenance_count = maintenance_result.fetchone().count or 0
            
            return TenantDashboardStats(
                current_lease=current_lease,
                next_payment_due=None,  # TODO: Calculate next payment due date
                payment_amount=float(lease_row.rent_amount) if lease_row else None,
                maintenance_requests=maintenance_count,
                messages_unread=0  # TODO: Implement message counting
            )
            
        else:
            # Admin or other roles - return basic stats
            return DashboardStats(
                total_properties=0,
                active_leases=0,
                pending_applications=0,
                open_maintenance=0,
                total_rent_collected=0.0,
                overdue_payments=0
            )
            
    except Exception as e:
        import traceback
        logger.error(f"Dashboard stats error: {e}")
        logger.error(f"Dashboard stats traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard stats: {str(e)}")

@router.get("/activity")
async def get_recent_activity(
    user_info: tuple[int, str] = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get recent activity for current user"""
    try:
        user_id, role = user_info
        
        # For now, return empty activity
        # TODO: Implement actual activity tracking
        return {
            "activities": [],
            "total": 0
        }
        
    except Exception as e:
        logger.error(f"Recent activity error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch recent activity")
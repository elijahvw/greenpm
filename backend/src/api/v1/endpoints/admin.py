"""
Admin Dashboard & Management API
Handles admin-specific functionality including user management, system monitoring, and analytics
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_

from src.core.database import get_db
from src.dependencies.auth import get_current_user, require_roles
from src.models.user import User
from src.models.property import Property
from src.models.lease import Lease
from src.models.payment import Payment
from src.models.maintenance import MaintenanceRequest
from src.models.audit import AuditLog
from src.schemas.admin import (
    SystemStats,
    UserStats,
    PropertyStats,
    FinancialStats,
    ActivityLog,
    UserManagement,
    SystemHealth,
    AnalyticsReport
)
from src.services.analytics_service import AnalyticsService
from src.services.notification_service import NotificationService

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard", response_model=SystemStats)
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Get admin dashboard statistics"""
    
    # User statistics
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    landlords = db.query(User).filter(User.role == "landlord").count()
    tenants = db.query(User).filter(User.role == "tenant").count()
    
    # Property statistics
    total_properties = db.query(Property).count()
    available_properties = db.query(Property).filter(Property.status == "available").count()
    rented_properties = db.query(Property).filter(Property.status == "rented").count()
    
    # Lease statistics
    total_leases = db.query(Lease).count()
    active_leases = db.query(Lease).filter(Lease.status == "active").count()
    pending_leases = db.query(Lease).filter(Lease.status == "pending").count()
    
    # Payment statistics
    total_payments = db.query(Payment).count()
    completed_payments = db.query(Payment).filter(Payment.status == "completed").count()
    pending_payments = db.query(Payment).filter(Payment.status == "pending").count()
    
    # Current month revenue
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_revenue = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.payment_date >= current_month_start,
            Payment.status == "completed"
        )
    ).scalar() or 0
    
    # Maintenance statistics
    total_maintenance = db.query(MaintenanceRequest).count()
    open_maintenance = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.status == "open"
    ).count()
    emergency_maintenance = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.is_emergency == True
    ).count()
    
    # Recent activity
    recent_users = db.query(User).order_by(desc(User.created_at)).limit(5).all()
    recent_properties = db.query(Property).order_by(desc(Property.created_at)).limit(5).all()
    recent_leases = db.query(Lease).order_by(desc(Lease.created_at)).limit(5).all()
    
    return SystemStats(
        total_users=total_users,
        active_users=active_users,
        landlords=landlords,
        tenants=tenants,
        total_properties=total_properties,
        available_properties=available_properties,
        rented_properties=rented_properties,
        total_leases=total_leases,
        active_leases=active_leases,
        pending_leases=pending_leases,
        total_payments=total_payments,
        completed_payments=completed_payments,
        pending_payments=pending_payments,
        current_month_revenue=current_month_revenue,
        total_maintenance=total_maintenance,
        open_maintenance=open_maintenance,
        emergency_maintenance=emergency_maintenance,
        recent_users=recent_users,
        recent_properties=recent_properties,
        recent_leases=recent_leases
    )

@router.get("/users", response_model=List[UserManagement])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Get all users for management"""
    
    query = db.query(User)
    
    # Apply filters
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if search:
        query = query.filter(
            or_(
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%")
            )
        )
    
    # Order by creation date
    query = query.order_by(desc(User.created_at))
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_update: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Update user (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log the action
    audit_log = AuditLog(
        user_id=current_user.id,
        action="update_user",
        resource_type="user",
        resource_id=user_id,
        details=user_update
    )
    db.add(audit_log)
    
    # Update user
    for field, value in user_update.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    # Send notification if user was activated/deactivated
    if "is_active" in user_update:
        notification_service = NotificationService()
        background_tasks.add_task(
            notification_service.send_user_notification,
            user_id,
            current_user,
            "account_status_changed"
        )
    
    return {"message": "User updated successfully"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Delete user (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log the action
    audit_log = AuditLog(
        user_id=current_user.id,
        action="delete_user",
        resource_type="user",
        resource_id=user_id,
        details={"deleted_user_email": user.email}
    )
    db.add(audit_log)
    
    # Check if user has active leases
    active_leases = db.query(Lease).filter(
        and_(
            or_(Lease.tenant_id == user_id, Lease.landlord_id == user_id),
            Lease.status == "active"
        )
    ).count()
    
    if active_leases > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete user with active leases"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@router.get("/analytics/revenue")
async def get_revenue_analytics(
    start_date: datetime,
    end_date: datetime,
    group_by: str = "month",  # day, week, month, year
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Get revenue analytics"""
    
    analytics_service = AnalyticsService()
    revenue_data = analytics_service.get_revenue_analytics(
        db, start_date, end_date, group_by
    )
    
    return revenue_data

@router.get("/analytics/users")
async def get_user_analytics(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Get user analytics"""
    
    analytics_service = AnalyticsService()
    user_data = analytics_service.get_user_analytics(
        db, start_date, end_date
    )
    
    return user_data

@router.get("/analytics/properties")
async def get_property_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Get property analytics"""
    
    analytics_service = AnalyticsService()
    property_data = analytics_service.get_property_analytics(db)
    
    return property_data

@router.get("/activity-log", response_model=List[ActivityLog])
async def get_activity_log(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Get system activity log"""
    
    query = db.query(AuditLog)
    
    # Apply filters
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    # Order by timestamp (newest first)
    query = query.order_by(desc(AuditLog.created_at))
    
    logs = query.offset(skip).limit(limit).all()
    return logs

@router.get("/system-health", response_model=SystemHealth)
async def get_system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Get system health metrics"""
    
    # Database health
    try:
        db.execute("SELECT 1")
        database_status = "healthy"
    except Exception:
        database_status = "unhealthy"
    
    # Check for recent errors
    recent_errors = db.query(AuditLog).filter(
        and_(
            AuditLog.action == "error",
            AuditLog.created_at >= datetime.utcnow() - timedelta(hours=1)
        )
    ).count()
    
    # Check for overdue maintenance
    overdue_maintenance = db.query(MaintenanceRequest).filter(
        and_(
            MaintenanceRequest.status == "open",
            MaintenanceRequest.created_at <= datetime.utcnow() - timedelta(days=7)
        )
    ).count()
    
    # Check for failed payments
    failed_payments = db.query(Payment).filter(
        and_(
            Payment.status == "failed",
            Payment.created_at >= datetime.utcnow() - timedelta(days=1)
        )
    ).count()
    
    return SystemHealth(
        database_status=database_status,
        recent_errors=recent_errors,
        overdue_maintenance=overdue_maintenance,
        failed_payments=failed_payments,
        last_check=datetime.utcnow()
    )

@router.post("/bulk-actions/users")
async def bulk_user_actions(
    action: str,
    user_ids: List[str],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Perform bulk actions on users"""
    
    valid_actions = ["activate", "deactivate", "delete"]
    if action not in valid_actions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action. Must be one of: {valid_actions}"
        )
    
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    if len(users) != len(user_ids):
        raise HTTPException(status_code=404, detail="Some users not found")
    
    results = []
    
    for user in users:
        try:
            if action == "activate":
                user.is_active = True
                results.append({"user_id": user.id, "status": "activated"})
            
            elif action == "deactivate":
                user.is_active = False
                results.append({"user_id": user.id, "status": "deactivated"})
            
            elif action == "delete":
                # Check for active leases
                active_leases = db.query(Lease).filter(
                    and_(
                        or_(Lease.tenant_id == user.id, Lease.landlord_id == user.id),
                        Lease.status == "active"
                    )
                ).count()
                
                if active_leases > 0:
                    results.append({"user_id": user.id, "status": "error", "message": "Has active leases"})
                    continue
                
                db.delete(user)
                results.append({"user_id": user.id, "status": "deleted"})
            
            # Log the action
            audit_log = AuditLog(
                user_id=current_user.id,
                action=f"bulk_{action}_user",
                resource_type="user",
                resource_id=user.id,
                details={"bulk_action": True}
            )
            db.add(audit_log)
            
        except Exception as e:
            results.append({"user_id": user.id, "status": "error", "message": str(e)})
    
    db.commit()
    
    return {"results": results}

@router.get("/reports/monthly")
async def get_monthly_report(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Get comprehensive monthly report"""
    
    # Date range for the month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # Revenue data
    revenue = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.payment_date >= start_date,
            Payment.payment_date < end_date,
            Payment.status == "completed"
        )
    ).scalar() or 0
    
    # New users
    new_users = db.query(User).filter(
        and_(
            User.created_at >= start_date,
            User.created_at < end_date
        )
    ).count()
    
    # New properties
    new_properties = db.query(Property).filter(
        and_(
            Property.created_at >= start_date,
            Property.created_at < end_date
        )
    ).count()
    
    # New leases
    new_leases = db.query(Lease).filter(
        and_(
            Lease.created_at >= start_date,
            Lease.created_at < end_date
        )
    ).count()
    
    # Maintenance requests
    maintenance_requests = db.query(MaintenanceRequest).filter(
        and_(
            MaintenanceRequest.created_at >= start_date,
            MaintenanceRequest.created_at < end_date
        )
    ).count()
    
    return {
        "period": f"{year}-{month:02d}",
        "revenue": revenue,
        "new_users": new_users,
        "new_properties": new_properties,
        "new_leases": new_leases,
        "maintenance_requests": maintenance_requests
    }

@router.post("/notifications/broadcast")
async def broadcast_notification(
    title: str,
    message: str,
    background_tasks: BackgroundTasks,
    user_role: Optional[str] = None,
    user_ids: Optional[List[str]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Broadcast notification to users"""
    
    # Determine recipients
    if user_ids:
        recipients = db.query(User).filter(User.id.in_(user_ids)).all()
    elif user_role:
        recipients = db.query(User).filter(User.role == user_role).all()
    else:
        recipients = db.query(User).all()
    
    # Send notifications
    notification_service = NotificationService()
    for recipient in recipients:
        background_tasks.add_task(
            notification_service.send_broadcast_notification,
            recipient.id,
            title,
            message,
            current_user.id
        )
    
    # Log the action
    audit_log = AuditLog(
        user_id=current_user.id,
        action="broadcast_notification",
        resource_type="notification",
        resource_id="broadcast",
        details={
            "title": title,
            "recipient_count": len(recipients),
            "user_role": user_role
        }
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": f"Notification sent to {len(recipients)} users"}

@router.get("/export/data")
async def export_data(
    data_type: str,
    format: str = "csv",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Export system data"""
    
    valid_types = ["users", "properties", "leases", "payments", "maintenance"]
    if data_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid data type. Must be one of: {valid_types}"
        )
    
    # This would typically generate and return a file
    # For now, return a placeholder response
    return {
        "message": f"Export of {data_type} data initiated",
        "format": format,
        "start_date": start_date,
        "end_date": end_date,
        "download_url": f"/api/v1/admin/downloads/{data_type}_{format}_export.{format}"
    }
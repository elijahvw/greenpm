"""
Maintenance & Repair Management API
Handles maintenance requests, work orders, and contractor management
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from src.core.database import get_db
from src.dependencies.auth import get_current_user, require_roles
from src.models.user import User
from src.models.maintenance import MaintenanceRequest
from src.models.property import Property
from src.models.lease import Lease
from src.schemas.maintenance import (
    MaintenanceRequestCreate,
    MaintenanceRequestUpdate,
    MaintenanceRequestResponse,
    MaintenanceRequestList,
    MaintenanceStatus,
    MaintenancePriority
)
from src.services.storage_service import StorageService
from src.services.notification_service import NotificationService

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

@router.post("/requests", response_model=MaintenanceRequestResponse)
async def create_maintenance_request(
    request: MaintenanceRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new maintenance request"""
    
    # Verify property exists
    property_obj = db.query(Property).filter(Property.id == request.property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Check permissions
    if current_user.role == "tenant":
        # Verify tenant lives in the property
        lease = db.query(Lease).filter(
            and_(
                Lease.property_id == request.property_id,
                Lease.tenant_id == current_user.id,
                Lease.status == "active"
            )
        ).first()
        if not lease:
            raise HTTPException(
                status_code=403,
                detail="You don't have an active lease for this property"
            )
    elif current_user.role == "landlord":
        # Verify landlord owns the property
        if property_obj.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Create maintenance request
    db_request = MaintenanceRequest(
        **request.dict(),
        tenant_id=current_user.id if current_user.role == "tenant" else None,
        landlord_id=property_obj.owner_id,
        status="open",
        created_by=current_user.id
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # Send notification to landlord
    notification_service = NotificationService()
    background_tasks.add_task(
        notification_service.send_maintenance_notification,
        property_obj.owner_id,
        current_user,
        db_request,
        "maintenance_request_created"
    )
    
    return db_request

@router.get("/requests", response_model=MaintenanceRequestList)
async def get_maintenance_requests(
    skip: int = 0,
    limit: int = 100,
    property_id: Optional[str] = None,
    status: Optional[MaintenanceStatus] = None,
    priority: Optional[MaintenancePriority] = None,
    emergency_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get maintenance requests (filtered by user role)"""
    
    query = db.query(MaintenanceRequest)
    
    # Filter based on user role
    if current_user.role == "tenant":
        query = query.filter(MaintenanceRequest.tenant_id == current_user.id)
    elif current_user.role == "landlord":
        query = query.filter(MaintenanceRequest.landlord_id == current_user.id)
    
    # Apply additional filters
    if property_id:
        query = query.filter(MaintenanceRequest.property_id == property_id)
    
    if status:
        query = query.filter(MaintenanceRequest.status == status)
    
    if priority:
        query = query.filter(MaintenanceRequest.priority == priority)
    
    if emergency_only:
        query = query.filter(MaintenanceRequest.is_emergency == True)
    
    # Order by priority and creation date
    query = query.order_by(
        MaintenanceRequest.is_emergency.desc(),
        MaintenanceRequest.priority.desc(),
        desc(MaintenanceRequest.created_at)
    )
    
    total = query.count()
    requests = query.offset(skip).limit(limit).all()
    
    return MaintenanceRequestList(
        requests=requests,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/requests/{request_id}", response_model=MaintenanceRequestResponse)
async def get_maintenance_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific maintenance request"""
    
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    
    # Check permissions
    if current_user.role == "tenant" and request.tenant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "landlord" and request.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return request

@router.put("/requests/{request_id}", response_model=MaintenanceRequestResponse)
async def update_maintenance_request(
    request_id: str,
    request_update: MaintenanceRequestUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update maintenance request"""
    
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    
    # Check permissions
    if current_user.role == "tenant":
        if request.tenant_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Tenants can only update certain fields
        allowed_fields = ["description", "additional_notes"]
        for field in allowed_fields:
            if hasattr(request_update, field):
                value = getattr(request_update, field)
                if value is not None:
                    setattr(request, field, value)
    
    elif current_user.role == "landlord":
        if request.landlord_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Landlords can update all fields
        update_data = request_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(request, field, value)
    
    elif current_user.role == "admin":
        # Admins can update all fields
        update_data = request_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(request, field, value)
    
    request.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(request)
    
    # Send notification about status change
    if request_update.status and request.tenant_id:
        notification_service = NotificationService()
        background_tasks.add_task(
            notification_service.send_maintenance_notification,
            request.tenant_id,
            current_user,
            request,
            f"maintenance_request_{request_update.status}"
        )
    
    return request

@router.post("/requests/{request_id}/images")
async def upload_maintenance_images(
    request_id: str,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload images for maintenance request"""
    
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    
    # Check permissions
    if current_user.role == "tenant" and request.tenant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "landlord" and request.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Upload images
    storage_service = StorageService()
    uploaded_images = []
    
    for file in files:
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} is not an image"
            )
        
        image_url = await storage_service.upload_image(
            file,
            f"maintenance/{request_id}",
            current_user.id
        )
        uploaded_images.append(image_url)
    
    # Update request with image URLs
    if not request.images:
        request.images = []
    
    request.images.extend(uploaded_images)
    request.images = request.images  # Trigger SQLAlchemy update
    
    db.commit()
    
    return {"uploaded_images": uploaded_images}

# Work Order functionality disabled - WorkOrder model not available
# @router.post("/requests/{request_id}/work-order", response_model=WorkOrderResponse)
# async def create_work_order(...):

# @router.get("/work-orders", response_model=WorkOrderList)
# async def get_work_orders(...): - WorkOrder model not available

# async def get_work_order(...): - WorkOrder model not available

# async def update_work_order(...): - WorkOrder model not available

@router.post("/requests/{request_id}/close")
async def close_maintenance_request(
    request_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin")),
    resolution_notes: str = "Request completed successfully"
):
    """Close maintenance request"""
    
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    
    # Check permissions
    if current_user.role == "landlord" and request.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Close request
    request.status = "closed"
    request.completed_at = datetime.utcnow()
    request.resolution_notes = resolution_notes
    
    db.commit()
    
    # Send notification to tenant
    if request.tenant_id:
        notification_service = NotificationService()
        background_tasks.add_task(
            notification_service.send_maintenance_notification,
            request.tenant_id,
            current_user,
            request,
            "maintenance_request_closed"
        )
    
    return {"message": "Maintenance request closed successfully"}

@router.get("/dashboard/stats")
async def get_maintenance_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get maintenance statistics"""
    
    base_query = db.query(MaintenanceRequest)
    
    # Filter based on user role
    if current_user.role == "tenant":
        base_query = base_query.filter(MaintenanceRequest.tenant_id == current_user.id)
    elif current_user.role == "landlord":
        base_query = base_query.filter(MaintenanceRequest.landlord_id == current_user.id)
    
    # Get stats
    total_requests = base_query.count()
    open_requests = base_query.filter(MaintenanceRequest.status == "open").count()
    in_progress_requests = base_query.filter(MaintenanceRequest.status == "in_progress").count()
    completed_requests = base_query.filter(MaintenanceRequest.status == "completed").count()
    emergency_requests = base_query.filter(MaintenanceRequest.is_emergency == True).count()
    
    # Get recent requests
    recent_requests = base_query.order_by(desc(MaintenanceRequest.created_at)).limit(5).all()
    
    return {
        "total_requests": total_requests,
        "open_requests": open_requests,
        "in_progress_requests": in_progress_requests,
        "completed_requests": completed_requests,
        "emergency_requests": emergency_requests,
        "recent_requests": recent_requests
    }

@router.delete("/requests/{request_id}")
async def delete_maintenance_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Delete maintenance request (admin only)"""
    
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    
    db.delete(request)
    db.commit()
    
    return {"message": "Maintenance request deleted successfully"}
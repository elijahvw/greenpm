"""
Property Application Management API
Handles tenant applications, screening, and approval process
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from src.core.database import get_db
from src.dependencies.auth import get_current_user, require_roles
from src.models.user import User
from src.models.application import Application
from src.models.property import Property
from src.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationStatus,
    ApplicationList,
    ScreeningData
)
from src.services.storage_service import StorageService
from src.services.notification_service import NotificationService

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("/", response_model=ApplicationResponse)
async def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new rental application"""
    
    # Check if property exists and is available
    property_obj = db.query(Property).filter(Property.id == application.property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    if property_obj.status != "available":
        raise HTTPException(status_code=400, detail="Property is not available for rent")
    
    # Check if user already has an application for this property
    existing_application = db.query(Application).filter(
        and_(
            Application.property_id == application.property_id,
            Application.applicant_id == current_user.id,
            Application.status.in_(["pending", "approved"])
        )
    ).first()
    
    if existing_application:
        raise HTTPException(
            status_code=400, 
            detail="You already have an active application for this property"
        )
    
    # Create application
    db_application = Application(
        **application.dict(),
        applicant_id=current_user.id,
        status="pending"
    )
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    
    # Send notification to property owner
    notification_service = NotificationService()
    await notification_service.send_application_notification(
        property_obj.owner_id,
        current_user,
        property_obj,
        "new_application"
    )
    
    return db_application

@router.get("/", response_model=ApplicationList)
async def get_applications(
    skip: int = 0,
    limit: int = 100,
    property_id: Optional[str] = None,
    status: Optional[ApplicationStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get applications (filtered by user role)"""
    
    query = db.query(Application)
    
    # Filter based on user role
    if current_user.role == "tenant":
        query = query.filter(Application.applicant_id == current_user.id)
    elif current_user.role == "landlord":
        # Get applications for landlord's properties
        landlord_properties = db.query(Property.id).filter(Property.owner_id == current_user.id)
        query = query.filter(Application.property_id.in_(landlord_properties))
    
    # Apply additional filters
    if property_id:
        query = query.filter(Application.property_id == property_id)
    
    if status:
        query = query.filter(Application.status == status)
    
    # Order by creation date (newest first)
    query = query.order_by(desc(Application.created_at))
    
    total = query.count()
    applications = query.offset(skip).limit(limit).all()
    
    return ApplicationList(
        applications=applications,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific application"""
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check permissions
    if current_user.role == "tenant" and application.applicant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "landlord":
        property_obj = db.query(Property).filter(Property.id == application.property_id).first()
        if not property_obj or property_obj.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return application

@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: str,
    application_update: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update application (applicant can update, landlord can approve/reject)"""
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check permissions and allowed updates
    if current_user.role == "tenant":
        if application.applicant_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Tenants can only update their own applications if still pending
        if application.status != "pending":
            raise HTTPException(
                status_code=400, 
                detail="Cannot update application after it has been processed"
            )
        
        # Update allowed fields for tenants
        allowed_fields = [
            "annual_income", "employment_status", "employer_name",
            "previous_address", "emergency_contact_name", "emergency_contact_phone",
            "references", "additional_notes"
        ]
        
        for field in allowed_fields:
            if hasattr(application_update, field):
                value = getattr(application_update, field)
                if value is not None:
                    setattr(application, field, value)
    
    elif current_user.role == "landlord":
        # Verify landlord owns the property
        property_obj = db.query(Property).filter(Property.id == application.property_id).first()
        if not property_obj or property_obj.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Landlords can update status and screening data
        if application_update.status:
            application.status = application_update.status
        
        if application_update.screening_data:
            application.screening_data = application_update.screening_data
        
        if application_update.landlord_notes:
            application.landlord_notes = application_update.landlord_notes
    
    db.commit()
    db.refresh(application)
    
    # Send notification about status change
    if application_update.status and application_update.status != "pending":
        notification_service = NotificationService()
        await notification_service.send_application_notification(
            application.applicant_id,
            current_user,
            property_obj,
            "application_" + application_update.status
        )
    
    return application

@router.post("/{application_id}/documents")
async def upload_application_document(
    application_id: str,
    file: UploadFile = File(...),
    document_type: str = "general",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload supporting documents for application"""
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check permissions
    if current_user.role == "tenant" and application.applicant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "landlord":
        property_obj = db.query(Property).filter(Property.id == application.property_id).first()
        if not property_obj or property_obj.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Upload document
    storage_service = StorageService()
    document_url = await storage_service.upload_document(
        file,
        f"applications/{application_id}/{document_type}",
        current_user.id
    )
    
    # Update application with document URL
    if not application.documents:
        application.documents = {}
    
    application.documents[document_type] = document_url
    application.documents = application.documents  # Trigger SQLAlchemy update
    
    db.commit()
    
    return {"document_url": document_url, "document_type": document_type}

@router.post("/{application_id}/screening")
async def run_screening(
    application_id: str,
    screening_provider: str = "rentprep",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin"))
):
    """Run background screening for application"""
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Verify landlord owns the property
    if current_user.role == "landlord":
        property_obj = db.query(Property).filter(Property.id == application.property_id).first()
        if not property_obj or property_obj.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Mock screening service integration
    # In production, this would integrate with RentPrep, TransUnion, etc.
    screening_data = {
        "provider": screening_provider,
        "credit_score": 725,
        "background_check": "passed",
        "eviction_history": "none",
        "employment_verification": "verified",
        "income_verification": "verified",
        "rental_history": "positive",
        "report_date": "2024-01-15T10:00:00Z",
        "recommendations": "Approved - Good candidate"
    }
    
    application.screening_data = screening_data
    application.screening_status = "completed"
    
    db.commit()
    
    return {"message": "Screening completed", "screening_data": screening_data}

@router.post("/{application_id}/approve")
async def approve_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin"))
):
    """Approve application and create lease"""
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Verify landlord owns the property
    if current_user.role == "landlord":
        property_obj = db.query(Property).filter(Property.id == application.property_id).first()
        if not property_obj or property_obj.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Update application status
    application.status = "approved"
    
    # Reject other pending applications for the same property
    other_applications = db.query(Application).filter(
        and_(
            Application.property_id == application.property_id,
            Application.id != application_id,
            Application.status == "pending"
        )
    ).all()
    
    for other_app in other_applications:
        other_app.status = "rejected"
        other_app.landlord_notes = "Property has been leased to another applicant"
    
    # Update property status
    property_obj.status = "rented"
    
    db.commit()
    
    # Send notifications
    notification_service = NotificationService()
    await notification_service.send_application_notification(
        application.applicant_id,
        current_user,
        property_obj,
        "application_approved"
    )
    
    # Send rejection notifications to other applicants
    for other_app in other_applications:
        await notification_service.send_application_notification(
            other_app.applicant_id,
            current_user,
            property_obj,
            "application_rejected"
        )
    
    return {"message": "Application approved successfully"}

@router.post("/{application_id}/reject")
async def reject_application(
    application_id: str,
    reason: str = "Requirements not met",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin"))
):
    """Reject application"""
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Verify landlord owns the property
    if current_user.role == "landlord":
        property_obj = db.query(Property).filter(Property.id == application.property_id).first()
        if not property_obj or property_obj.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Update application
    application.status = "rejected"
    application.landlord_notes = reason
    
    db.commit()
    
    # Send notification
    notification_service = NotificationService()
    await notification_service.send_application_notification(
        application.applicant_id,
        current_user,
        property_obj,
        "application_rejected"
    )
    
    return {"message": "Application rejected"}

@router.delete("/{application_id}")
async def delete_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Delete application (admin only)"""
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    db.delete(application)
    db.commit()
    
    return {"message": "Application deleted successfully"}
"""
Lease Management API
Handles lease creation, management, renewals, and termination
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, and_, or_

from src.core.database import get_db
from src.dependencies.auth import get_current_user, require_roles
from src.models.user import User
from src.models.lease import Lease
from src.models.property import Property
from src.models.application import Application
from src.schemas.lease import (
    LeaseCreate,
    LeaseUpdate,
    LeaseResponse,
    LeaseList,
    LeaseStatus,
    LeaseTerms,
    LeaseRenewalRequest
)
from src.services.document_service import DocumentService
from src.services.notification_service import NotificationService
from src.services.payment_service import PaymentService

router = APIRouter(prefix="/leases", tags=["leases"])

# Simple GET endpoint using direct SQL to avoid ORM issues
@router.get("/")
async def get_leases(
    db: AsyncSession = Depends(get_db)
):
    """Get all leases - simplified version"""
    try:
        from sqlalchemy import text
        
        result = await db.execute(
            text("""
                SELECT l.id, l.property_id, l.tenant_id, l.start_date, l.end_date,
                       l.rent_amount, l.security_deposit, l.status,
                       p.title as property_title, p.address_line1,
                       u.first_name, u.last_name, u.email
                FROM leases l
                JOIN properties p ON l.property_id = p.id
                JOIN users u ON l.tenant_id = u.id
                ORDER BY l.created_at DESC
            """)
        )
        
        leases = []
        for row in result.fetchall():
            leases.append({
                "id": row.id,
                "property_id": row.property_id,
                "tenant_id": row.tenant_id,
                "start_date": row.start_date.isoformat() if row.start_date else None,
                "end_date": row.end_date.isoformat() if row.end_date else None,
                "rent_amount": float(row.rent_amount) if row.rent_amount else 0,
                "security_deposit": float(row.security_deposit) if row.security_deposit else 0,
                "status": row.status,
                "property_title": row.property_title,
                "property_address": row.address_line1,
                "tenant_name": f"{row.first_name} {row.last_name}",
                "tenant_email": row.email
            })
        
        return leases
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Get leases error: {e}")
        return []

@router.post("/", response_model=LeaseResponse)
async def create_lease(
    lease: LeaseCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin"))
):
    """Create a new lease"""
    
    # Verify property exists and is owned by current user
    property_obj = db.query(Property).filter(Property.id == lease.property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    if current_user.role == "landlord" and property_obj.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Verify tenant exists
    tenant = db.query(User).filter(User.id == lease.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Check for existing active lease (only one active lease per property allowed)
    existing_active_lease = db.query(Lease).filter(
        and_(
            Lease.property_id == lease.property_id,
            Lease.status == "active"
        )
    ).first()
    
    if existing_active_lease:
        raise HTTPException(
            status_code=400,
            detail=f"Property already has an active lease (ID: {existing_active_lease.id}). Please terminate the existing lease before creating a new one."
        )
    
    # Check for overlapping leases with pending status
    overlapping_lease = db.query(Lease).filter(
        and_(
            Lease.property_id == lease.property_id,
            Lease.status.in_(["pending"]),
            or_(
                and_(
                    Lease.start_date <= lease.start_date,
                    Lease.end_date >= lease.start_date
                ),
                and_(
                    Lease.start_date <= lease.end_date,
                    Lease.end_date >= lease.end_date
                ),
                and_(
                    Lease.start_date >= lease.start_date,
                    Lease.end_date <= lease.end_date
                )
            )
        )
    ).first()
    
    if overlapping_lease:
        raise HTTPException(
            status_code=400,
            detail=f"Lease dates overlap with existing pending lease (ID: {overlapping_lease.id})"
        )
    
    # Create lease
    db_lease = Lease(
        **lease.dict(),
        landlord_id=property_obj.owner_id,
        status="pending",
        created_by=current_user.id
    )
    
    db.add(db_lease)
    db.commit()
    db.refresh(db_lease)
    
    # Update property status
    property_obj.status = "rented"
    property_obj.current_tenant_id = lease.tenant_id
    
    # Mark approved application as leased
    application = db.query(Application).filter(
        and_(
            Application.property_id == lease.property_id,
            Application.applicant_id == lease.tenant_id,
            Application.status == "approved"
        )
    ).first()
    
    if application:
        application.status = "leased"
    
    db.commit()
    
    # Generate lease document
    document_service = DocumentService()
    background_tasks.add_task(
        document_service.generate_lease_document,
        db_lease.id,
        current_user.id
    )
    
    # Send notification to tenant
    notification_service = NotificationService()
    background_tasks.add_task(
        notification_service.send_lease_notification,
        tenant.id,
        current_user,
        db_lease,
        "lease_created"
    )
    
    return db_lease

@router.get("/", response_model=LeaseList)
async def get_leases(
    skip: int = 0,
    limit: int = 100,
    property_id: Optional[str] = None,
    status: Optional[LeaseStatus] = None,
    tenant_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get leases (filtered by user role)"""
    
    query = db.query(Lease)
    
    # Filter based on user role
    if current_user.role == "tenant":
        query = query.filter(Lease.tenant_id == current_user.id)
    elif current_user.role == "landlord":
        query = query.filter(Lease.landlord_id == current_user.id)
    
    # Apply additional filters
    if property_id:
        query = query.filter(Lease.property_id == property_id)
    
    if status:
        query = query.filter(Lease.status == status)
    
    if tenant_id and current_user.role in ["landlord", "admin"]:
        query = query.filter(Lease.tenant_id == tenant_id)
    
    # Order by creation date (newest first)
    query = query.order_by(desc(Lease.created_at))
    
    total = query.count()
    leases = query.offset(skip).limit(limit).all()
    
    return LeaseList(
        leases=leases,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{lease_id}", response_model=LeaseResponse)
async def get_lease(
    lease_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific lease"""
    
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    # Check permissions
    if current_user.role == "tenant" and lease.tenant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "landlord" and lease.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return lease

@router.put("/{lease_id}", response_model=LeaseResponse)
async def update_lease(
    lease_id: str,
    lease_update: LeaseUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin"))
):
    """Update lease (landlord/admin only)"""
    
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    # Check permissions
    if current_user.role == "landlord" and lease.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update allowed fields
    update_data = lease_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lease, field, value)
    
    lease.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(lease)
    
    # Send notification about changes
    notification_service = NotificationService()
    background_tasks.add_task(
        notification_service.send_lease_notification,
        lease.tenant_id,
        current_user,
        lease,
        "lease_updated"
    )
    
    return lease

@router.post("/{lease_id}/activate")
async def activate_lease(
    lease_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin"))
):
    """Activate lease (move from pending to active)"""
    
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    # Check permissions
    if current_user.role == "landlord" and lease.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if lease.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending leases can be activated"
        )
    
    lease.status = "active"
    lease.activated_at = datetime.utcnow()
    
    db.commit()
    
    # Set up recurring rent payments
    payment_service = PaymentService()
    background_tasks.add_task(
        payment_service.setup_recurring_payments,
        lease.id
    )
    
    # Send notification
    notification_service = NotificationService()
    background_tasks.add_task(
        notification_service.send_lease_notification,
        lease.tenant_id,
        current_user,
        lease,
        "lease_activated"
    )
    
    return {"message": "Lease activated successfully"}

@router.post("/{lease_id}/renew")
async def renew_lease(
    lease_id: str,
    renewal_request: LeaseRenewalRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin"))
):
    """Renew lease with new terms"""
    
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    # Check permissions
    if current_user.role == "landlord" and lease.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if lease.status != "active":
        raise HTTPException(
            status_code=400,
            detail="Only active leases can be renewed"
        )
    
    # Create new lease for renewal
    new_lease = Lease(
        property_id=lease.property_id,
        tenant_id=lease.tenant_id,
        landlord_id=lease.landlord_id,
        start_date=renewal_request.new_start_date,
        end_date=renewal_request.new_end_date,
        monthly_rent=renewal_request.new_monthly_rent or lease.monthly_rent,
        security_deposit=renewal_request.new_security_deposit or lease.security_deposit,
        lease_terms=renewal_request.new_lease_terms or lease.lease_terms,
        status="pending",
        created_by=current_user.id,
        renewed_from=lease.id
    )
    
    db.add(new_lease)
    
    # Mark current lease as renewed
    lease.status = "renewed"
    lease.renewed_to = new_lease.id
    
    db.commit()
    db.refresh(new_lease)
    
    # Generate renewal document
    document_service = DocumentService()
    background_tasks.add_task(
        document_service.generate_lease_document,
        new_lease.id,
        current_user.id
    )
    
    # Send notification to tenant
    notification_service = NotificationService()
    background_tasks.add_task(
        notification_service.send_lease_notification,
        lease.tenant_id,
        current_user,
        new_lease,
        "lease_renewal_offered"
    )
    
    return new_lease

@router.post("/{lease_id}/terminate")
async def terminate_lease(
    lease_id: str,
    termination_date: datetime,
    background_tasks: BackgroundTasks,
    reason: str = "End of lease term",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin"))
):
    """Terminate lease"""
    
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    # Check permissions
    if current_user.role == "landlord" and lease.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if lease.status not in ["active", "pending"]:
        raise HTTPException(
            status_code=400,
            detail="Only active or pending leases can be terminated"
        )
    
    # Update lease
    lease.status = "terminated"
    lease.terminated_at = datetime.utcnow()
    lease.termination_date = termination_date
    lease.termination_reason = reason
    
    # Update property status
    property_obj = db.query(Property).filter(Property.id == lease.property_id).first()
    if property_obj:
        property_obj.status = "available"
        property_obj.current_tenant_id = None
    
    db.commit()
    
    # Cancel recurring payments
    payment_service = PaymentService()
    background_tasks.add_task(
        payment_service.cancel_recurring_payments,
        lease.id
    )
    
    # Send notification
    notification_service = NotificationService()
    background_tasks.add_task(
        notification_service.send_lease_notification,
        lease.tenant_id,
        current_user,
        lease,
        "lease_terminated"
    )
    
    return {"message": "Lease terminated successfully"}

@router.get("/{lease_id}/document")
async def get_lease_document(
    lease_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get lease document URL"""
    
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    # Check permissions
    if current_user.role == "tenant" and lease.tenant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "landlord" and lease.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not lease.document_url:
        raise HTTPException(status_code=404, detail="Lease document not found")
    
    return {"document_url": lease.document_url}

@router.post("/{lease_id}/sign")
async def sign_lease(
    lease_id: str,
    signature_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sign lease document"""
    
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    # Check permissions
    if current_user.role == "tenant" and lease.tenant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "landlord" and lease.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Record signature
    if not lease.signatures:
        lease.signatures = {}
    
    lease.signatures[current_user.id] = {
        "signature": signature_data.get("signature"),
        "signed_at": datetime.utcnow().isoformat(),
        "ip_address": signature_data.get("ip_address"),
        "user_agent": signature_data.get("user_agent")
    }
    
    # Check if both parties have signed
    tenant_signed = lease.tenant_id in lease.signatures
    landlord_signed = lease.landlord_id in lease.signatures
    
    if tenant_signed and landlord_signed:
        lease.fully_signed = True
        lease.signed_at = datetime.utcnow()
        
        # Auto-activate if both parties signed
        if lease.status == "pending":
            lease.status = "active"
            lease.activated_at = datetime.utcnow()
            
            # Set up recurring payments
            payment_service = PaymentService()
            background_tasks.add_task(
                payment_service.setup_recurring_payments,
                lease.id
            )
    
    db.commit()
    
    # Send notification
    notification_service = NotificationService()
    if lease.fully_signed:
        # Notify both parties
        background_tasks.add_task(
            notification_service.send_lease_notification,
            lease.tenant_id,
            current_user,
            lease,
            "lease_fully_signed"
        )
        background_tasks.add_task(
            notification_service.send_lease_notification,
            lease.landlord_id,
            current_user,
            lease,
            "lease_fully_signed"
        )
    else:
        # Notify the other party
        other_party_id = lease.landlord_id if current_user.id == lease.tenant_id else lease.tenant_id
        background_tasks.add_task(
            notification_service.send_lease_notification,
            other_party_id,
            current_user,
            lease,
            "lease_signed"
        )
    
    return {"message": "Lease signed successfully", "fully_signed": lease.fully_signed}

@router.get("/{lease_id}/payment-schedule")
async def get_payment_schedule(
    lease_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get rent payment schedule for lease"""
    
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    # Check permissions
    if current_user.role == "tenant" and lease.tenant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "landlord" and lease.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Generate payment schedule
    payment_service = PaymentService()
    schedule = payment_service.generate_payment_schedule(lease)
    
    return {"payment_schedule": schedule}

@router.delete("/{lease_id}")
async def delete_lease(
    lease_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Delete lease (admin only)"""
    
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    # Update property status if lease was active
    if lease.status == "active":
        property_obj = db.query(Property).filter(Property.id == lease.property_id).first()
        if property_obj:
            property_obj.status = "available"
            property_obj.current_tenant_id = None
    
    db.delete(lease)
    db.commit()
    
    return {"message": "Lease deleted successfully"}
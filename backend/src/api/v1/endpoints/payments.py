"""
Payment & Financial Management API
Handles rent collection, payments, financial reporting, and late fees
"""

from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func, extract

from src.core.database import get_db
from src.dependencies.auth import get_current_user, require_roles
from src.models.user import User
from src.models.payment import Payment
from src.models.lease import Lease
from src.models.property import Property
from src.schemas.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentList,
    PaymentStatus,
    PaymentScheduleResponse,
    LateFeeResponse,
    FinancialReport,
    PaymentSummary
)
from src.services.payment_service import PaymentService
from src.services.notification_service import NotificationService

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment: PaymentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new payment"""
    
    # Verify lease exists
    lease = db.query(Lease).filter(Lease.id == payment.lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    # Check permissions
    if current_user.role == "tenant" and lease.tenant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "landlord" and lease.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create payment
    db_payment = Payment(
        **payment.dict(),
        tenant_id=lease.tenant_id,
        landlord_id=lease.landlord_id,
        property_id=lease.property_id,
        status="pending",
        created_by=current_user.id
    )
    
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    # Process payment through payment service
    payment_service = PaymentService()
    background_tasks.add_task(
        payment_service.process_payment,
        db_payment.id
    )
    
    return db_payment

@router.get("/", response_model=PaymentList)
async def get_payments(
    skip: int = 0,
    limit: int = 100,
    lease_id: Optional[str] = None,
    property_id: Optional[str] = None,
    status: Optional[PaymentStatus] = None,
    payment_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payments (filtered by user role)"""
    
    query = db.query(Payment)
    
    # Filter based on user role
    if current_user.role == "tenant":
        query = query.filter(Payment.tenant_id == current_user.id)
    elif current_user.role == "landlord":
        query = query.filter(Payment.landlord_id == current_user.id)
    
    # Apply additional filters
    if lease_id:
        query = query.filter(Payment.lease_id == lease_id)
    
    if property_id:
        query = query.filter(Payment.property_id == property_id)
    
    if status:
        query = query.filter(Payment.status == status)
    
    if payment_type:
        query = query.filter(Payment.payment_type == payment_type)
    
    if start_date:
        query = query.filter(Payment.payment_date >= start_date)
    
    if end_date:
        query = query.filter(Payment.payment_date <= end_date)
    
    # Order by payment date (newest first)
    query = query.order_by(desc(Payment.payment_date))
    
    total = query.count()
    payments = query.offset(skip).limit(limit).all()
    
    return PaymentList(
        payments=payments,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific payment"""
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check permissions
    if current_user.role == "tenant" and payment.tenant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "landlord" and payment.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return payment

@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: str,
    payment_update: PaymentUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin"))
):
    """Update payment (landlord/admin only)"""
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check permissions
    if current_user.role == "landlord" and payment.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update payment
    update_data = payment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(payment, field, value)
    
    payment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(payment)
    
    # Send notification about payment update
    notification_service = NotificationService()
    background_tasks.add_task(
        notification_service.send_payment_notification,
        payment.tenant_id,
        current_user,
        payment,
        "payment_updated"
    )
    
    return payment

# @router.post("/schedule", response_model=PaymentScheduleResponse) - PaymentSchedule model not available
async def create_payment_schedule(
    lease_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin"))
):
    """Create payment schedule for lease"""
    
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    # Check permissions
    if current_user.role == "landlord" and lease.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Generate payment schedule
    payment_service = PaymentService()
    schedule = payment_service.create_payment_schedule(lease)
    
    return schedule

# @router.get("/schedule/{lease_id}", response_model=List[PaymentScheduleResponse]) - PaymentSchedule model not available
async def get_payment_schedule(
    lease_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment schedule for lease"""
    
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    # Check permissions
    if current_user.role == "tenant" and lease.tenant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "landlord" and lease.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get payment schedule
    schedule = db.query(PaymentSchedule).filter(
        PaymentSchedule.lease_id == lease_id
    ).order_by(PaymentSchedule.due_date).all()
    
    return schedule

@router.post("/late-fees/calculate")
async def calculate_late_fees(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin")),
    lease_id: Optional[str] = None
):
    """Calculate and apply late fees"""
    
    payment_service = PaymentService()
    
    if lease_id:
        # Calculate late fees for specific lease
        lease = db.query(Lease).filter(Lease.id == lease_id).first()
        if not lease:
            raise HTTPException(status_code=404, detail="Lease not found")
        
        # Check permissions
        if current_user.role == "landlord" and lease.landlord_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        late_fees = payment_service.calculate_late_fees(lease_id)
    else:
        # Calculate late fees for all landlord's leases
        if current_user.role == "landlord":
            leases = db.query(Lease).filter(Lease.landlord_id == current_user.id).all()
            late_fees = []
            for lease in leases:
                lease_fees = payment_service.calculate_late_fees(lease.id)
                late_fees.extend(lease_fees)
        else:
            # Admin can calculate for all leases
            late_fees = payment_service.calculate_all_late_fees()
    
    return {"late_fees_calculated": len(late_fees), "late_fees": late_fees}

@router.get("/late-fees", response_model=List[LateFeeResponse])
async def get_late_fees(
    lease_id: Optional[str] = None,
    unpaid_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get late fees"""
    
    query = db.query(LateFee)
    
    # Filter based on user role
    if current_user.role == "tenant":
        # Get tenant's late fees
        tenant_leases = db.query(Lease.id).filter(Lease.tenant_id == current_user.id)
        query = query.filter(LateFee.lease_id.in_(tenant_leases))
    elif current_user.role == "landlord":
        # Get landlord's late fees
        landlord_leases = db.query(Lease.id).filter(Lease.landlord_id == current_user.id)
        query = query.filter(LateFee.lease_id.in_(landlord_leases))
    
    # Apply additional filters
    if lease_id:
        query = query.filter(LateFee.lease_id == lease_id)
    
    if unpaid_only:
        query = query.filter(LateFee.paid == False)
    
    # Order by due date
    query = query.order_by(desc(LateFee.due_date))
    
    late_fees = query.all()
    return late_fees

@router.get("/reports/financial", response_model=FinancialReport)
async def get_financial_report(
    start_date: datetime,
    end_date: datetime,
    property_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin"))
):
    """Get financial report"""
    
    # Base query for payments
    query = db.query(Payment).filter(
        and_(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date,
            Payment.status == "completed"
        )
    )
    
    # Filter based on user role
    if current_user.role == "landlord":
        query = query.filter(Payment.landlord_id == current_user.id)
    
    # Filter by property if specified
    if property_id:
        query = query.filter(Payment.property_id == property_id)
    
    # Calculate totals
    total_rent = query.filter(Payment.payment_type == "rent").with_entities(
        func.sum(Payment.amount)
    ).scalar() or 0
    
    total_late_fees = query.filter(Payment.payment_type == "late_fee").with_entities(
        func.sum(Payment.amount)
    ).scalar() or 0
    
    total_security_deposits = query.filter(Payment.payment_type == "security_deposit").with_entities(
        func.sum(Payment.amount)
    ).scalar() or 0
    
    total_other = query.filter(Payment.payment_type == "other").with_entities(
        func.sum(Payment.amount)
    ).scalar() or 0
    
    # Get monthly breakdown
    monthly_breakdown = db.query(
        extract('month', Payment.payment_date).label('month'),
        extract('year', Payment.payment_date).label('year'),
        func.sum(Payment.amount).label('total')
    ).filter(
        and_(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date,
            Payment.status == "completed"
        )
    )
    
    if current_user.role == "landlord":
        monthly_breakdown = monthly_breakdown.filter(Payment.landlord_id == current_user.id)
    
    if property_id:
        monthly_breakdown = monthly_breakdown.filter(Payment.property_id == property_id)
    
    monthly_breakdown = monthly_breakdown.group_by(
        extract('year', Payment.payment_date),
        extract('month', Payment.payment_date)
    ).all()
    
    # Get property breakdown
    property_breakdown = db.query(
        Property.name,
        Property.address,
        func.sum(Payment.amount).label('total')
    ).join(Payment, Property.id == Payment.property_id).filter(
        and_(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date,
            Payment.status == "completed"
        )
    )
    
    if current_user.role == "landlord":
        property_breakdown = property_breakdown.filter(Payment.landlord_id == current_user.id)
    
    if property_id:
        property_breakdown = property_breakdown.filter(Payment.property_id == property_id)
    
    property_breakdown = property_breakdown.group_by(
        Property.id, Property.name, Property.address
    ).all()
    
    return FinancialReport(
        start_date=start_date,
        end_date=end_date,
        total_rent=total_rent,
        total_late_fees=total_late_fees,
        total_security_deposits=total_security_deposits,
        total_other=total_other,
        total_income=total_rent + total_late_fees + total_security_deposits + total_other,
        monthly_breakdown=monthly_breakdown,
        property_breakdown=property_breakdown
    )

@router.get("/summary", response_model=PaymentSummary)
async def get_payment_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment summary for dashboard"""
    
    # Base query
    query = db.query(Payment)
    
    # Filter based on user role
    if current_user.role == "tenant":
        query = query.filter(Payment.tenant_id == current_user.id)
    elif current_user.role == "landlord":
        query = query.filter(Payment.landlord_id == current_user.id)
    
    # Calculate totals
    total_payments = query.count()
    completed_payments = query.filter(Payment.status == "completed").count()
    pending_payments = query.filter(Payment.status == "pending").count()
    failed_payments = query.filter(Payment.status == "failed").count()
    
    # Current month totals
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_total = query.filter(
        and_(
            Payment.payment_date >= current_month_start,
            Payment.status == "completed"
        )
    ).with_entities(func.sum(Payment.amount)).scalar() or 0
    
    # Outstanding payments (overdue)
    today = datetime.now().date()
    overdue_payments = db.query(PaymentSchedule).filter(
        and_(
            PaymentSchedule.due_date < today,
            PaymentSchedule.paid == False
        )
    )
    
    if current_user.role == "tenant":
        tenant_leases = db.query(Lease.id).filter(Lease.tenant_id == current_user.id)
        overdue_payments = overdue_payments.filter(PaymentSchedule.lease_id.in_(tenant_leases))
    elif current_user.role == "landlord":
        landlord_leases = db.query(Lease.id).filter(Lease.landlord_id == current_user.id)
        overdue_payments = overdue_payments.filter(PaymentSchedule.lease_id.in_(landlord_leases))
    
    overdue_count = overdue_payments.count()
    overdue_amount = overdue_payments.with_entities(func.sum(PaymentSchedule.amount)).scalar() or 0
    
    # Recent payments
    recent_payments = query.order_by(desc(Payment.created_at)).limit(5).all()
    
    return PaymentSummary(
        total_payments=total_payments,
        completed_payments=completed_payments,
        pending_payments=pending_payments,
        failed_payments=failed_payments,
        current_month_total=current_month_total,
        overdue_count=overdue_count,
        overdue_amount=overdue_amount,
        recent_payments=recent_payments
    )

@router.post("/{payment_id}/refund")
async def refund_payment(
    payment_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("landlord", "admin")),
    refund_amount: Optional[Decimal] = None,
    reason: str = "Refund requested"
):
    """Refund payment"""
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check permissions
    if current_user.role == "landlord" and payment.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if payment.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Only completed payments can be refunded"
        )
    
    # Process refund
    payment_service = PaymentService()
    refund_result = payment_service.process_refund(
        payment_id,
        refund_amount or payment.amount,
        reason
    )
    
    # Update payment status
    payment.status = "refunded"
    payment.refund_amount = refund_amount or payment.amount
    payment.refund_reason = reason
    payment.refunded_at = datetime.utcnow()
    
    db.commit()
    
    # Send notification
    notification_service = NotificationService()
    background_tasks.add_task(
        notification_service.send_payment_notification,
        payment.tenant_id,
        current_user,
        payment,
        "payment_refunded"
    )
    
    return {"message": "Payment refunded successfully", "refund_result": refund_result}

@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Delete payment (admin only)"""
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    db.delete(payment)
    db.commit()
    
    return {"message": "Payment deleted successfully"}
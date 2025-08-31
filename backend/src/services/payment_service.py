"""
Payment Service
Handles payment processing, recurring payments, and financial calculations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.models.payment import Payment
from src.models.lease import Lease


class PaymentService:
    """Service for handling payments and financial operations"""
    
    def __init__(self):
        self.stripe_service = None  # Initialize when needed
        
    async def process_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a payment through payment gateway"""
        # TODO: Implement Stripe/payment gateway integration
        return {
            "status": "success",
            "payment_id": "temp_payment_id",
            "message": "Payment processed successfully"
        }
    
    def create_payment_schedule(self, lease: Lease) -> Dict[str, Any]:
        """Create payment schedule for a lease"""
        # TODO: Implement payment schedule creation
        return {
            "lease_id": lease.id,
            "amount": lease.rent_amount or 0,
            "due_date": datetime.now().replace(day=1).isoformat(),
            "status": "scheduled"
        }
    
    def calculate_late_fees(self, lease_id: str) -> List[Dict[str, Any]]:
        """Calculate late fees for a lease"""
        # TODO: Implement late fee calculation logic
        return []
    
    def calculate_all_late_fees(self) -> List[Dict[str, Any]]:
        """Calculate late fees for all overdue payments"""
        # TODO: Implement comprehensive late fee calculation
        return []
    
    async def process_refund(self, payment_id: str, amount: Decimal, reason: str) -> Dict[str, Any]:
        """Process a payment refund"""
        # TODO: Implement refund processing
        return {
            "status": "success",
            "refund_id": "temp_refund_id",
            "amount": amount,
            "reason": reason
        }
    
    async def setup_recurring_payments(self, lease_id: str) -> Dict[str, Any]:
        """Setup recurring payments for a lease"""
        # TODO: Implement recurring payment setup
        return {
            "status": "success",
            "message": "Recurring payments setup successfully"
        }
    
    async def cancel_recurring_payments(self, lease_id: str) -> Dict[str, Any]:
        """Cancel recurring payments for a lease"""
        # TODO: Implement recurring payment cancellation
        return {
            "status": "success",
            "message": "Recurring payments cancelled successfully"
        }
    
    def generate_payment_schedule(self, lease: Lease) -> List[Dict[str, Any]]:
        """Generate comprehensive payment schedule for a lease"""
        schedule = []
        
        if not (lease.start_date and lease.end_date and lease.rent_amount):
            return schedule
            
        try:
            # Handle different date formats
            if isinstance(lease.start_date, str):
                start_date = datetime.fromisoformat(lease.start_date.replace('Z', '+00:00'))
            else:
                start_date = lease.start_date
                
            if isinstance(lease.end_date, str):
                end_date = datetime.fromisoformat(lease.end_date.replace('Z', '+00:00'))
            else:
                end_date = lease.end_date
            
            current_date = start_date.replace(day=1)  # Start from first day of month
            
            # Generate monthly rent payments
            while current_date <= end_date:
                # Calculate due date (typically first of the month)
                due_date = current_date
                
                # Create payment entry
                payment_entry = {
                    "lease_id": lease.id,
                    "due_date": due_date.isoformat(),
                    "amount": float(lease.rent_amount),
                    "type": "rent",
                    "status": "scheduled",
                    "description": f"Monthly rent for {due_date.strftime('%B %Y')}",
                    "late_fee_amount": float(lease.late_fee_penalty) if lease.late_fee_penalty else 0,
                    "grace_period_days": lease.grace_period_days if hasattr(lease, 'grace_period_days') else 5
                }
                
                # Add late fee information if applicable
                if lease.late_fee_penalty and lease.late_fee_penalty > 0:
                    grace_period = lease.grace_period_days if hasattr(lease, 'grace_period_days') else 5
                    late_fee_date = due_date + timedelta(days=grace_period + 1)
                    payment_entry["late_fee_date"] = late_fee_date.isoformat()
                
                schedule.append(payment_entry)
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            # Add security deposit entry if applicable
            if lease.security_deposit and lease.security_deposit > 0:
                security_deposit_entry = {
                    "lease_id": lease.id,
                    "due_date": start_date.isoformat(),
                    "amount": float(lease.security_deposit),
                    "type": "security_deposit",
                    "status": "scheduled",
                    "description": "Security deposit payment",
                    "one_time": True
                }
                schedule.insert(0, security_deposit_entry)  # Add at beginning
            
            # Add pet deposit if applicable
            if hasattr(lease, 'pet_policy') and lease.pet_policy and lease.pet_policy.get('deposit', 0) > 0:
                pet_deposit_entry = {
                    "lease_id": lease.id,
                    "due_date": start_date.isoformat(),
                    "amount": float(lease.pet_policy['deposit']),
                    "type": "pet_deposit",
                    "status": "scheduled",
                    "description": "Pet deposit payment",
                    "one_time": True
                }
                schedule.insert(-1, pet_deposit_entry)  # Add before regular rent payments
            
            # Add monthly pet fees if applicable
            if hasattr(lease, 'pet_policy') and lease.pet_policy and lease.pet_policy.get('monthlyFee', 0) > 0:
                current_date = start_date.replace(day=1)
                while current_date <= end_date:
                    pet_fee_entry = {
                        "lease_id": lease.id,
                        "due_date": current_date.isoformat(),
                        "amount": float(lease.pet_policy['monthlyFee']),
                        "type": "pet_fee",
                        "status": "scheduled",
                        "description": f"Monthly pet fee for {current_date.strftime('%B %Y')}"
                    }
                    schedule.append(pet_fee_entry)
                    
                    # Move to next month
                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)
            
        except Exception as e:
            logger.error(f"Error generating payment schedule: {e}")
            return []
        
        return schedule
    
    def create_renewal_payment_schedule(self, original_lease: Lease, new_start_date: datetime, new_end_date: datetime, new_rent_amount: Optional[float] = None) -> List[Dict[str, Any]]:
        """Create payment schedule for a renewed lease"""
        # Create a temporary lease object for renewal
        renewal_lease = type('RenewalLease', (), {
            'id': original_lease.id + '_renewal',
            'start_date': new_start_date,
            'end_date': new_end_date,
            'rent_amount': new_rent_amount or original_lease.rent_amount,
            'security_deposit': 0,  # Usually not required for renewals
            'late_fee_penalty': original_lease.late_fee_penalty,
            'grace_period_days': getattr(original_lease, 'grace_period_days', 5),
            'pet_policy': getattr(original_lease, 'pet_policy', None)
        })()
        
        return self.generate_payment_schedule(renewal_lease)
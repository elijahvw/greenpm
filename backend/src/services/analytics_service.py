"""
Green PM - Analytics Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_, or_, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from src.models.user import User, UserRole
from src.models.property import Property
from src.models.lease import Lease, LeaseStatus
from src.models.payment import Payment, PaymentStatus
from src.models.maintenance import MaintenanceRequest

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        try:
            # Count users
            user_count = await self.db.execute(
                select(func.count(User.id))
            )
            total_users = user_count.scalar() or 0
            
            active_users = await self.db.execute(
                select(func.count(User.id)).where(User.is_active == True)
            )
            active_users_count = active_users.scalar() or 0
            
            # Count properties
            property_count = await self.db.execute(
                select(func.count(Property.id))
            )
            total_properties = property_count.scalar() or 0
            
            # Count leases
            lease_count = await self.db.execute(
                select(func.count(Lease.id))
            )
            total_leases = lease_count.scalar() or 0
            
            active_lease_count = await self.db.execute(
                select(func.count(Lease.id)).where(Lease.status == LeaseStatus.ACTIVE)
            )
            active_leases = active_lease_count.scalar() or 0
            
            # Count payments
            payment_count = await self.db.execute(
                select(func.count(Payment.id))
            )
            total_payments = payment_count.scalar() or 0
            
            # Calculate total revenue
            revenue = await self.db.execute(
                select(func.sum(Payment.amount)).where(
                    Payment.status == PaymentStatus.COMPLETED
                )
            )
            total_revenue = float(revenue.scalar() or 0)
            
            # Count pending maintenance
            pending_maintenance = await self.db.execute(
                select(func.count(MaintenanceRequest.id)).where(
                    MaintenanceRequest.status.in_(['pending', 'in_progress'])
                )
            )
            pending_maintenance_count = pending_maintenance.scalar() or 0
            
            return {
                "total_users": total_users,
                "active_users": active_users_count,
                "total_properties": total_properties,
                "total_leases": total_leases,
                "active_leases": active_leases,
                "total_payments": total_payments,
                "total_revenue": total_revenue,
                "pending_maintenance": pending_maintenance_count,
                "system_health": "healthy",
                "server_uptime": "0d 0h 0m",
                "database_status": "connected",
                "recent_registrations": 0,
                "recent_payments": 0,
                "recent_maintenance": 0
            }
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            raise

    async def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            # Total users by role
            landlords = await self.db.execute(
                select(func.count(User.id)).where(User.role == UserRole.LANDLORD)
            )
            landlords_count = landlords.scalar() or 0
            
            tenants = await self.db.execute(
                select(func.count(User.id)).where(User.role == UserRole.TENANT)
            )
            tenants_count = tenants.scalar() or 0
            
            property_managers = await self.db.execute(
                select(func.count(User.id)).where(User.role == UserRole.PROPERTY_MANAGER)
            )
            property_managers_count = property_managers.scalar() or 0
            
            # Active vs inactive
            total_users = landlords_count + tenants_count + property_managers_count
            
            active_users = await self.db.execute(
                select(func.count(User.id)).where(User.is_active == True)
            )
            active_users_count = active_users.scalar() or 0
            
            return {
                "total_users": total_users,
                "active_users": active_users_count,
                "landlords": landlords_count,
                "tenants": tenants_count,
                "property_managers": property_managers_count,
                "pending_users": 0,
                "suspended_users": 0,
                "new_users_this_month": 0,
                "user_growth_rate": 0.0
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            raise

    async def get_property_analytics(self) -> Dict[str, Any]:
        """Get property analytics"""
        try:
            # Total properties
            total_properties = await self.db.execute(
                select(func.count(Property.id))
            )
            total_count = total_properties.scalar() or 0
            
            # Occupied vs vacant (based on active leases)
            occupied = await self.db.execute(
                select(func.count(Property.id.distinct())).select_from(
                    Property.__table__.join(
                        Lease.__table__,
                        Property.id == Lease.property_id
                    )
                ).where(Lease.status == LeaseStatus.ACTIVE)
            )
            occupied_count = occupied.scalar() or 0
            vacant_count = total_count - occupied_count
            
            # Average rent
            avg_rent = await self.db.execute(
                select(func.avg(Lease.monthly_rent)).where(
                    Lease.status == LeaseStatus.ACTIVE
                )
            )
            average_rent = float(avg_rent.scalar() or 0)
            
            return {
                "total_properties": total_count,
                "occupied_properties": occupied_count,
                "vacant_properties": vacant_count,
                "maintenance_pending": 0,
                "average_rent": average_rent,
                "total_square_footage": None,
                "properties_by_type": {},
                "properties_by_location": {}
            }
            
        except Exception as e:
            logger.error(f"Error getting property analytics: {e}")
            raise

    async def get_financial_analytics(self) -> Dict[str, Any]:
        """Get financial analytics"""
        try:
            # Total revenue
            total_revenue = await self.db.execute(
                select(func.sum(Payment.amount)).where(
                    Payment.status == PaymentStatus.COMPLETED
                )
            )
            total_revenue_amount = float(total_revenue.scalar() or 0)
            
            # Monthly revenue (current month)
            current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_revenue = await self.db.execute(
                select(func.sum(Payment.amount)).where(
                    and_(
                        Payment.status == PaymentStatus.COMPLETED,
                        Payment.created_at >= current_month_start
                    )
                )
            )
            monthly_revenue_amount = float(monthly_revenue.scalar() or 0)
            
            # Outstanding rent (pending payments)
            outstanding_rent = await self.db.execute(
                select(func.sum(Payment.amount)).where(
                    Payment.status == PaymentStatus.PENDING
                )
            )
            outstanding_amount = float(outstanding_rent.scalar() or 0)
            
            return {
                "total_revenue": total_revenue_amount,
                "monthly_revenue": monthly_revenue_amount,
                "outstanding_rent": outstanding_amount,
                "security_deposits": 0.0,
                "maintenance_costs": 0.0,
                "average_rent_per_unit": 0.0,
                "collection_rate": 0.0,
                "revenue_trend": []
            }
            
        except Exception as e:
            logger.error(f"Error getting financial analytics: {e}")
            raise

    async def get_maintenance_analytics(self) -> Dict[str, Any]:
        """Get maintenance analytics"""
        try:
            # Count requests by status
            total_requests = await self.db.execute(
                select(func.count(MaintenanceRequest.id))
            )
            total_count = total_requests.scalar() or 0
            
            pending_requests = await self.db.execute(
                select(func.count(MaintenanceRequest.id)).where(
                    MaintenanceRequest.status == 'pending'
                )
            )
            pending_count = pending_requests.scalar() or 0
            
            in_progress_requests = await self.db.execute(
                select(func.count(MaintenanceRequest.id)).where(
                    MaintenanceRequest.status == 'in_progress'
                )
            )
            in_progress_count = in_progress_requests.scalar() or 0
            
            completed_requests = await self.db.execute(
                select(func.count(MaintenanceRequest.id)).where(
                    MaintenanceRequest.status == 'completed'
                )
            )
            completed_count = completed_requests.scalar() or 0
            
            return {
                "total_requests": total_count,
                "pending_requests": pending_count,
                "in_progress_requests": in_progress_count,
                "completed_requests": completed_count,
                "overdue_requests": 0,
                "average_completion_time": 0.0,
                "total_maintenance_cost": 0.0,
                "requests_by_priority": {},
                "requests_by_category": {}
            }
            
        except Exception as e:
            logger.error(f"Error getting maintenance analytics: {e}")
            raise

    async def get_revenue_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get revenue trend over specified days"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # This would normally query payments grouped by date
            # For now, returning empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting revenue trend: {e}")
            raise

    async def get_user_activity(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get user activity over specified days"""
        try:
            # This would normally query user activity logs
            # For now, returning empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting user activity: {e}")
            raise
"""
Green PM - User Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
import logging

from src.models.user import User, UserRole, UserStatus
from src.schemas.user import UserUpdate, UserProfileUpdate, UserPreferencesUpdate

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_uuid(self, uuid: str) -> Optional[User]:
        """Get user by UUID"""
        stmt = select(User).where(User.uuid == uuid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        """Get user by Firebase UID"""
        stmt = select(User).where(User.firebase_uid == firebase_uid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user_profile(self, user_id: int, profile_data: UserProfileUpdate) -> Optional[User]:
        """Update user profile"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        # Update fields
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user_preferences(self, user_id: int, preferences: UserPreferencesUpdate) -> Optional[User]:
        """Update user notification preferences"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        # Update preferences
        update_data = preferences.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user_status(self, user_id: int, status: UserStatus) -> Optional[User]:
        """Update user status"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.status = status
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user_role(self, user_id: int, role: UserRole) -> Optional[User]:
        """Update user role"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.role = role
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> bool:
        """Delete user (soft delete by setting status to inactive)"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        user.status = UserStatus.INACTIVE
        await self.db.commit()
        return True

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 20,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None
    ) -> tuple[List[User], int]:
        """Get users with filtering and pagination"""
        
        # Build query
        stmt = select(User)
        count_stmt = select(func.count(User.id))
        
        # Apply filters
        conditions = []
        
        if role:
            conditions.append(User.role == role)
        
        if status:
            conditions.append(User.status == status)
        
        if search:
            search_term = f"%{search}%"
            conditions.append(
                or_(
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.email.ilike(search_term)
                )
            )
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))
        
        # Get total count
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        stmt = stmt.order_by(User.created_at.desc()).offset(skip).limit(limit)
        
        # Execute query
        result = await self.db.execute(stmt)
        users = result.scalars().all()
        
        return list(users), total

    async def get_landlords(self, skip: int = 0, limit: int = 20) -> tuple[List[User], int]:
        """Get all landlords"""
        return await self.get_users(skip=skip, limit=limit, role=UserRole.LANDLORD)

    async def get_tenants(self, skip: int = 0, limit: int = 20) -> tuple[List[User], int]:
        """Get all tenants"""
        return await self.get_users(skip=skip, limit=limit, role=UserRole.TENANT)

    async def verify_email(self, user_id: int) -> Optional[User]:
        """Mark user email as verified"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.email_verified = True
        if user.status == UserStatus.PENDING:
            user.status = UserStatus.ACTIVE

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def verify_phone(self, user_id: int) -> Optional[User]:
        """Mark user phone as verified"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.phone_verified = True
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def verify_identity(self, user_id: int) -> Optional[User]:
        """Mark user identity as verified"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.identity_verified = True
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def enable_two_factor(self, user_id: int, secret: str) -> Optional[User]:
        """Enable two-factor authentication"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.two_factor_enabled = True
        user.two_factor_secret = secret
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def disable_two_factor(self, user_id: int) -> Optional[User]:
        """Disable two-factor authentication"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.two_factor_enabled = False
        user.two_factor_secret = None
        await self.db.commit()
        await self.db.refresh(user)
        return user
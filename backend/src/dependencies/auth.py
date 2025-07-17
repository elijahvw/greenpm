"""
Green PM - Authentication Dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from src.core.database import get_db
from src.core.security import security
from src.services.user_service import UserService
from src.models.user import User, UserRole

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    try:
        # Verify token
        payload = security.verify_token(credentials.credentials)
        user_id = int(payload.get("sub"))
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        # Get user from database
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_landlord(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current landlord user"""
    if not current_user.is_landlord:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_current_tenant(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current tenant user"""
    if not current_user.is_tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_current_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current admin user"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_roles(*roles: UserRole):
    """Dependency factory for role-based access control"""
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    
    return role_checker

# Optional authentication (for public endpoints that can benefit from user context)
async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        payload = security.verify_token(credentials.credentials)
        user_id = int(payload.get("sub"))
        
        if user_id is None:
            return None
        
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        
        return user if user and user.is_active else None
        
    except Exception:
        return None
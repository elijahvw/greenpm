"""
Green PM - Authentication Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
import logging

from src.core.database import get_db
from src.core.security import security
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.schemas.auth import (
    LoginRequest, LoginResponse, RegisterRequest, RegisterResponse,
    RefreshTokenRequest, PasswordResetRequest, PasswordResetConfirmRequest,
    ChangePasswordRequest
)
from src.schemas.user import UserResponse
from src.dependencies.auth import get_current_user, get_current_active_user
from src.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()
bearer_scheme = HTTPBearer()

@router.post("/register", response_model=RegisterResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.register_user(request)
        
        # Generate access token
        access_token = security.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        
        return RegisterResponse(
            user=UserResponse.from_orm(user),
            access_token=access_token,
            token_type="bearer"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.authenticate_user(request.email, request.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Generate access token
        access_token = security.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        
        # Update last login
        await auth_service.update_last_login(user.id)
        
        return LoginResponse(
            user=UserResponse.from_orm(user),
            access_token=access_token,
            token_type="bearer"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/firebase-login", response_model=LoginResponse)
async def firebase_login(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Login with Firebase token"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.authenticate_firebase_user(credentials.credentials)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Firebase token"
            )
        
        # Generate access token
        access_token = security.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        
        return LoginResponse(
            user=UserResponse.from_orm(user),
            access_token=access_token,
            token_type="bearer"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Firebase login error: {e}")
        raise HTTPException(status_code=500, detail="Firebase login failed")

@router.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    try:
        # Verify the refresh token
        payload = security.verify_token(request.refresh_token)
        user_id = int(payload.get("sub"))
        
        # Get user
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Generate new access token
        access_token = security.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )

@router.post("/password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset"""
    try:
        auth_service = AuthService(db)
        await auth_service.request_password_reset(request.email)
        
        return {"message": "Password reset email sent if account exists"}
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        # Always return success to prevent email enumeration
        return {"message": "Password reset email sent if account exists"}

@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    db: AsyncSession = Depends(get_db)
):
    """Confirm password reset"""
    try:
        auth_service = AuthService(db)
        await auth_service.reset_password(request.token, request.new_password)
        
        return {"message": "Password reset successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Password reset confirm error: {e}")
        raise HTTPException(status_code=500, detail="Password reset failed")

@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    try:
        auth_service = AuthService(db)
        await auth_service.change_password(
            current_user.id,
            request.current_password,
            request.new_password
        )
        
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(status_code=500, detail="Password change failed")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return UserResponse.from_orm(current_user)

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout user (invalidate token on client side)"""
    # In a stateless JWT system, logout is handled client-side
    # But we can log the logout event for audit purposes
    try:
        auth_service = AuthService(db)
        await auth_service.log_logout(current_user.id)
        
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"message": "Logged out successfully"}  # Always return success
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
    """Login user - simplified version bypassing ORM issues"""
    try:
        from sqlalchemy import text
        from src.core.security import SecurityManager
        
        logger.info(f"🔐 Login attempt for: {request.email}")
        
        # Get user directly with raw SQL to avoid relationship issues
        result = await db.execute(
            text("""
                SELECT id, uuid, email, hashed_password, role, status, first_name, last_name,
                       phone, avatar_url, bio, address_line1, address_line2, city, state, 
                       zip_code, country, email_verified, phone_verified, identity_verified,
                       two_factor_enabled, notification_email, notification_sms, 
                       notification_push, created_at, updated_at, last_login,
                       date_of_birth, social_security_number, notes, move_in_date, move_out_date,
                       employer, position, monthly_income, employment_start_date,
                       emergency_contact_name, emergency_contact_phone, emergency_contact_relationship
                FROM users 
                WHERE email = :email
            """),
            {"email": request.email}
        )
        
        user_row = result.fetchone()
        
        if not user_row:
            logger.warning(f"❌ User not found: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        logger.info(f"✅ User found: {user_row.email}, status: {user_row.status}")
        
        # Verify password
        security_manager = SecurityManager()
        password_valid = security_manager.verify_password(request.password, user_row.hashed_password)
        logger.info(f"🔑 Password valid: {password_valid}")
        
        if not password_valid:
            logger.warning(f"❌ Invalid password for: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if user_row.status != 'ACTIVE':
            logger.warning(f"❌ Account not active: {user_row.status}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is not active"
            )
        
        # Generate access token
        access_token = security_manager.create_access_token(
            data={
                "sub": str(user_row.id),
                "email": user_row.email,
                "role": user_row.role
            }
        )
        
        # Update last login
        await db.execute(
            text("UPDATE users SET last_login = NOW() WHERE id = :user_id"),
            {"user_id": user_row.id}
        )
        await db.commit()
        
        # Create user response
        user_data = UserResponse(
            id=user_row.id,
            uuid=user_row.uuid or "",  # Handle None values
            email=user_row.email,
            first_name=user_row.first_name,
            last_name=user_row.last_name,
            phone=user_row.phone,
            role=user_row.role,
            status=user_row.status,
            avatar_url=user_row.avatar_url,
            bio=user_row.bio,
            address_line1=user_row.address_line1,
            address_line2=user_row.address_line2,
            city=user_row.city,
            state=user_row.state,
            zip_code=user_row.zip_code,
            country=user_row.country,
            email_verified=user_row.email_verified or False,
            phone_verified=user_row.phone_verified or False,
            identity_verified=user_row.identity_verified or False,
            two_factor_enabled=user_row.two_factor_enabled or False,
            notification_email=user_row.notification_email or True,
            notification_sms=user_row.notification_sms or True,
            notification_push=user_row.notification_push or True,
            created_at=user_row.created_at,
            updated_at=user_row.updated_at,
            last_login=user_row.last_login,
            # Additional fields
            date_of_birth=user_row.date_of_birth,
            social_security_number=user_row.social_security_number,
            notes=user_row.notes,
            move_in_date=user_row.move_in_date,
            move_out_date=user_row.move_out_date,
            employer=user_row.employer,
            position=user_row.position,
            monthly_income=user_row.monthly_income,
            employment_start_date=user_row.employment_start_date,
            emergency_contact_name=user_row.emergency_contact_name,
            emergency_contact_phone=user_row.emergency_contact_phone,
            emergency_contact_relationship=user_row.emergency_contact_relationship
        )
        
        return LoginResponse(
            user=user_data,
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
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information - simplified version bypassing ORM issues"""
    try:
        from sqlalchemy import text
        from src.core.security import SecurityManager
        
        # Verify token
        security_manager = SecurityManager()
        payload = security_manager.verify_token(credentials.credentials)
        user_id = int(payload.get("sub"))
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        # Get user directly with raw SQL to avoid relationship issues
        result = await db.execute(
            text("""
                SELECT id, uuid, email, role, status, first_name, last_name,
                       phone, avatar_url, bio, address_line1, address_line2, city, state, 
                       zip_code, country, email_verified, phone_verified, identity_verified,
                       two_factor_enabled, notification_email, notification_sms, 
                       notification_push, created_at, updated_at, last_login,
                       date_of_birth, social_security_number, notes, move_in_date, move_out_date,
                       employer, position, monthly_income, employment_start_date,
                       emergency_contact_name, emergency_contact_phone, emergency_contact_relationship
                FROM users 
                WHERE id = :user_id
            """),
            {"user_id": user_id}
        )
        
        user_row = result.fetchone()
        
        if not user_row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Check if user is active
        if user_row.status != 'ACTIVE':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )
        
        # Create user response
        user_data = UserResponse(
            id=user_row.id,
            uuid=user_row.uuid or "",
            email=user_row.email,
            first_name=user_row.first_name,
            last_name=user_row.last_name,
            phone=user_row.phone,
            role=user_row.role,
            status=user_row.status,
            avatar_url=user_row.avatar_url,
            bio=user_row.bio,
            address_line1=user_row.address_line1,
            address_line2=user_row.address_line2,
            city=user_row.city,
            state=user_row.state,
            zip_code=user_row.zip_code,
            country=user_row.country,
            email_verified=user_row.email_verified or False,
            phone_verified=user_row.phone_verified or False,
            identity_verified=user_row.identity_verified or False,
            two_factor_enabled=user_row.two_factor_enabled or False,
            notification_email=user_row.notification_email or True,
            notification_sms=user_row.notification_sms or True,
            notification_push=user_row.notification_push or True,
            created_at=user_row.created_at,
            updated_at=user_row.updated_at,
            last_login=user_row.last_login,
            # Additional fields
            date_of_birth=user_row.date_of_birth,
            social_security_number=user_row.social_security_number,
            notes=user_row.notes,
            move_in_date=user_row.move_in_date,
            move_out_date=user_row.move_out_date,
            employer=user_row.employer,
            position=user_row.position,
            monthly_income=user_row.monthly_income,
            employment_start_date=user_row.employment_start_date,
            emergency_contact_name=user_row.emergency_contact_name,
            emergency_contact_phone=user_row.emergency_contact_phone,
            emergency_contact_relationship=user_row.emergency_contact_relationship
        )
        
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

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
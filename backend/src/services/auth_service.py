"""
Green PM - Authentication Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
import json
import logging

from src.core.security import security
from src.models.user import User, UserRole, UserStatus
from src.schemas.auth import RegisterRequest
from src.services.user_service import UserService
from src.services.notification_service import NotificationService
from src.core.config import settings

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)
        self.notification_service = NotificationService()
        
        # Initialize Firebase if not already done
        if not firebase_admin._apps:
            try:
                if settings.FIREBASE_CONFIG:
                    firebase_config = json.loads(settings.FIREBASE_CONFIG)
                    cred = credentials.Certificate(firebase_config)
                    firebase_admin.initialize_app(cred)
            except Exception as e:
                logger.warning(f"Firebase initialization failed: {e}")

    async def register_user(self, request: RegisterRequest) -> User:
        """Register a new user"""
        # Check if user already exists
        existing_user = await self.user_service.get_user_by_email(request.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash password
        hashed_password = security.hash_password(request.password)
        
        # Create user
        user_data = {
            "email": request.email,
            "hashed_password": hashed_password,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "phone": request.phone,
            "role": UserRole(request.role),
            "status": UserStatus.PENDING
        }
        
        user = await self.user_service.create_user(user_data)
        
        # Send welcome email
        try:
            await self.notification_service.send_welcome_email(user)
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
        
        return user

    async def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate user with email and password"""
        user = await self.user_service.get_user_by_email(email)
        
        if not user or not user.hashed_password:
            return None
        
        if not security.verify_password(password, user.hashed_password):
            return None
        
        if user.status == UserStatus.SUSPENDED:
            raise ValueError("Account is suspended")
        
        return user

    async def authenticate_firebase_user(self, firebase_token: str) -> User:
        """Authenticate user with Firebase token"""
        try:
            # Verify Firebase token
            decoded_token = firebase_auth.verify_id_token(firebase_token)
            firebase_uid = decoded_token['uid']
            email = decoded_token.get('email')
            
            if not email:
                raise ValueError("Email not found in Firebase token")
            
            # Get or create user
            user = await self.user_service.get_user_by_firebase_uid(firebase_uid)
            
            if not user:
                # Check if user exists with this email
                user = await self.user_service.get_user_by_email(email)
                if user:
                    # Link Firebase UID to existing user
                    user.firebase_uid = firebase_uid
                    await self.db.commit()
                else:
                    # Create new user from Firebase data
                    user_data = {
                        "email": email,
                        "firebase_uid": firebase_uid,
                        "first_name": decoded_token.get('name', '').split(' ')[0] or 'User',
                        "last_name": ' '.join(decoded_token.get('name', '').split(' ')[1:]) or '',
                        "email_verified": decoded_token.get('email_verified', False),
                        "role": UserRole.TENANT,
                        "status": UserStatus.ACTIVE
                    }
                    user = await self.user_service.create_user(user_data)
            
            if user.status == UserStatus.SUSPENDED:
                raise ValueError("Account is suspended")
            
            return user
            
        except Exception as e:
            logger.error(f"Firebase authentication error: {e}")
            return None

    async def request_password_reset(self, email: str):
        """Request password reset"""
        user = await self.user_service.get_user_by_email(email)
        
        if user:
            # Generate reset token
            reset_token = security.generate_reset_token()
            reset_expires = datetime.utcnow() + timedelta(hours=1)
            
            # Update user with reset token
            user.password_reset_token = reset_token
            user.password_reset_expires = reset_expires
            await self.db.commit()
            
            # Send reset email
            try:
                await self.notification_service.send_password_reset_email(user, reset_token)
            except Exception as e:
                logger.error(f"Failed to send password reset email: {e}")

    async def reset_password(self, token: str, new_password: str):
        """Reset password with token"""
        # Find user with valid reset token
        stmt = select(User).where(
            User.password_reset_token == token,
            User.password_reset_expires > datetime.utcnow()
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("Invalid or expired reset token")
        
        # Update password
        user.hashed_password = security.hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        
        await self.db.commit()

    async def change_password(self, user_id: int, current_password: str, new_password: str):
        """Change user password"""
        user = await self.user_service.get_user_by_id(user_id)
        
        if not user or not user.hashed_password:
            raise ValueError("User not found")
        
        # Verify current password
        if not security.verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")
        
        # Update password
        user.hashed_password = security.hash_password(new_password)
        await self.db.commit()

    async def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        user = await self.user_service.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            await self.db.commit()

    async def log_logout(self, user_id: int):
        """Log user logout event"""
        # This could be expanded to include audit logging
        logger.info(f"User {user_id} logged out")
"""
Simple Authentication Endpoints - bypassing complex ORM relationships
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

from src.core.database import get_db
from src.core.security import SecurityManager
from src.schemas.auth import LoginRequest, LoginResponse
from src.schemas.user import UserResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/simple-login", response_model=LoginResponse)
async def simple_login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Simple login without complex ORM relationships"""
    try:
        # Get user directly with raw SQL to avoid relationship issues
        result = await db.execute(
            text("""
                SELECT id, email, hashed_password, role, status, first_name, last_name,
                       phone, created_at, updated_at
                FROM users 
                WHERE email = :email
            """),
            {"email": request.email}
        )
        
        user_row = result.fetchone()
        
        if not user_row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        security = SecurityManager()
        if not security.verify_password(request.password, user_row.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if user_row.status != 'ACTIVE':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is not active"
            )
        
        # Generate access token
        access_token = security.create_access_token(
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
        user_data = {
            "id": user_row.id,
            "email": user_row.email,
            "first_name": user_row.first_name,
            "last_name": user_row.last_name,
            "phone": user_row.phone,
            "role": user_row.role,
            "status": user_row.status,
            "created_at": user_row.created_at,
            "updated_at": user_row.updated_at
        }
        
        return LoginResponse(
            user=UserResponse(**user_data),
            access_token=access_token,
            token_type="bearer"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Simple login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")
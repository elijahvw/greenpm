#!/usr/bin/env python3
"""
Test simple login logic
"""
import asyncio
import sys
sys.path.append('.')

from sqlalchemy import text
from src.core.database import AsyncSessionLocal
from src.core.security import SecurityManager

async def test_simple_login():
    """Test the exact login logic from the endpoint"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    async with AsyncSessionLocal() as db:
        try:
            email = "admin@greenpm.com"
            password = "password123"
            
            print(f"🔐 Testing login for: {email}")
            
            # Exact query from the endpoint
            result = await db.execute(
                text("""
                    SELECT id, uuid, email, hashed_password, role, status, first_name, last_name,
                           phone, avatar_url, bio, address_line1, address_line2, city, state, 
                           zip_code, country, email_verified, phone_verified, identity_verified,
                           two_factor_enabled, notification_email, notification_sms, 
                           notification_push, created_at, updated_at, last_login
                    FROM users 
                    WHERE email = :email
                """),
                {"email": email}
            )
            
            user_row = result.fetchone()
            
            if not user_row:
                print(f"❌ User not found")
                return
            
            print(f"✅ User found: {user_row.email}")
            print(f"📋 Role: {user_row.role}")
            print(f"📋 Status: {user_row.status}")
            
            # Test password verification
            security_manager = SecurityManager()
            password_valid = security_manager.verify_password(password, user_row.hashed_password)
            print(f"🔑 Password valid: {password_valid}")
            
            if not password_valid:
                print(f"❌ Password verification failed")
                return
            
            # Check status
            if user_row.status != 'ACTIVE':
                print(f"❌ Account not active: {user_row.status}")
                return
            
            # Generate token
            access_token = security_manager.create_access_token(
                data={
                    "sub": str(user_row.id),
                    "email": user_row.email,
                    "role": user_row.role
                }
            )
            
            print(f"✅ Token generated: {access_token[:50]}...")
            
            # Test creating UserResponse object
            from src.schemas.user import UserResponse
            
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
                last_login=user_row.last_login
            )
            
            print(f"✅ UserResponse created successfully")
            print(f"👤 User: {user_data.first_name} {user_data.last_name}")
            
            # Test creating LoginResponse
            from src.schemas.auth import LoginResponse
            
            response = LoginResponse(
                user=user_data,
                access_token=access_token,
                token_type="bearer"
            )
            
            print(f"✅ LoginResponse created successfully")
            print(f"🎉 Login logic working perfectly!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """Run simple login test"""
    try:
        await test_simple_login()
        return 0
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
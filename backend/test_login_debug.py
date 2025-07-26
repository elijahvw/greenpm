#!/usr/bin/env python3
"""
Debug login process
"""
import asyncio
import sys
sys.path.append('.')

from sqlalchemy import text
from src.core.database import AsyncSessionLocal
from src.core.security import SecurityManager

async def test_login():
    """Test login process step by step"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    email = "landlord@example.com"
    password = "landlord123"
    
    async with AsyncSessionLocal() as db:
        # Get user
        result = await db.execute(
            text("""
                SELECT id, email, hashed_password, role, status
                FROM users 
                WHERE email = :email
            """),
            {"email": email}
        )
        
        user_row = result.fetchone()
        
        if not user_row:
            print(f"❌ User not found: {email}")
            return
        
        print(f"✅ User found: {user_row.email}")
        print(f"   Role: {user_row.role}")
        print(f"   Status: {user_row.status}")
        
        # Test password verification
        security = SecurityManager()
        password_valid = security.verify_password(password, user_row.hashed_password)
        
        print(f"   Password valid: {password_valid}")
        
        if user_row.status != 'ACTIVE':
            print(f"❌ Account not active: {user_row.status}")
            return
        
        print("✅ All checks passed - login should work!")

if __name__ == "__main__":
    asyncio.run(test_login())
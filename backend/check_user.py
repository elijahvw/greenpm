#!/usr/bin/env python3
"""
Check demo user details
"""
import asyncio
import sys
sys.path.append('.')

from sqlalchemy import text
from src.core.database import AsyncSessionLocal

async def check_user():
    """Check demo user details"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("""
                SELECT email, role, status, hashed_password
                FROM users 
                WHERE email IN ('admin@greenpm.com', 'landlord@example.com')
            """)
        )
        
        users = result.fetchall()
        for user in users:
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Status: {user.status}")
            print(f"Has password: {'Yes' if user.hashed_password else 'No'}")
            print("---")

if __name__ == "__main__":
    asyncio.run(check_user())
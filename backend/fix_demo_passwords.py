#!/usr/bin/env python3
"""
Fix demo user passwords for login
"""
import asyncio
import sys
sys.path.append('.')

from sqlalchemy import text
from src.core.database import AsyncSessionLocal
from src.core.security import SecurityManager

async def fix_demo_passwords():
    """Fix demo user passwords"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    security = SecurityManager()
    
    # Demo credentials
    demo_users = [
        ("admin@greenpm.com", "GreenPM2024!"),
        ("landlord@example.com", "landlord123"),
        ("tenant@example.com", "tenant123")
    ]
    
    async with AsyncSessionLocal() as db:
        for email, password in demo_users:
            try:
                # Hash the password
                hashed_password = security.hash_password(password)
                
                # Update the user's password
                result = await db.execute(
                    text("""
                        UPDATE users 
                        SET hashed_password = :hashed_password,
                            status = 'ACTIVE',
                            updated_at = NOW()
                        WHERE email = :email
                    """),
                    {
                        "email": email,
                        "hashed_password": hashed_password
                    }
                )
                
                if result.rowcount > 0:
                    print(f"✅ Updated password for {email}")
                else:
                    print(f"❌ User not found: {email}")
                    
            except Exception as e:
                print(f"❌ Error updating {email}: {e}")
        
        await db.commit()
        print("✅ Demo passwords updated successfully!")

if __name__ == "__main__":
    asyncio.run(fix_demo_passwords())
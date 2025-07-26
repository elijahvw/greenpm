#!/usr/bin/env python3
"""
Fix user role enum to include PLATFORM_ADMIN
"""
import asyncio
import sys
sys.path.append('.')

from sqlalchemy import text
from src.core.database import AsyncSessionLocal

async def fix_user_role_enum():
    """Add PLATFORM_ADMIN to user role enum"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    async with AsyncSessionLocal() as db:
        try:
            print("🔄 Updating user role enum...")
            
            # Add PLATFORM_ADMIN to the enum
            await db.execute(text("""
                ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'PLATFORM_ADMIN'
            """))
            
            print("✅ Added PLATFORM_ADMIN to user role enum")
            
            await db.commit()
            print("✅ User role enum updated successfully!")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error updating enum: {e}")
            raise

async def main():
    """Run enum fix"""
    try:
        await fix_user_role_enum()
        return 0
    except Exception as e:
        print(f"❌ Enum fix failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
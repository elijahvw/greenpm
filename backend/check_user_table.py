#!/usr/bin/env python3
"""
Check user table structure
"""
import asyncio
import sys
sys.path.append('.')

from sqlalchemy import text
from src.core.database import AsyncSessionLocal

async def check_user_table():
    """Check user table structure"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    async with AsyncSessionLocal() as db:
        try:
            print("🔍 USER TABLE STRUCTURE")
            print("=" * 30)
            
            # Get table structure
            result = await db.execute(
                text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    ORDER BY ordinal_position
                """)
            )
            columns = result.fetchall()
            
            print("Columns in users table:")
            for col in columns:
                nullable = "NULL" if col.is_nullable == "YES" else "NOT NULL"
                default = f" DEFAULT {col.column_default}" if col.column_default else ""
                print(f"  • {col.column_name}: {col.data_type} {nullable}{default}")
            
            print(f"\nTotal columns: {len(columns)}")
            
            # Get current users
            print("\n👥 CURRENT USERS")
            print("=" * 15)
            
            result = await db.execute(
                text("""
                    SELECT 
                        u.id, u.email, u.role, u.company_id,
                        c.name as company_name, c.subdomain
                    FROM users u
                    LEFT JOIN companies c ON c.id = u.company_id
                    ORDER BY u.id
                """)
            )
            users = result.fetchall()
            
            for user in users:
                company_info = f"{user.company_name} ({user.subdomain})" if user.company_name else "No Company"
                print(f"  • ID: {user.id}, Email: {user.email}, Role: {user.role}, Company: {company_info}")
            
            # Check passwords
            print("\n🔐 PASSWORD CHECK")
            print("=" * 17)
            
            result = await db.execute(
                text("SELECT id, email, password_hash FROM users")
            )
            password_users = result.fetchall()
            
            for user in password_users:
                has_hash = "✅ Has hash" if user.password_hash else "❌ No hash"
                print(f"  • {user.email}: {has_hash}")
                
        except Exception as e:
            print(f"❌ Error checking table: {e}")

async def main():
    """Run table check"""
    try:
        await check_user_table()
        return 0
    except Exception as e:
        print(f"❌ Check failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
#!/usr/bin/env python3
"""
Fix demo users for login
"""
import asyncio
import sys
sys.path.append('.')

from sqlalchemy import text
from src.core.database import AsyncSessionLocal

async def fix_demo_users():
    """Fix demo user setup with correct column names"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    async with AsyncSessionLocal() as db:
        try:
            print("🔧 FIXING DEMO USERS")
            print("=" * 25)
            
            # Get default company ID
            result = await db.execute(
                text("SELECT id FROM companies WHERE subdomain = 'default'")
            )
            default_company = result.fetchone()
            
            if not default_company:
                print("❌ Default company not found")
                return
            
            default_company_id = default_company.id
            print(f"📋 Using default company ID: {default_company_id}")
            
            # Check current users first
            print("\n👥 Current Users:")
            result = await db.execute(
                text("""
                    SELECT id, email, role, status, company_id, hashed_password
                    FROM users 
                    ORDER BY id
                """)
            )
            current_users = result.fetchall()
            
            for user in current_users:
                has_password = "✅ Has password" if user.hashed_password else "❌ No password"
                print(f"  • {user.email} (Role: {user.role}, Status: {user.status}, Company: {user.company_id}) - {has_password}")
            
            # Default password hash for "password123"
            # This is bcrypt hash of "password123"
            default_password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.aTG"
            
            # Demo users we need
            demo_users = [
                {
                    "email": "admin@greenpm.com",
                    "role": "PLATFORM_ADMIN",
                    "company_id": None,  # Platform admin has no company
                    "first_name": "Platform",
                    "last_name": "Admin"
                },
                {
                    "email": "landlord@demo.com", 
                    "role": "LANDLORD",
                    "company_id": default_company_id,
                    "first_name": "Demo",
                    "last_name": "Landlord"
                },
                {
                    "email": "tenant@demo.com",
                    "role": "TENANT", 
                    "company_id": default_company_id,
                    "first_name": "Demo",
                    "last_name": "Tenant"
                }
            ]
            
            print(f"\n🔑 Setting up demo users with password: password123")
            
            for user_data in demo_users:
                # Check if user exists
                result = await db.execute(
                    text("SELECT id, status, hashed_password, role, company_id FROM users WHERE email = :email"),
                    {"email": user_data["email"]}
                )
                existing_user = result.fetchone()
                
                if existing_user:
                    # Update existing user
                    updates = []
                    params = {"user_id": existing_user.id}
                    
                    # Always ensure correct password, role, status, and company
                    updates.append("hashed_password = :hashed_password")
                    updates.append("role = :role")
                    updates.append("status = :status")
                    updates.append("company_id = :company_id")
                    
                    params.update({
                        "hashed_password": default_password_hash,
                        "role": user_data["role"],
                        "status": "ACTIVE",
                        "company_id": user_data["company_id"]
                    })
                    
                    await db.execute(
                        text(f"UPDATE users SET {', '.join(updates)} WHERE id = :user_id"),
                        params
                    )
                    print(f"✅ Updated {user_data['email']}")
                        
                else:
                    # Create new user
                    await db.execute(
                        text("""
                            INSERT INTO users (
                                email, hashed_password, first_name, last_name, role, 
                                company_id, status, created_at
                            ) VALUES (
                                :email, :hashed_password, :first_name, :last_name, :role,
                                :company_id, 'ACTIVE', NOW()
                            )
                        """),
                        {
                            **user_data,
                            "hashed_password": default_password_hash
                        }
                    )
                    print(f"✅ Created {user_data['email']}")
            
            # Also fix the existing landlord@example.com if it exists
            result = await db.execute(
                text("SELECT id FROM users WHERE email = 'landlord@example.com'")
            )
            existing_landlord = result.fetchone()
            
            if existing_landlord:
                await db.execute(
                    text("""
                        UPDATE users 
                        SET hashed_password = :password, status = 'ACTIVE', role = 'LANDLORD'
                        WHERE email = 'landlord@example.com'
                    """),
                    {"password": default_password_hash}
                )
                print("✅ Updated landlord@example.com password")
            
            await db.commit()
            
            print("\n✅ Demo users fixed!")
            print("\n🔑 Demo Credentials (all use password: password123):")
            print("  • admin@greenpm.com (Platform Admin)")
            print("  • landlord@demo.com (Landlord)")
            print("  • landlord@example.com (Existing Landlord)")
            print("  • tenant@demo.com (Tenant)")
            
            # Verify the fix
            print("\n🔍 Verification:")
            result = await db.execute(
                text("""
                    SELECT email, role, status, company_id, 
                           CASE WHEN hashed_password IS NOT NULL THEN 'Has Password' ELSE 'No Password' END as password_status
                    FROM users 
                    WHERE email IN ('admin@greenpm.com', 'landlord@demo.com', 'tenant@demo.com', 'landlord@example.com')
                    ORDER BY email
                """)
            )
            verified_users = result.fetchall()
            
            for user in verified_users:
                print(f"  • {user.email}: {user.role}, {user.status}, Company: {user.company_id}, {user.password_status}")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error fixing users: {e}")
            raise

async def main():
    """Run user fix"""
    try:
        await fix_demo_users()
        return 0
    except Exception as e:
        print(f"❌ User fix failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
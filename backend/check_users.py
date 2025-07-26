#!/usr/bin/env python3
"""
Check current user data and fix login issues
"""
import asyncio
import sys
sys.path.append('.')

from sqlalchemy import text
from src.core.database import AsyncSessionLocal

async def check_users():
    """Check current user data"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    async with AsyncSessionLocal() as db:
        try:
            print("👥 CURRENT USER DATA")
            print("=" * 50)
            
            # Get all users
            result = await db.execute(
                text("""
                    SELECT 
                        u.id, u.email, u.role, u.is_active, u.company_id,
                        c.name as company_name, c.subdomain
                    FROM users u
                    LEFT JOIN companies c ON c.id = u.company_id
                    ORDER BY u.id
                """)
            )
            users = result.fetchall()
            
            print(f"Found {len(users)} users:")
            for user in users:
                company_info = f"{user.company_name} ({user.subdomain})" if user.company_name else "No Company"
                active_status = "✅ Active" if user.is_active else "❌ Inactive"
                print(f"  • ID: {user.id}")
                print(f"    Email: {user.email}")
                print(f"    Role: {user.role}")
                print(f"    Status: {active_status}")
                print(f"    Company: {company_info}")
                print()
            
            # Check for demo credentials
            demo_emails = [
                'admin@greenpm.com',
                'landlord@demo.com', 
                'tenant@demo.com',
                'tenant1@demo.com',
                'tenant2@demo.com'
            ]
            
            print("🔍 DEMO CREDENTIALS CHECK")
            print("=" * 30)
            
            for email in demo_emails:
                result = await db.execute(
                    text("SELECT id, email, role, is_active, company_id FROM users WHERE email = :email"),
                    {"email": email}
                )
                user = result.fetchone()
                
                if user:
                    status = "✅ Found" if user.is_active else "❌ Found but inactive"
                    print(f"  • {email}: {status} (Role: {user.role}, Company: {user.company_id})")
                else:
                    print(f"  • {email}: ❌ Not found")
            
            # Check password hashes
            print("\n🔐 PASSWORD HASH CHECK")
            print("=" * 25)
            
            result = await db.execute(
                text("SELECT email, password_hash FROM users WHERE email IN :emails"),
                {"emails": tuple(demo_emails)}
            )
            password_users = result.fetchall()
            
            for user in password_users:
                has_hash = "✅ Has hash" if user.password_hash else "❌ No hash"
                hash_preview = user.password_hash[:20] + "..." if user.password_hash else "None"
                print(f"  • {user.email}: {has_hash} ({hash_preview})")
                
        except Exception as e:
            print(f"❌ Error checking users: {e}")

async def fix_demo_users():
    """Fix demo user setup"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    async with AsyncSessionLocal() as db:
        try:
            print("\n🔧 FIXING DEMO USERS")
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
            
            # Demo users to ensure exist
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
                },
                {
                    "email": "tenant1@demo.com",
                    "role": "TENANT",
                    "company_id": default_company_id, 
                    "first_name": "Demo",
                    "last_name": "Tenant1"
                },
                {
                    "email": "tenant2@demo.com",
                    "role": "TENANT",
                    "company_id": default_company_id,
                    "first_name": "Demo", 
                    "last_name": "Tenant2"
                }
            ]
            
            # Default password hash for "password123"
            # This is bcrypt hash of "password123"
            default_password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.aTG"
            
            for user_data in demo_users:
                # Check if user exists
                result = await db.execute(
                    text("SELECT id, is_active, password_hash FROM users WHERE email = :email"),
                    {"email": user_data["email"]}
                )
                existing_user = result.fetchone()
                
                if existing_user:
                    # Update existing user
                    updates = []
                    params = {"user_id": existing_user.id}
                    
                    if not existing_user.is_active:
                        updates.append("is_active = :is_active")
                        params["is_active"] = True
                    
                    if not existing_user.password_hash:
                        updates.append("password_hash = :password_hash")
                        params["password_hash"] = default_password_hash
                    
                    # Always update role and company_id to ensure correct setup
                    updates.append("role = :role")
                    updates.append("company_id = :company_id")
                    params["role"] = user_data["role"]
                    params["company_id"] = user_data["company_id"]
                    
                    if updates:
                        await db.execute(
                            text(f"UPDATE users SET {', '.join(updates)} WHERE id = :user_id"),
                            params
                        )
                        print(f"✅ Updated {user_data['email']}")
                    else:
                        print(f"📋 {user_data['email']} already correct")
                        
                else:
                    # Create new user
                    await db.execute(
                        text("""
                            INSERT INTO users (
                                email, password_hash, first_name, last_name, role, 
                                company_id, is_active, created_at
                            ) VALUES (
                                :email, :password_hash, :first_name, :last_name, :role,
                                :company_id, true, NOW()
                            )
                        """),
                        {
                            **user_data,
                            "password_hash": default_password_hash
                        }
                    )
                    print(f"✅ Created {user_data['email']}")
            
            await db.commit()
            print("\n✅ Demo users fixed!")
            print("\n🔑 Demo Credentials:")
            print("  • admin@greenpm.com / password123 (Platform Admin)")
            print("  • landlord@demo.com / password123 (Landlord)")
            print("  • tenant@demo.com / password123 (Tenant)")
            print("  • tenant1@demo.com / password123 (Tenant)")
            print("  • tenant2@demo.com / password123 (Tenant)")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error fixing users: {e}")
            raise

async def main():
    """Run user check and fix"""
    try:
        await check_users()
        await fix_demo_users()
        await check_users()  # Check again after fixes
        return 0
    except Exception as e:
        print(f"❌ User fix failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
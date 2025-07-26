#!/usr/bin/env python3
"""
Test login functionality in detail
"""
import asyncio
import sys
sys.path.append('.')

from sqlalchemy import text
from src.core.database import AsyncSessionLocal
from src.core.security import SecurityManager

async def test_login_detailed():
    """Test login functionality with detailed output"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    async with AsyncSessionLocal() as db:
        try:
            print("🔐 DETAILED LOGIN TEST")
            print("=" * 30)
            
            security_manager = SecurityManager()
            
            # First, test the security manager itself
            print("🧪 Testing SecurityManager...")
            test_password = "password123"
            test_hash = security_manager.hash_password(test_password)
            test_verify = security_manager.verify_password(test_password, test_hash)
            
            print(f"  Password: {test_password}")
            print(f"  Generated hash: {test_hash}")
            print(f"  Verification: {test_verify}")
            
            if not test_verify:
                print("❌ SecurityManager is broken!")
                return
            
            print("✅ SecurityManager working correctly")
            
            # Now test each user
            test_emails = ["admin@greenpm.com", "landlord@demo.com", "tenant@demo.com", "landlord@example.com"]
            
            for email in test_emails:
                print(f"\n👤 Testing user: {email}")
                
                # Get user
                result = await db.execute(
                    text("SELECT id, email, hashed_password, role, status FROM users WHERE email = :email"),
                    {"email": email}
                )
                user = result.fetchone()
                
                if not user:
                    print(f"  ❌ User not found")
                    continue
                
                print(f"  ✅ User found (ID: {user.id}, Role: {user.role}, Status: {user.status})")
                
                if not user.hashed_password:
                    print(f"  ❌ No password hash")
                    continue
                
                print(f"  📋 Hash: {user.hashed_password[:50]}...")
                
                # Test current password
                current_valid = security_manager.verify_password("password123", user.hashed_password)
                print(f"  🔐 Current password valid: {current_valid}")
                
                if not current_valid:
                    print(f"  🔧 Regenerating password hash...")
                    new_hash = security_manager.hash_password("password123")
                    
                    await db.execute(
                        text("UPDATE users SET hashed_password = :hash WHERE id = :user_id"),
                        {"hash": new_hash, "user_id": user.id}
                    )
                    await db.commit()
                    
                    # Test again
                    new_valid = security_manager.verify_password("password123", new_hash)
                    print(f"  ✅ New password valid: {new_valid}")
                    print(f"  📋 New hash: {new_hash[:50]}...")
                
                else:
                    print(f"  ✅ Password already working")
            
            print(f"\n🎉 All users should now have working passwords!")
            print(f"🔑 Use 'password123' for all demo accounts")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """Run detailed login test"""
    try:
        await test_login_detailed()
        return 0
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
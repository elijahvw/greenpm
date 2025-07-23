#!/usr/bin/env python3
"""
Simple test script to verify login functionality
"""
import asyncio
import asyncpg
from src.core.security import SecurityManager

async def test_login():
    """Test login functionality directly"""
    conn = await asyncpg.connect('postgresql://greenpm_user:greenpm22@34.172.72.85:5432/greenpm_dev')
    
    # Get user directly from database
    user_row = await conn.fetchrow('''
        SELECT id, email, hashed_password, role, status, first_name, last_name
        FROM users 
        WHERE email = $1
    ''', 'landlord@example.com')
    
    if not user_row:
        print("❌ User not found")
        await conn.close()
        return
    
    print(f"✅ User found: {user_row['email']}")
    
    # Test password verification
    security = SecurityManager()
    password_valid = security.verify_password('landlord123', user_row['hashed_password'])
    
    if not password_valid:
        print("❌ Password verification failed")
        await conn.close()
        return
    
    print("✅ Password verification successful")
    
    # Check if user is active
    if user_row['status'] != 'ACTIVE':
        print(f"❌ User status is {user_row['status']}, not ACTIVE")
        await conn.close()
        return
    
    print("✅ User is active")
    
    # Generate JWT token
    token_data = {
        "sub": str(user_row['id']),
        "email": user_row['email'],
        "role": user_row['role']
    }
    
    access_token = security.create_access_token(data=token_data)
    print(f"✅ JWT token generated: {access_token[:50]}...")
    
    # Create response
    response = {
        "user": {
            "id": user_row['id'],
            "email": user_row['email'],
            "first_name": user_row['first_name'],
            "last_name": user_row['last_name'],
            "role": user_row['role'],
            "status": user_row['status']
        },
        "access_token": access_token,
        "token_type": "bearer"
    }
    
    print("✅ Login successful!")
    print("Response:", response)
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(test_login())
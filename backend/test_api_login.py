#!/usr/bin/env python3
"""
Test API login endpoints
"""
import asyncio
import sys
import httpx
import json

async def test_api_login():
    """Test the actual API login endpoints"""
    base_url = "http://localhost:8000"
    
    # Test credentials
    test_credentials = [
        {"email": "admin@greenpm.com", "password": "password123", "role": "Platform Admin"},
        {"email": "landlord@demo.com", "password": "password123", "role": "Landlord"},
        {"email": "landlord@example.com", "password": "password123", "role": "Existing Landlord"},
        {"email": "tenant@demo.com", "password": "password123", "role": "Tenant"}
    ]
    
    print("🌐 TESTING API LOGIN ENDPOINTS")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        for creds in test_credentials:
            print(f"\n👤 Testing {creds['role']}: {creds['email']}")
            
            try:
                # Test login
                response = await client.post(
                    f"{base_url}/api/v1/auth/login",
                    json={
                        "email": creds["email"],
                        "password": creds["password"]
                    },
                    timeout=10.0
                )
                
                print(f"  📡 Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ Login successful!")
                    print(f"  👤 User: {data['user']['first_name']} {data['user']['last_name']}")
                    print(f"  🎭 Role: {data['user']['role']}")
                    print(f"  🔑 Token: {data['access_token'][:50]}...")
                    
                    # Test /me endpoint with token
                    headers = {"Authorization": f"Bearer {data['access_token']}"}
                    me_response = await client.get(
                        f"{base_url}/api/v1/auth/me",
                        headers=headers,
                        timeout=10.0
                    )
                    
                    if me_response.status_code == 200:
                        me_data = me_response.json()
                        print(f"  ✅ /me endpoint working: {me_data['email']}")
                    else:
                        print(f"  ❌ /me endpoint failed: {me_response.status_code}")
                        print(f"      {me_response.text}")
                    
                else:
                    print(f"  ❌ Login failed")
                    print(f"  📄 Response: {response.text}")
                    
            except httpx.ConnectError:
                print(f"  ❌ Cannot connect to server at {base_url}")
                print(f"  💡 Make sure the backend server is running")
                break
            except Exception as e:
                print(f"  ❌ Error: {e}")

async def main():
    """Run API login test"""
    try:
        await test_api_login()
        return 0
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
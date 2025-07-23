#!/usr/bin/env python3
"""
Create data using direct API calls with proper permissions
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def get_token(email, password):
    response = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"], response.json()["user"]
    return None, None

def create_leases_as_landlord():
    # Get landlord token
    landlord_token, landlord_user = get_token("landlord1@example.com", "landlord123")
    if not landlord_token:
        print("Failed to get landlord token")
        return
    
    headers = {"Authorization": f"Bearer {landlord_token}"}
    
    # Get landlord's properties
    properties_response = requests.get(f"{BASE_URL}/properties", headers=headers)
    if properties_response.status_code != 200:
        print("Failed to get properties")
        return
    
    properties = properties_response.json()
    print(f"Found {len(properties)} properties for landlord")
    
    # Get tenant tokens and IDs
    tenant_credentials = [
        ("tenant1@example.com", "tenant123"),
        ("tenant2@example.com", "tenant123"),
        ("tenant3@example.com", "tenant123")
    ]
    
    tenant_users = []
    for email, password in tenant_credentials:
        token, user = get_token(email, password)
        if user:
            tenant_users.append(user)
    
    print(f"Found {len(tenant_users)} tenants")
    
    # Create leases for first 3 properties
    for i in range(min(3, len(properties), len(tenant_users))):
        property_data = properties[i]
        tenant = tenant_users[i]
        
        lease_data = {
            "property_id": property_data["id"],
            "tenant_id": tenant["id"],
            "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=335)).strftime("%Y-%m-%d"),
            "rent_amount": property_data["rent_amount"],
            "deposit_amount": property_data["rent_amount"],
            "status": "active"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/leases", json=lease_data, headers=headers)
            if response.status_code in [200, 201]:
                print(f"✓ Created lease: {tenant['first_name']} {tenant['last_name']} -> {property_data['name']}")
            else:
                print(f"✗ Failed to create lease: {response.text}")
        except Exception as e:
            print(f"✗ Error creating lease: {e}")

def create_maintenance_as_tenant():
    # Get tenant tokens and create maintenance requests
    tenant_credentials = [
        ("tenant1@example.com", "tenant123"),
        ("tenant2@example.com", "tenant123")
    ]
    
    # Get landlord's properties first
    landlord_token, _ = get_token("landlord1@example.com", "landlord123")
    if not landlord_token:
        return
    
    landlord_headers = {"Authorization": f"Bearer {landlord_token}"}
    properties_response = requests.get(f"{BASE_URL}/properties", headers=landlord_headers)
    if properties_response.status_code != 200:
        return
    
    properties = properties_response.json()
    
    maintenance_requests = [
        {
            "title": "Leaky Faucet in Kitchen",
            "description": "The kitchen faucet has been dripping constantly for the past week",
            "priority": "medium",
            "category": "plumbing"
        },
        {
            "title": "Broken Air Conditioning", 
            "description": "AC unit stopped working, apartment is getting very hot",
            "priority": "high",
            "category": "hvac"
        }
    ]
    
    for i, (email, password) in enumerate(tenant_credentials):
        if i >= len(maintenance_requests) or i >= len(properties):
            break
            
        tenant_token, tenant_user = get_token(email, password)
        if not tenant_token:
            continue
            
        headers = {"Authorization": f"Bearer {tenant_token}"}
        request_data = maintenance_requests[i].copy()
        request_data["property_id"] = properties[i]["id"]
        
        try:
            response = requests.post(f"{BASE_URL}/maintenance", json=request_data, headers=headers)
            if response.status_code in [200, 201]:
                print(f"✓ Created maintenance request: {request_data['title']}")
            else:
                print(f"✗ Failed to create maintenance request: {response.text}")
        except Exception as e:
            print(f"✗ Error creating maintenance request: {e}")

def create_payments_as_landlord():
    # Get landlord token
    landlord_token, landlord_user = get_token("landlord1@example.com", "landlord123")
    if not landlord_token:
        return
    
    headers = {"Authorization": f"Bearer {landlord_token}"}
    
    # Get properties
    properties_response = requests.get(f"{BASE_URL}/properties", headers=headers)
    if properties_response.status_code != 200:
        return
    
    properties = properties_response.json()
    
    # Get tenant users
    tenant_users = []
    for email, password in [("tenant1@example.com", "tenant123"), ("tenant2@example.com", "tenant123"), ("tenant3@example.com", "tenant123")]:
        token, user = get_token(email, password)
        if user:
            tenant_users.append(user)
    
    # Create payments for the last 3 months
    for month_offset in range(3):
        payment_date = datetime.now() - timedelta(days=30 * month_offset)
        
        for i, tenant in enumerate(tenant_users[:3]):
            if i >= len(properties):
                break
                
            payment_data = {
                "tenant_id": tenant["id"],
                "property_id": properties[i]["id"],
                "amount": properties[i]["rent_amount"],
                "payment_date": payment_date.strftime("%Y-%m-%d"),
                "payment_method": ["bank_transfer", "credit_card", "check"][i % 3],
                "status": "completed" if month_offset > 0 else ["completed", "pending"][i % 2],
                "description": f"Rent payment for {payment_date.strftime('%B %Y')}"
            }
            
            try:
                response = requests.post(f"{BASE_URL}/payments", json=payment_data, headers=headers)
                if response.status_code in [200, 201]:
                    print(f"✓ Created payment: {tenant['first_name']} {tenant['last_name']} - {payment_date.strftime('%B %Y')}")
                else:
                    print(f"✗ Failed to create payment: {response.text}")
            except Exception as e:
                print(f"✗ Error creating payment: {e}")

def main():
    print("🏠 Creating comprehensive data...")
    
    print("\n📋 Creating leases...")
    create_leases_as_landlord()
    
    print("\n🔧 Creating maintenance requests...")
    create_maintenance_as_tenant()
    
    print("\n💰 Creating payments...")
    create_payments_as_landlord()
    
    print("\n✅ Data creation completed!")
    
    # Test the API endpoints
    print("\n🧪 Testing API endpoints...")
    landlord_token, _ = get_token("landlord1@example.com", "landlord123")
    if landlord_token:
        headers = {"Authorization": f"Bearer {landlord_token}"}
        
        # Test dashboard
        dashboard_response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
        if dashboard_response.status_code == 200:
            stats = dashboard_response.json()
            print(f"✓ Dashboard stats: {stats['totals']['properties']} properties, {stats['totals']['leases']} leases")
        
        # Test properties
        properties_response = requests.get(f"{BASE_URL}/properties", headers=headers)
        if properties_response.status_code == 200:
            properties = properties_response.json()
            print(f"✓ Properties: {len(properties)} found")
        
        # Test leases
        leases_response = requests.get(f"{BASE_URL}/leases", headers=headers)
        if leases_response.status_code == 200:
            leases = leases_response.json()
            print(f"✓ Leases: {len(leases)} found")

if __name__ == "__main__":
    main()
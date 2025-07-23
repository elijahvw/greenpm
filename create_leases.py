#!/usr/bin/env python3
"""
Create leases and additional data
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def get_token(email, password):
    response = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def get_users_and_properties():
    # Get admin token (try different credentials)
    admin_token = get_token("test@example.com", "password123")
    if not admin_token:
        admin_token = get_token("landlord1@example.com", "landlord123")
    if not admin_token:
        print("Failed to get admin token")
        return None, None, None
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get all users
    users_response = requests.get(f"{BASE_URL}/users", headers=headers)
    if users_response.status_code != 200:
        print("Failed to get users")
        return None, None, None
    
    users = users_response.json()
    
    # Get all properties
    properties_response = requests.get(f"{BASE_URL}/properties", headers=headers)
    if properties_response.status_code != 200:
        print("Failed to get properties")
        return None, None, None
    
    properties = properties_response.json()
    
    return admin_token, users, properties

def create_leases():
    admin_token, users, properties = get_users_and_properties()
    if not admin_token:
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Find tenants and landlords
    tenants = [u for u in users if u['role'] == 'tenant']
    landlords = [u for u in users if u['role'] == 'landlord']
    
    print(f"Found {len(tenants)} tenants and {len(properties)} properties")
    
    # Create leases for first 3 properties with first 3 tenants
    for i in range(min(3, len(tenants), len(properties))):
        tenant = tenants[i]
        property_data = properties[i]
        
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

def create_maintenance_requests():
    admin_token, users, properties = get_users_and_properties()
    if not admin_token:
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    tenants = [u for u in users if u['role'] == 'tenant']
    
    maintenance_requests = [
        {
            "property_id": properties[0]["id"] if properties else None,
            "tenant_id": tenants[0]["id"] if tenants else None,
            "title": "Leaky Faucet in Kitchen",
            "description": "The kitchen faucet has been dripping constantly for the past week",
            "priority": "medium",
            "category": "plumbing",
            "status": "open"
        },
        {
            "property_id": properties[1]["id"] if len(properties) > 1 else None,
            "tenant_id": tenants[1]["id"] if len(tenants) > 1 else None,
            "title": "Broken Air Conditioning",
            "description": "AC unit stopped working, apartment is getting very hot",
            "priority": "high",
            "category": "hvac",
            "status": "in_progress"
        },
        {
            "property_id": properties[0]["id"] if properties else None,
            "tenant_id": tenants[0]["id"] if tenants else None,
            "title": "Squeaky Door Hinges",
            "description": "Bedroom door hinges are very squeaky and need lubrication",
            "priority": "low",
            "category": "general",
            "status": "open"
        }
    ]
    
    for request_data in maintenance_requests:
        if not request_data["property_id"] or not request_data["tenant_id"]:
            continue
            
        try:
            response = requests.post(f"{BASE_URL}/maintenance", json=request_data, headers=headers)
            if response.status_code in [200, 201]:
                print(f"✓ Created maintenance request: {request_data['title']}")
            else:
                print(f"✗ Failed to create maintenance request: {response.text}")
        except Exception as e:
            print(f"✗ Error creating maintenance request: {e}")

def create_payments():
    admin_token, users, properties = get_users_and_properties()
    if not admin_token:
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    tenants = [u for u in users if u['role'] == 'tenant']
    
    # Create payments for the last 3 months
    for month_offset in range(3):
        payment_date = datetime.now() - timedelta(days=30 * month_offset)
        
        for i, tenant in enumerate(tenants[:3]):  # First 3 tenants
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
    print("🏠 Creating additional data...")
    
    print("\n📋 Creating leases...")
    create_leases()
    
    print("\n🔧 Creating maintenance requests...")
    create_maintenance_requests()
    
    print("\n💰 Creating payments...")
    create_payments()
    
    print("\n✅ Additional data creation completed!")

if __name__ == "__main__":
    main()
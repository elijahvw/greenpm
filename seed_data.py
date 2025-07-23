#!/usr/bin/env python3
"""
Seed script to populate the database with comprehensive test data
"""
import requests
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000/api/v1"

# Test users data
USERS = [
    {
        "email": "admin@greenpm.com",
        "password": "admin123",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin"
    },
    {
        "email": "landlord1@example.com", 
        "password": "landlord123",
        "first_name": "John",
        "last_name": "Smith",
        "role": "landlord",
        "phone": "+1-555-0101"
    },
    {
        "email": "landlord2@example.com",
        "password": "landlord123", 
        "first_name": "Sarah",
        "last_name": "Johnson",
        "role": "landlord",
        "phone": "+1-555-0102"
    },
    {
        "email": "tenant1@example.com",
        "password": "tenant123",
        "first_name": "Mike",
        "last_name": "Davis",
        "role": "tenant",
        "phone": "+1-555-0201"
    },
    {
        "email": "tenant2@example.com",
        "password": "tenant123",
        "first_name": "Lisa",
        "last_name": "Wilson",
        "role": "tenant", 
        "phone": "+1-555-0202"
    },
    {
        "email": "tenant3@example.com",
        "password": "tenant123",
        "first_name": "David",
        "last_name": "Brown",
        "role": "tenant",
        "phone": "+1-555-0203"
    }
]

# Properties data
PROPERTIES = [
    {
        "name": "Downtown Luxury Apartment",
        "description": "Modern 2-bedroom apartment in the heart of downtown with city views",
        "address": "123 Main St, Downtown, NY 10001",
        "type": "apartment",
        "bedrooms": 2,
        "bathrooms": 2,
        "square_feet": 1200,
        "rent_amount": 2500.00
    },
    {
        "name": "Suburban Family House",
        "description": "Spacious 3-bedroom house with backyard, perfect for families",
        "address": "456 Oak Ave, Suburbia, NY 10002", 
        "type": "house",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1800,
        "rent_amount": 3200.00
    },
    {
        "name": "Cozy Studio Loft",
        "description": "Artistic studio loft in trendy neighborhood",
        "address": "789 Art St, Creative District, NY 10003",
        "type": "studio", 
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 600,
        "rent_amount": 1800.00
    },
    {
        "name": "Waterfront Condo",
        "description": "Beautiful 2-bedroom condo with water views and amenities",
        "address": "321 Harbor Dr, Waterfront, NY 10004",
        "type": "condo",
        "bedrooms": 2,
        "bathrooms": 2,
        "square_feet": 1400,
        "rent_amount": 2800.00
    },
    {
        "name": "Historic Townhouse",
        "description": "Charming 4-bedroom townhouse in historic district",
        "address": "654 Heritage Ln, Historic District, NY 10005",
        "type": "townhouse",
        "bedrooms": 4,
        "bathrooms": 3,
        "square_feet": 2200,
        "rent_amount": 4000.00
    }
]

def create_users():
    """Create test users"""
    print("Creating users...")
    tokens = {}
    
    for user in USERS:
        try:
            # Register user
            response = requests.post(f"{BASE_URL}/auth/register", json=user)
            if response.status_code == 201 or response.status_code == 200:
                # Registration successful or user already exists
                if response.status_code == 201:
                    print(f"✓ Created user: {user['email']}")
                else:
                    # Check if response contains token (auto-login)
                    try:
                        response_data = response.json()
                        if "access_token" in response_data:
                            token = response_data["access_token"]
                            tokens[user["email"]] = token
                            print(f"✓ User exists and logged in: {user['email']}")
                            continue
                    except:
                        pass
                
                # Login to get token
                login_response = requests.post(f"{BASE_URL}/auth/login", json={
                    "email": user["email"],
                    "password": user["password"]
                })
                if login_response.status_code == 200:
                    token = login_response.json()["access_token"]
                    tokens[user["email"]] = token
                    print(f"✓ Got token for: {user['email']}")
            elif "already registered" in response.text:
                # User already exists, just login
                login_response = requests.post(f"{BASE_URL}/auth/login", json={
                    "email": user["email"],
                    "password": user["password"]
                })
                if login_response.status_code == 200:
                    token = login_response.json()["access_token"]
                    tokens[user["email"]] = token
                    print(f"✓ User already exists, logged in: {user['email']}")
            else:
                print(f"✗ Failed to create user {user['email']}: {response.text}")
        except Exception as e:
            print(f"✗ Error creating user {user['email']}: {e}")
    
    return tokens

def create_properties(tokens):
    """Create properties"""
    print("\nCreating properties...")
    property_ids = []
    
    # Use landlord tokens to create properties
    landlord_tokens = [tokens.get("landlord1@example.com"), tokens.get("landlord2@example.com")]
    
    for i, property_data in enumerate(PROPERTIES):
        token = landlord_tokens[i % len(landlord_tokens)]
        if not token:
            continue
            
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.post(f"{BASE_URL}/properties", json=property_data, headers=headers)
            if response.status_code in [200, 201]:
                property_id = response.json()["id"]
                property_ids.append(property_id)
                print(f"✓ Created property: {property_data['name']}")
            else:
                print(f"✗ Failed to create property {property_data['name']}: {response.text}")
        except Exception as e:
            print(f"✗ Error creating property {property_data['name']}: {e}")
    
    return property_ids

def create_leases(tokens, property_ids):
    """Create leases for properties"""
    print("\nCreating leases...")
    
    tenant_emails = ["tenant1@example.com", "tenant2@example.com", "tenant3@example.com"]
    landlord_token = tokens.get("landlord1@example.com")
    
    if not landlord_token:
        print("✗ No landlord token available")
        return []
    
    headers = {"Authorization": f"Bearer {landlord_token}"}
    lease_ids = []
    
    # Create leases for occupied properties (first 3 properties)
    for i, property_id in enumerate(property_ids[:3]):
        if i >= len(tenant_emails):
            break
            
        tenant_email = tenant_emails[i]
        
        # Get tenant ID
        try:
            users_response = requests.get(f"{BASE_URL}/users?role=tenant", headers=headers)
            if users_response.status_code == 200:
                tenants = users_response.json()
                tenant = next((t for t in tenants if t["email"] == tenant_email), None)
                if not tenant:
                    continue
                
                lease_data = {
                    "property_id": property_id,
                    "tenant_id": tenant["id"],
                    "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    "end_date": (datetime.now() + timedelta(days=335)).strftime("%Y-%m-%d"),
                    "rent_amount": PROPERTIES[i]["rent_amount"],
                    "deposit_amount": PROPERTIES[i]["deposit_amount"],
                    "status": "active"
                }
                
                response = requests.post(f"{BASE_URL}/leases", json=lease_data, headers=headers)
                if response.status_code in [200, 201]:
                    lease_id = response.json()["id"]
                    lease_ids.append(lease_id)
                    print(f"✓ Created lease for property {property_id} and tenant {tenant_email}")
                else:
                    print(f"✗ Failed to create lease: {response.text}")
        except Exception as e:
            print(f"✗ Error creating lease: {e}")
    
    return lease_ids

def create_maintenance_requests(tokens, property_ids):
    """Create maintenance requests"""
    print("\nCreating maintenance requests...")
    
    tenant_tokens = [tokens.get("tenant1@example.com"), tokens.get("tenant2@example.com")]
    
    maintenance_requests = [
        {
            "property_id": property_ids[0] if property_ids else None,
            "title": "Leaky Faucet in Kitchen",
            "description": "The kitchen faucet has been dripping constantly for the past week",
            "priority": "medium",
            "category": "plumbing"
        },
        {
            "property_id": property_ids[1] if len(property_ids) > 1 else None,
            "title": "Broken Air Conditioning",
            "description": "AC unit stopped working, apartment is getting very hot",
            "priority": "high", 
            "category": "hvac"
        },
        {
            "property_id": property_ids[0] if property_ids else None,
            "title": "Squeaky Door Hinges",
            "description": "Bedroom door hinges are very squeaky and need lubrication",
            "priority": "low",
            "category": "general"
        }
    ]
    
    for i, request_data in enumerate(maintenance_requests):
        if not request_data["property_id"]:
            continue
            
        token = tenant_tokens[i % len(tenant_tokens)]
        if not token:
            continue
            
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.post(f"{BASE_URL}/maintenance", json=request_data, headers=headers)
            if response.status_code in [200, 201]:
                print(f"✓ Created maintenance request: {request_data['title']}")
            else:
                print(f"✗ Failed to create maintenance request: {response.text}")
        except Exception as e:
            print(f"✗ Error creating maintenance request: {e}")

def create_payments(tokens, property_ids):
    """Create payment records"""
    print("\nCreating payments...")
    
    landlord_token = tokens.get("landlord1@example.com")
    if not landlord_token:
        print("✗ No landlord token available")
        return
    
    headers = {"Authorization": f"Bearer {landlord_token}"}
    
    # Get tenants
    try:
        users_response = requests.get(f"{BASE_URL}/users?role=tenant", headers=headers)
        if users_response.status_code != 200:
            print("✗ Failed to get tenants")
            return
        
        tenants = users_response.json()[:3]  # First 3 tenants
        
        # Create payments for the last 3 months
        for month_offset in range(3):
            payment_date = datetime.now() - timedelta(days=30 * month_offset)
            
            for i, tenant in enumerate(tenants):
                if i >= len(property_ids):
                    break
                    
                payment_data = {
                    "tenant_id": tenant["id"],
                    "property_id": property_ids[i],
                    "amount": PROPERTIES[i]["rent_amount"],
                    "payment_date": payment_date.strftime("%Y-%m-%d"),
                    "payment_method": random.choice(["bank_transfer", "credit_card", "check"]),
                    "status": "completed" if month_offset > 0 else random.choice(["completed", "pending"]),
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
                    
    except Exception as e:
        print(f"✗ Error creating payments: {e}")

def main():
    print("🌱 Starting database seeding...")
    
    # Create users and get tokens
    tokens = create_users()
    
    if not tokens:
        print("✗ No tokens available, cannot continue")
        return
    
    # Create properties
    property_ids = create_properties(tokens)
    
    if not property_ids:
        print("✗ No properties created, cannot continue")
        return
    
    # Create leases
    lease_ids = create_leases(tokens, property_ids)
    
    # Create maintenance requests
    create_maintenance_requests(tokens, property_ids)
    
    # Create payments
    create_payments(tokens, property_ids)
    
    print(f"\n🎉 Database seeding completed!")
    print(f"Created:")
    print(f"  - {len(USERS)} users")
    print(f"  - {len(property_ids)} properties") 
    print(f"  - {len(lease_ids)} leases")
    print(f"  - Maintenance requests")
    print(f"  - Payment records")
    
    print(f"\n🔑 Login credentials:")
    for user in USERS:
        print(f"  {user['role'].title()}: {user['email']} / {user['password']}")

if __name__ == "__main__":
    main()
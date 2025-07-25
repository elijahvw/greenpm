#!/usr/bin/env python3
"""
Test creating a lease with proper tenant names
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_tenant_names():
    print("🧪 Testing lease creation with proper tenant names...")
    
    # Create a lease with proper tenant information
    new_lease_data = {
        "property_id": 408361,  # Use existing property
        "tenant_id": "john.doe.new@example.com",  # Completely new tenant email
        "tenant_first_name": "John",
        "tenant_last_name": "Doe", 
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "monthly_rent": 2500.00,
        "security_deposit": 2500.00,
        "status": "PENDING",  # Use PENDING to avoid validation issues
        "lease_terms": {
            "additional_terms": "Test lease with proper tenant name"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/leases", json=new_lease_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            lease_data = response.json()
            tenant_name = lease_data.get('tenantName') or lease_data.get('tenant_name')
            tenant_email = lease_data.get('tenantEmail') or lease_data.get('tenant_email')
            
            print(f"✅ Lease created successfully!")
            print(f"   Tenant Name: {tenant_name}")
            print(f"   Tenant Email: {tenant_email}")
            
            # Now check if the property shows the correct tenant
            print(f"\n🔍 Checking property display...")
            prop_response = requests.get(f"{BASE_URL}/properties")
            if prop_response.status_code == 200:
                properties = prop_response.json()
                for prop in properties:
                    if str(prop.get('id')) == str(new_lease_data['property_id']):
                        current_lease = prop.get('current_lease')
                        if current_lease:
                            prop_tenant_name = current_lease.get('tenant_name')
                            print(f"   Property shows tenant: {prop_tenant_name}")
                            if prop_tenant_name == "John Doe":
                                print(f"   ✅ Property correctly shows tenant name!")
                            else:
                                print(f"   ❌ Property still shows generic name")
                        break
            
            return True
        else:
            print(f"❌ Failed to create lease: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_tenant_names()
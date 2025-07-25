#!/usr/bin/env python3
"""
Simple test to create a lease with PENDING status
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_simple_create():
    print("🧪 Testing simple lease creation...")
    
    new_lease_data = {
        "property_id": 408361,  # Use existing property ID
        "tenant_id": "test@example.com",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "monthly_rent": 2000.00,
        "security_deposit": 2000.00,
        "status": "ACTIVE",  # Use ACTIVE status to trigger validation
        "lease_terms": {
            "additional_terms": "Test lease"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/leases", json=new_lease_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ Basic lease creation works!")
            return True
        else:
            print("❌ Basic lease creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_simple_create()
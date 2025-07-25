#!/usr/bin/env python3
"""
Test script to verify lease validation by trying to create a second active lease
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_create_duplicate_active_lease():
    print("🧪 Testing lease validation by creating duplicate active lease...")
    
    # First, get all leases to see current state
    print("\n1. Getting current leases...")
    try:
        response = requests.get(f"{BASE_URL}/leases")
        if response.status_code == 200:
            leases = response.json()
            print(f"   Found {len(leases)} leases")
            
            # Find a property with an active lease
            active_lease = None
            for lease in leases:
                if lease.get('status', '').upper() == 'ACTIVE':
                    active_lease = lease
                    break
            
            if not active_lease:
                print("   No active lease found to test with")
                return None
                
            property_id = active_lease.get('property_id') or active_lease.get('propertyId')
            print(f"   Found active lease {active_lease['id']} on property {property_id}")
            
            # Try to create another active lease on the same property
            print(f"\n2. Testing validation: Trying to create another active lease on property {property_id}...")
            
            new_lease_data = {
                "property_id": property_id,
                "tenant_id": "test@example.com",  # Use email as expected by create endpoint
                "start_date": "2024-01-01",
                "end_date": "2024-12-31", 
                "monthly_rent": 2000.00,
                "security_deposit": 2000.00,
                "status": "active",  # This should trigger validation error
                "lease_terms": {
                    "pet_policy": None,
                    "smoking_allowed": False,
                    "subletting_allowed": False,
                    "maintenance_responsibility": None,
                    "utilities_included": [],
                    "parking_included": False,
                    "additional_terms": "Test lease for validation"
                }
            }
            
            try:
                create_response = requests.post(f"{BASE_URL}/leases", json=new_lease_data)
                if create_response.status_code == 400:
                    error_detail = create_response.json().get('detail', 'Unknown error')
                    print(f"   ✅ Validation working! Error: {error_detail}")
                    return True
                else:
                    print(f"   ❌ Validation failed! Create succeeded when it should have failed. Status: {create_response.status_code}")
                    print(f"   Response: {create_response.json()}")
                    return False
            except Exception as e:
                print(f"   ❌ Error testing validation: {e}")
                return False
                
        else:
            print(f"   ❌ Failed to get leases: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = test_create_duplicate_active_lease()
    if result is True:
        print("\n🎉 Lease validation is working correctly!")
    elif result is False:
        print("\n❌ Lease validation is not working!")
    else:
        print("\n⚠️  Could not test validation (no suitable test data)")
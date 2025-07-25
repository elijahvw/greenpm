#!/usr/bin/env python3
"""
Test script to verify lease validation by trying to update a lease to active when another is already active
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_update_to_duplicate_active_lease():
    print("🧪 Testing lease validation by updating to duplicate active lease...")
    
    # First, get all leases to see current state
    print("\n1. Getting current leases...")
    try:
        response = requests.get(f"{BASE_URL}/leases")
        if response.status_code == 200:
            leases = response.json()
            print(f"   Found {len(leases)} leases")
            
            # Find a property with an active lease and a non-active lease
            active_lease = None
            non_active_lease = None
            
            for lease in leases:
                status = lease.get('status', '').upper()
                if status == 'ACTIVE' and not active_lease:
                    active_lease = lease
                elif status != 'ACTIVE' and not non_active_lease:
                    non_active_lease = lease
                    
                if active_lease and non_active_lease:
                    break
            
            if not active_lease:
                print("   No active lease found to test with")
                return None
                
            if not non_active_lease:
                print("   No non-active lease found to test with")
                return None
                
            active_property_id = active_lease.get('property_id') or active_lease.get('propertyId')
            non_active_lease_id = non_active_lease.get('id')
            
            print(f"   Found active lease {active_lease['id']} on property {active_property_id}")
            print(f"   Found non-active lease {non_active_lease_id}")
            
            # Try to update the non-active lease to be active on the same property as the active lease
            print(f"\n2. Testing validation: Trying to update lease {non_active_lease_id} to active on property {active_property_id}...")
            
            update_data = {
                "id": non_active_lease_id,
                "property_id": active_property_id,  # Same property as active lease
                "status": "active"  # This should trigger validation error
            }
            
            try:
                update_response = requests.put(f"{BASE_URL}/leases/{non_active_lease_id}", json=update_data)
                if update_response.status_code == 400:
                    error_detail = update_response.json().get('detail', 'Unknown error')
                    print(f"   ✅ Validation working! Error: {error_detail}")
                    return True
                else:
                    print(f"   ❌ Validation failed! Update succeeded when it should have failed. Status: {update_response.status_code}")
                    print(f"   Response: {update_response.json()}")
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
    result = test_update_to_duplicate_active_lease()
    if result is True:
        print("\n🎉 Lease validation is working correctly!")
    elif result is False:
        print("\n❌ Lease validation is not working!")
    else:
        print("\n⚠️  Could not test validation (no suitable test data)")
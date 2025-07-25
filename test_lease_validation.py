#!/usr/bin/env python3
"""
Test script to verify lease validation is working
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_lease_validation():
    print("🧪 Testing lease validation...")
    
    # First, get all leases to see current state
    print("\n1. Getting current leases...")
    try:
        response = requests.get(f"{BASE_URL}/leases")
        if response.status_code == 200:
            leases = response.json()
            print(f"   Found {len(leases)} leases")
            
            # Find leases by property
            property_leases = {}
            for lease in leases:
                prop_id = lease.get('property_id') or lease.get('propertyId')
                if prop_id not in property_leases:
                    property_leases[prop_id] = []
                property_leases[prop_id].append(lease)
            
            print("   Leases by property:")
            for prop_id, prop_leases in property_leases.items():
                active_count = sum(1 for l in prop_leases if l.get('status', '').upper() == 'ACTIVE')
                print(f"     Property {prop_id}: {len(prop_leases)} leases ({active_count} active)")
                
                # Test updating a non-active lease to active if there's already an active one
                if active_count >= 1:
                    non_active_lease = next((l for l in prop_leases if l.get('status', '').upper() != 'ACTIVE'), None)
                    if non_active_lease:
                        print(f"\n2. Testing validation: Trying to activate lease {non_active_lease['id']} when property {prop_id} already has active lease...")
                        
                        update_data = {
                            "id": non_active_lease['id'],
                            "status": "active"
                        }
                        
                        try:
                            update_response = requests.put(f"{BASE_URL}/leases/{non_active_lease['id']}", json=update_data)
                            if update_response.status_code == 400:
                                error_detail = update_response.json().get('detail', 'Unknown error')
                                print(f"   ✅ Validation working! Error: {error_detail}")
                                return True
                            else:
                                print(f"   ❌ Validation failed! Update succeeded when it should have failed. Status: {update_response.status_code}")
                                return False
                        except Exception as e:
                            print(f"   ❌ Error testing validation: {e}")
                            return False
                        
            print("   No suitable test case found (need property with active lease + non-active lease)")
            return None
            
        else:
            print(f"   ❌ Failed to get leases: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = test_lease_validation()
    if result is True:
        print("\n🎉 Lease validation is working correctly!")
    elif result is False:
        print("\n❌ Lease validation is not working!")
    else:
        print("\n⚠️  Could not test validation (no suitable test data)")
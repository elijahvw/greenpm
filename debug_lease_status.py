#!/usr/bin/env python3
"""
Debug script to check lease statuses in the database
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def debug_lease_statuses():
    print("🔍 Debugging lease statuses...")
    
    try:
        response = requests.get(f"{BASE_URL}/leases")
        if response.status_code == 200:
            leases = response.json()
            print(f"\nFound {len(leases)} leases:")
            
            for lease in leases:
                lease_id = lease.get('id')
                property_id = lease.get('property_id') or lease.get('propertyId')
                status = lease.get('status')
                print(f"  Lease {lease_id}: Property {property_id}, Status: '{status}' (type: {type(status)})")
                
                # Check if status is exactly 'ACTIVE'
                if status == 'ACTIVE':
                    print(f"    ✅ This lease has ACTIVE status (uppercase)")
                elif status and status.upper() == 'ACTIVE':
                    print(f"    ⚠️  This lease has active status but not uppercase: '{status}'")
                else:
                    print(f"    ℹ️  This lease is not active: '{status}'")
                    
        else:
            print(f"❌ Failed to get leases: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_lease_statuses()
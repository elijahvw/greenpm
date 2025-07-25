#!/usr/bin/env python3
"""
Check what enum values exist in the database
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

def check_enum_values():
    print("🔍 Checking lease status enum values...")
    
    try:
        response = requests.get(f"{BASE_URL}/leases")
        if response.status_code == 200:
            leases = response.json()
            print(f"\nFound {len(leases)} leases:")
            
            statuses = set()
            for lease in leases:
                status = lease.get('status')
                if status:
                    statuses.add(status)
                    
            print(f"Unique status values found: {sorted(statuses)}")
            
            # Check if any lease has exactly 'ACTIVE' status
            active_leases = [l for l in leases if l.get('status') == 'ACTIVE']
            print(f"Leases with 'ACTIVE' status: {len(active_leases)}")
            
            # Check if any lease has 'active' status  
            active_lower_leases = [l for l in leases if l.get('status') == 'active']
            print(f"Leases with 'active' status: {len(active_lower_leases)}")
            
        else:
            print(f"❌ Failed to get leases: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_enum_values()
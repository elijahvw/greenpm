#!/usr/bin/env python3
"""
Debug script to check tenant data in the database
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def debug_tenant_data():
    print("🔍 Debugging tenant data in properties...")
    
    try:
        # Get properties
        response = requests.get(f"{BASE_URL}/properties")
        if response.status_code == 200:
            properties = response.json()
            print(f"\nFound {len(properties)} properties:")
            
            for prop in properties:
                prop_id = prop.get('id')
                prop_title = prop.get('title', 'Unknown')
                current_lease = prop.get('current_lease')
                
                print(f"\nProperty {prop_id}: {prop_title}")
                
                if current_lease:
                    tenant_name = current_lease.get('tenant_name')
                    tenant_email = current_lease.get('tenant_email')
                    tenant_id = current_lease.get('tenant_id')
                    lease_status = current_lease.get('status')
                    
                    print(f"  Current Lease:")
                    print(f"    Tenant ID: {tenant_id}")
                    print(f"    Tenant Name: '{tenant_name}'")
                    print(f"    Tenant Email: {tenant_email}")
                    print(f"    Lease Status: {lease_status}")
                    
                    if tenant_name == "Unknown Tenant" or not tenant_name.strip():
                        print(f"    ⚠️  Issue: Tenant name is missing or generic")
                else:
                    print(f"  No current lease (vacant)")
                    
        else:
            print(f"❌ Failed to get properties: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_tenant_data()
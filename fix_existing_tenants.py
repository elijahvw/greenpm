#!/usr/bin/env python3
"""
Fix existing tenants with generic "Tenant User" names
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def fix_existing_tenants():
    print("🔧 Fixing existing tenants with generic names...")
    
    try:
        # Get all properties to find tenants with generic names
        response = requests.get(f"{BASE_URL}/properties")
        if response.status_code == 200:
            properties = response.json()
            
            tenants_to_fix = []
            for prop in properties:
                current_lease = prop.get('current_lease')
                if current_lease:
                    tenant_name = current_lease.get('tenant_name')
                    if tenant_name == "Tenant User":
                        tenant_id = current_lease.get('tenant_id')
                        tenant_email = current_lease.get('tenant_email')
                        tenants_to_fix.append({
                            'tenant_id': tenant_id,
                            'tenant_email': tenant_email,
                            'property_title': prop.get('title', 'Unknown Property')
                        })
            
            print(f"Found {len(tenants_to_fix)} tenants to fix:")
            
            for i, tenant in enumerate(tenants_to_fix):
                tenant_id = tenant['tenant_id']
                tenant_email = tenant['tenant_email']
                property_title = tenant['property_title']
                
                # Generate a meaningful name based on email or property
                if '@' in tenant_email:
                    email_part = tenant_email.split('@')[0]
                    # Convert email part to a name (e.g., "john.doe" -> "John Doe")
                    if '.' in email_part:
                        parts = email_part.split('.')
                        first_name = parts[0].capitalize()
                        last_name = parts[1].capitalize() if len(parts) > 1 else "Tenant"
                    else:
                        first_name = email_part.capitalize()
                        last_name = "Tenant"
                else:
                    # Fallback to property-based naming
                    first_name = f"Tenant{i+1}"
                    last_name = "User"
                
                print(f"\n  Tenant {tenant_id} ({tenant_email}):")
                print(f"    Property: {property_title}")
                print(f"    New name: {first_name} {last_name}")
                
                # Update the tenant using the API
                update_data = {
                    "firstName": first_name,
                    "lastName": last_name
                }
                
                try:
                    update_response = requests.put(f"{BASE_URL}/users/tenants/{tenant_id}", json=update_data)
                    if update_response.status_code == 200:
                        print(f"    ✅ Updated successfully!")
                    else:
                        print(f"    ❌ Update failed: {update_response.status_code} - {update_response.text}")
                except Exception as update_error:
                    print(f"    ❌ Update error: {update_error}")
                
        else:
            print(f"❌ Failed to get properties: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_existing_tenants()
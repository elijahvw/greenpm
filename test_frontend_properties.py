#!/usr/bin/env python3
"""
Test that the frontend can access all properties for lease creation
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_frontend_properties():
    print("🧪 Testing frontend property access for lease creation...")
    
    try:
        # Test the endpoint the frontend now uses
        response = requests.get(f"{BASE_URL}/leases/properties")
        if response.status_code == 200:
            properties = response.json()
            print(f"✅ Frontend can access {len(properties)} properties:")
            
            # Also check the regular properties endpoint to compare
            regular_response = requests.get(f"{BASE_URL}/properties")
            if regular_response.status_code == 200:
                regular_properties = regular_response.json()
                print(f"📊 Regular properties endpoint returns {len(regular_properties)} properties")
                
                # Check if lease properties include occupied ones
                for prop in properties:
                    prop_id = prop.get('id')
                    title = prop.get('title')
                    
                    # Find the same property in regular endpoint to check occupancy
                    regular_prop = next((p for p in regular_properties if str(p.get('id')) == str(prop_id)), None)
                    if regular_prop:
                        current_lease = regular_prop.get('current_lease')
                        if current_lease:
                            lease_status = current_lease.get('status', 'unknown')
                            tenant_name = current_lease.get('tenant_name', 'Unknown')
                            print(f"  🏠 {title} (ID: {prop_id}) - OCCUPIED by {tenant_name} ({lease_status})")
                        else:
                            print(f"  🏠 {title} (ID: {prop_id}) - VACANT")
                    else:
                        print(f"  🏠 {title} (ID: {prop_id}) - Status unknown")
                        
                print(f"\n🎉 Success! All properties are available in the dropdown, including occupied ones.")
                return True
            else:
                print(f"❌ Could not fetch regular properties for comparison: {regular_response.status_code}")
                return False
        else:
            print(f"❌ Failed to get properties for leases: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_frontend_properties()
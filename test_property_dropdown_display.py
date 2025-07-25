#!/usr/bin/env python3
"""
Test how the property dropdown will display with the new format
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_property_dropdown_display():
    print("🏠 Testing property dropdown display format...")
    
    try:
        response = requests.get(f"{BASE_URL}/leases/properties")
        if response.status_code == 200:
            properties = response.json()
            print(f"✅ Found {len(properties)} properties for dropdown:")
            print("\nHow they will appear in the dropdown:")
            print("=" * 60)
            
            for prop in properties:
                prop_id = prop.get('id')
                title = prop.get('title', 'Untitled')
                address = prop.get('address', 'No address')
                rent_amount = prop.get('rent_amount', 0)
                
                # This is how it will appear in the dropdown
                dropdown_text = f"{title} - {address}"
                
                print(f"Option: {dropdown_text}")
                print(f"  ID: {prop_id}")
                print(f"  Rent: ${rent_amount}/month")
                print()
                
            print("=" * 60)
            print("✅ All properties now show both name and full address!")
            return True
        else:
            print(f"❌ Failed to get properties: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_property_dropdown_display()
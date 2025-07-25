#!/usr/bin/env python3
"""
Test the properties dropdown endpoint
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_properties_dropdown():
    print("🏠 Testing properties dropdown endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/leases/properties")
        if response.status_code == 200:
            properties = response.json()
            print(f"✅ Found {len(properties)} properties for lease creation:")
            
            for prop in properties:
                prop_id = prop.get('id')
                title = prop.get('title')
                address = prop.get('address')
                rent = prop.get('rent_amount', 0)
                bedrooms = prop.get('bedrooms', 0)
                bathrooms = prop.get('bathrooms', 0)
                
                print(f"\n  Property {prop_id}: {title}")
                print(f"    Address: {address}")
                print(f"    Rent: ${rent}/month")
                print(f"    Bedrooms: {bedrooms}, Bathrooms: {bathrooms}")
                
            return True
        else:
            print(f"❌ Failed to get properties: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_properties_dropdown()
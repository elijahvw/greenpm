#!/usr/bin/env python3
"""
Test navigation and filtering functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_property_lease_relationships():
    print("🔗 Testing Property-to-Lease Navigation and Filtering...")
    
    # 1. Get all properties
    print("\n🏠 Available Properties:")
    properties = requests.get(f"{BASE_URL}/properties").json()
    for prop in properties:
        print(f"  ID: {prop['id']} - {prop['name']} ({prop.get('address', 'No address')})")
    
    # 2. Get all leases
    print("\n📝 All Leases:")
    leases = requests.get(f"{BASE_URL}/leases").json()
    for lease in leases:
        print(f"  Lease ID: {lease['id']} - Property: {lease.get('property_name', 'Unknown')} - Tenant: {lease.get('tenant_name', 'Unknown')}")
    
    # 3. Test filtering leases by property
    print("\n🔍 Testing Property Filter (Property ID: 1):")
    property_1_leases = [lease for lease in leases if lease.get('propertyId') == '1' or lease.get('property_id') == '1']
    
    if property_1_leases:
        print(f"  ✅ Found {len(property_1_leases)} lease(s) for Property 1:")
        for lease in property_1_leases:
            print(f"    - Lease {lease['id']}: {lease.get('tenant_name', 'Unknown tenant')}")
            print(f"      Dates: {lease.get('startDate', lease.get('start_date', 'Unknown'))} to {lease.get('endDate', lease.get('end_date', 'Unknown'))}")
    else:
        print("  ⚠️  No leases found for Property 1")
    
    print("\n🔍 Testing Property Filter (Property ID: 2):")
    property_2_leases = [lease for lease in leases if lease.get('propertyId') == '2' or lease.get('property_id') == '2']
    
    if property_2_leases:
        print(f"  ✅ Found {len(property_2_leases)} lease(s) for Property 2:")
        for lease in property_2_leases:
            print(f"    - Lease {lease['id']}: {lease.get('tenant_name', 'Unknown tenant')}")
            print(f"      Dates: {lease.get('startDate', lease.get('start_date', 'Unknown'))} to {lease.get('endDate', lease.get('end_date', 'Unknown'))}")
    else:
        print("  ⚠️  No leases found for Property 2")
    
    # 4. Test security deposits for these leases
    print("\n💰 Security Deposits Connected to Leases:")
    deposits = requests.get(f"{BASE_URL}/security-deposits").json()
    for deposit in deposits:
        lease_id = deposit.get('leaseId')
        matching_lease = next((l for l in leases if l['id'] == lease_id), None)
        if matching_lease:
            print(f"  Deposit {deposit['id']} (${deposit['amount']}) → Lease {lease_id} → {deposit.get('tenant_name', 'Unknown')}")
            print(f"    Status: {deposit['status']} | Deductions: ${deposit.get('totalDeductions', 0)} | Available: ${deposit.get('refundAmount', deposit['amount'])}")
        
    print("\n🎉 Navigation and filtering tests complete!")

if __name__ == "__main__":
    test_property_lease_relationships()
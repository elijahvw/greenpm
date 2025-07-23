#!/usr/bin/env python3
"""
Test script to validate all data relationships are working correctly
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_relationships():
    print("🧪 Testing Green PM Data Relationships...")
    
    # 1. Get initial data counts
    print("\n📊 Initial Data State:")
    properties = requests.get(f"{BASE_URL}/properties").json()
    tenants = requests.get(f"{BASE_URL}/tenants").json()
    leases = requests.get(f"{BASE_URL}/leases").json()
    deposits = requests.get(f"{BASE_URL}/security-deposits").json()
    
    print(f"  Properties: {len(properties)}")
    print(f"  Tenants: {len(tenants)}")
    print(f"  Leases: {len(leases)}")
    print(f"  Security Deposits: {len(deposits)}")
    
    # 2. Test security deposit data relationships
    print("\n🔗 Testing Security Deposit Relationships:")
    for deposit in deposits[:2]:  # Test first 2 deposits
        print(f"\n  Deposit ID: {deposit['id']}")
        print(f"  Tenant: {deposit.get('tenant_name', 'Unknown')}")
        print(f"  Property: {deposit.get('property_address', 'Unknown')}")
        print(f"  Amount: ${deposit['amount']}")
        print(f"  Status: {deposit['status']}")
        print(f"  Deductions: {len(deposit.get('deductions', []))}")
        print(f"  Total Deductions: ${deposit.get('totalDeductions', 0)}")
    
    # 3. Test adding a deduction
    print("\n💰 Testing Deduction Addition:")
    test_deposit_id = "1"
    deduction_data = {
        "date": "2024-07-22",
        "amount": 150,
        "description": "Wall painting repair",
        "category": "damage",
        "notes": "Repaint due to nail holes"
    }
    
    print(f"  Adding ${deduction_data['amount']} deduction to deposit {test_deposit_id}")
    response = requests.post(
        f"{BASE_URL}/security-deposits/{test_deposit_id}/deductions",
        json=deduction_data
    )
    
    if response.status_code == 200:
        updated_deposit = response.json()
        print(f"  ✅ Deduction added successfully!")
        print(f"  New total deductions: ${updated_deposit.get('totalDeductions', 0)}")
        print(f"  New status: {updated_deposit.get('status', 'unknown')}")
        print(f"  Refund amount: ${updated_deposit.get('refundAmount', 0)}")
    else:
        print(f"  ❌ Failed to add deduction: {response.status_code}")
    
    # 4. Test lease creation with security deposit
    print("\n📝 Testing Lease Creation with Auto Security Deposit:")
    new_lease_data = {
        "propertyId": "1",
        "tenantId": "2",  # Use different tenant to avoid conflicts
        "startDate": "2024-08-01",
        "endDate": "2025-07-31",
        "monthlyRent": 1800,
        "securityDeposit": 1800,
        "lateFeePenalty": 50,
        "gracePeriodDays": 5,
        "leaseType": "fixed",
        "renewalOption": True,
        "notes": "Test lease created via API"
    }
    
    initial_lease_count = len(leases)
    initial_deposit_count = len(deposits)
    
    response = requests.post(f"{BASE_URL}/leases", json=new_lease_data)
    if response.status_code == 200:
        new_lease = response.json()
        print(f"  ✅ Lease created with ID: {new_lease['id']}")
        print(f"  Property: {new_lease.get('property_name', 'Unknown')}")
        print(f"  Tenant: {new_lease.get('tenant_name', 'Unknown')}")
        
        # Check if security deposit was auto-created
        updated_deposits = requests.get(f"{BASE_URL}/security-deposits").json()
        if len(updated_deposits) > initial_deposit_count:
            print(f"  ✅ Security deposit auto-created!")
            latest_deposit = updated_deposits[-1]  # Get the last deposit
            print(f"  Deposit ID: {latest_deposit['id']}")
            print(f"  Amount: ${latest_deposit['amount']}")
            print(f"  Connected to lease: {latest_deposit['leaseId']}")
        else:
            print(f"  ⚠️  No new security deposit found")
    else:
        print(f"  ❌ Failed to create lease: {response.status_code}")
    
    # 5. Final summary
    print("\n📊 Final Data State:")
    final_properties = requests.get(f"{BASE_URL}/properties").json()
    final_tenants = requests.get(f"{BASE_URL}/tenants").json()
    final_leases = requests.get(f"{BASE_URL}/leases").json()
    final_deposits = requests.get(f"{BASE_URL}/security-deposits").json()
    
    print(f"  Properties: {len(final_properties)}")
    print(f"  Tenants: {len(final_tenants)}")
    print(f"  Leases: {len(final_leases)}")
    print(f"  Security Deposits: {len(final_deposits)}")
    
    print("\n🎉 Relationship testing complete!")

if __name__ == "__main__":
    test_relationships()
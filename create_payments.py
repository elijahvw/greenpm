#!/usr/bin/env python3
"""
Create payments with proper lease_id
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def get_token(email, password):
    response = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"], response.json()["user"]
    return None, None

def create_payments():
    # Get landlord token
    landlord_token, landlord_user = get_token("landlord1@example.com", "landlord123")
    if not landlord_token:
        print("Failed to get landlord token")
        return
    
    headers = {"Authorization": f"Bearer {landlord_token}"}
    
    # Get leases
    leases_response = requests.get(f"{BASE_URL}/leases", headers=headers)
    if leases_response.status_code != 200:
        print("Failed to get leases")
        return
    
    leases = leases_response.json()
    print(f"Found {len(leases)} leases")
    
    # Create payments for the last 3 months
    for month_offset in range(3):
        payment_date = datetime.now() - timedelta(days=30 * month_offset)
        
        for i, lease in enumerate(leases):
            payment_data = {
                "lease_id": lease["id"],
                "amount": lease["rent_amount"],
                "payment_date": payment_date.strftime("%Y-%m-%d"),
                "payment_method": ["bank_transfer", "credit_card", "check"][i % 3],
                "status": "completed" if month_offset > 0 else ["completed", "pending"][i % 2],
                "description": f"Rent payment for {payment_date.strftime('%B %Y')}"
            }
            
            try:
                response = requests.post(f"{BASE_URL}/payments", json=payment_data, headers=headers)
                if response.status_code in [200, 201]:
                    print(f"✓ Created payment: Lease {lease['id'][:8]}... - {payment_date.strftime('%B %Y')} - ${payment_data['amount']}")
                else:
                    print(f"✗ Failed to create payment: {response.text}")
            except Exception as e:
                print(f"✗ Error creating payment: {e}")

def main():
    print("💰 Creating payments...")
    create_payments()
    print("✅ Payment creation completed!")

if __name__ == "__main__":
    main()
"""
Green PM - Simplified Database Configuration for Demo
"""
import sqlite3
import os
from contextlib import contextmanager
from typing import Dict, List, Any, Optional
import json
import hashlib
from datetime import datetime
import uuid

# Simple in-memory database for demo
DB_PATH = "/tmp/greenpm_demo.db"

class SimpleDatabase:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        """Initialize database with tables"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                is_verified INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                company_id TEXT,
                phone TEXT,
                address TEXT
            )
        """)
        
        # Properties table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id TEXT PRIMARY KEY,
                owner_id TEXT NOT NULL,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                type TEXT NOT NULL,
                bedrooms INTEGER,
                bathrooms INTEGER,
                square_feet INTEGER,
                rent_amount REAL,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users (id)
            )
        """)
        
        # Leases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leases (
                id TEXT PRIMARY KEY,
                property_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                rent_amount REAL NOT NULL,
                security_deposit REAL,
                late_fee_penalty REAL DEFAULT 0.0,
                grace_period_days INTEGER DEFAULT 5,
                lease_type TEXT DEFAULT 'fixed',
                renewal_option BOOLEAN DEFAULT FALSE,
                pet_policy_allowed BOOLEAN DEFAULT FALSE,
                pet_policy_deposit REAL DEFAULT 0.0,
                pet_policy_monthly_fee REAL DEFAULT 0.0,
                pet_policy_restrictions TEXT,
                utilities_included TEXT,
                tenant_responsibilities TEXT,
                landlord_responsibilities TEXT,
                special_terms TEXT,
                notes TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties (id),
                FOREIGN KEY (tenant_id) REFERENCES users (id)
            )
        """)
        
        # Maintenance Requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_requests (
                id TEXT PRIMARY KEY,
                property_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'open',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties (id),
                FOREIGN KEY (tenant_id) REFERENCES users (id)
            )
        """)
        
        # Payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                lease_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL,
                payment_method TEXT,
                status TEXT DEFAULT 'completed',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lease_id) REFERENCES leases (id),
                FOREIGN KEY (tenant_id) REFERENCES users (id)
            )
        """)
        
        # Companies table (for SaaS admin)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                subscription_plan TEXT DEFAULT 'basic',
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Insert demo data
        self.insert_demo_data()
    
    def insert_demo_data(self):
        """Insert demo data for testing"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Demo companies
        companies = [
            {
                'id': str(uuid.uuid4()),
                'name': 'Green Property Management',
                'email': 'info@greenpm.com',
                'phone': '555-0100',
                'address': '123 Business St, City, ST 12345',
                'subscription_plan': 'premium'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Sunrise Properties',
                'email': 'contact@sunriseprops.com',
                'phone': '555-0200',
                'address': '456 Commerce Ave, City, ST 12345',
                'subscription_plan': 'basic'
            }
        ]
        
        for company in companies:
            cursor.execute("""
                INSERT INTO companies (id, name, email, phone, address, subscription_plan)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company['id'], company['name'], company['email'], 
                  company['phone'], company['address'], company['subscription_plan']))
        
        # Demo users
        users = [
            {
                'id': str(uuid.uuid4()),
                'email': 'admin@greenpm.com',
                'first_name': 'Green PM',
                'last_name': 'Administrator',
                'password_hash': self.hash_password('GreenPM2024!'),
                'role': 'admin',
                'company_id': companies[0]['id']
            },
            {
                'id': str(uuid.uuid4()),
                'email': 'landlord@example.com',
                'first_name': 'John',
                'last_name': 'Landlord',
                'password_hash': self.hash_password('landlord123'),
                'role': 'landlord',
                'company_id': companies[0]['id'],
                'phone': '555-0301',
                'address': '789 Landlord Lane, City, ST 12345'
            },
            {
                'id': str(uuid.uuid4()),
                'email': 'tenant@example.com',
                'first_name': 'Jane',
                'last_name': 'Tenant',
                'password_hash': self.hash_password('tenant123'),
                'role': 'tenant',
                'company_id': companies[0]['id'],
                'phone': '555-0401',
                'address': '101 Tenant Dr, City, ST 12345'
            }
        ]
        
        for user in users:
            cursor.execute("""
                INSERT INTO users (id, email, first_name, last_name, password_hash, role, company_id, phone, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user['id'], user['email'], user['first_name'], user['last_name'],
                  user['password_hash'], user['role'], user.get('company_id'), 
                  user.get('phone'), user.get('address')))
        
        # Demo properties
        landlord_id = users[1]['id']  # John Landlord
        properties = [
            {
                'id': str(uuid.uuid4()),
                'owner_id': landlord_id,
                'name': 'Sunset Apartments',
                'address': '123 Main St, City, ST 12345',
                'type': 'apartment',
                'bedrooms': 2,
                'bathrooms': 1,
                'square_feet': 1000,
                'rent_amount': 1500.00,
                'description': 'Beautiful 2-bedroom apartment in downtown area'
            },
            {
                'id': str(uuid.uuid4()),
                'owner_id': landlord_id,
                'name': 'Green Valley Condos',
                'address': '456 Oak Ave, City, ST 12345',
                'type': 'condo',
                'bedrooms': 3,
                'bathrooms': 2,
                'square_feet': 1200,
                'rent_amount': 1800.00,
                'description': 'Modern 3-bedroom condo with amenities'
            }
        ]
        
        for prop in properties:
            cursor.execute("""
                INSERT INTO properties (id, owner_id, name, address, type, bedrooms, bathrooms, square_feet, rent_amount, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (prop['id'], prop['owner_id'], prop['name'], prop['address'],
                  prop['type'], prop['bedrooms'], prop['bathrooms'], 
                  prop['square_feet'], prop['rent_amount'], prop['description']))
        
        # Demo leases
        tenant_id = users[2]['id']  # Jane Tenant
        leases = [
            {
                'id': str(uuid.uuid4()),
                'property_id': properties[0]['id'],
                'tenant_id': tenant_id,
                'start_date': '2024-01-01',
                'end_date': '2024-12-31',
                'rent_amount': 1500.00,
                'security_deposit': 1500.00,
                'status': 'active'
            }
        ]
        
        for lease in leases:
            cursor.execute("""
                INSERT INTO leases (id, property_id, tenant_id, start_date, end_date, rent_amount, security_deposit, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (lease['id'], lease['property_id'], lease['tenant_id'],
                  lease['start_date'], lease['end_date'], lease['rent_amount'],
                  lease['security_deposit'], lease['status']))
        
        # Demo maintenance requests
        maintenance_requests = [
            {
                'id': str(uuid.uuid4()),
                'property_id': properties[0]['id'],
                'tenant_id': tenant_id,
                'title': 'Leaky Faucet',
                'description': 'Kitchen faucet is dripping constantly',
                'priority': 'high',
                'status': 'open'
            },
            {
                'id': str(uuid.uuid4()),
                'property_id': properties[0]['id'],
                'tenant_id': tenant_id,
                'title': 'AC Not Working',
                'description': 'Air conditioning unit stopped working',
                'priority': 'medium',
                'status': 'in_progress'
            }
        ]
        
        for req in maintenance_requests:
            cursor.execute("""
                INSERT INTO maintenance_requests (id, property_id, tenant_id, title, description, priority, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (req['id'], req['property_id'], req['tenant_id'],
                  req['title'], req['description'], req['priority'], req['status']))
        
        # Demo payments
        payments = [
            {
                'id': str(uuid.uuid4()),
                'lease_id': leases[0]['id'],
                'tenant_id': tenant_id,
                'amount': 1500.00,
                'payment_date': '2024-01-01',
                'payment_method': 'bank_transfer',
                'status': 'completed'
            },
            {
                'id': str(uuid.uuid4()),
                'lease_id': leases[0]['id'],
                'tenant_id': tenant_id,
                'amount': 1500.00,
                'payment_date': '2024-02-01',
                'payment_method': 'bank_transfer',
                'status': 'completed'
            }
        ]
        
        for payment in payments:
            cursor.execute("""
                INSERT INTO payments (id, lease_id, tenant_id, amount, payment_date, payment_method, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (payment['id'], payment['lease_id'], payment['tenant_id'],
                  payment['amount'], payment['payment_date'], payment['payment_method'],
                  payment['status']))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Simple password hashing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self.hash_password(password) == password_hash
    
    @contextmanager
    def get_connection(self):
        """Get database connection context manager"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an update/insert query"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

# Global database instance
db = SimpleDatabase()
#!/usr/bin/env python3
"""
Database seeding script for Green PM
Creates initial admin user and sample data
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend src directory to Python path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.core.database import AsyncSessionLocal, engine, Base
from src.core.security import SecurityManager
from src.models.user import User
from src.models.property import Property
from src.models.lease import Lease
from src.models.payment import Payment
from src.models.maintenance import MaintenanceRequest
from src.models.application import Application
from src.models.message import Message
from src.models.audit import AuditLog
import uuid
from datetime import datetime, timedelta

async def create_tables():
    """Create all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully")

async def create_admin_user():
    """Create the master admin user"""
    admin_password = "GreenPM2024!"
    
    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        existing_admin = await session.execute(
            text("SELECT id FROM users WHERE email = 'admin@greenpm.com'")
        )
        if existing_admin.scalar():
            print("❌ Admin user already exists")
            return admin_password
        
        # Create admin user
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@greenpm.com",
            first_name="Green PM",
            last_name="Administrator",
            password_hash=SecurityManager.hash_password(admin_password),
            role="admin",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(admin_user)
        await session.commit()
        
        print(f"✅ Master admin user created:")
        print(f"   Email: admin@greenpm.com")
        print(f"   Password: {admin_password}")
        print(f"   Role: admin")
        
        return admin_password

async def create_sample_landlord():
    """Create a sample landlord user"""
    landlord_password = "landlord123"
    
    async with AsyncSessionLocal() as session:
        # Check if landlord already exists
        existing_landlord = await session.execute(
            "SELECT id FROM users WHERE email = 'landlord@example.com'"
        )
        if existing_landlord.scalar():
            print("❌ Sample landlord already exists")
            return landlord_password
        
        # Create landlord user
        landlord_user = User(
            id=uuid.uuid4(),
            email="landlord@example.com",
            first_name="John",
            last_name="Landlord",
            password_hash=SecurityManager.hash_password(landlord_password),
            role="landlord",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(landlord_user)
        await session.commit()
        
        print(f"✅ Sample landlord user created:")
        print(f"   Email: landlord@example.com")
        print(f"   Password: {landlord_password}")
        print(f"   Role: landlord")
        
        return landlord_password

async def create_sample_tenant():
    """Create a sample tenant user"""
    tenant_password = "tenant123"
    
    async with AsyncSessionLocal() as session:
        # Check if tenant already exists
        existing_tenant = await session.execute(
            "SELECT id FROM users WHERE email = 'tenant@example.com'"
        )
        if existing_tenant.scalar():
            print("❌ Sample tenant already exists")
            return tenant_password
        
        # Create tenant user
        tenant_user = User(
            id=uuid.uuid4(),
            email="tenant@example.com",
            first_name="Jane",
            last_name="Tenant",
            password_hash=SecurityManager.hash_password(tenant_password),
            role="tenant",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(tenant_user)
        await session.commit()
        
        print(f"✅ Sample tenant user created:")
        print(f"   Email: tenant@example.com")
        print(f"   Password: {tenant_password}")
        print(f"   Role: tenant")
        
        return tenant_password

async def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    
    try:
        # Create tables
        await create_tables()
        
        # Create users
        admin_password = await create_admin_user()
        landlord_password = await create_sample_landlord()
        tenant_password = await create_sample_tenant()
        
        print("\n🎉 Database seeding completed successfully!")
        print("\n📋 Login Credentials:")
        print(f"   Master Admin: admin@greenpm.com / {admin_password}")
        print(f"   Sample Landlord: landlord@example.com / {landlord_password}")
        print(f"   Sample Tenant: tenant@example.com / {tenant_password}")
        print("\n🌐 Access your application at: https://34.8.153.46")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
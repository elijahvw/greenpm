#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models.user import User, UserRole, UserStatus
from src.core.security import security
from src.core.config import settings

async def create_test_landlord():
    # Create database engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Check if landlord already exists
        existing_user = await db.get(User, 1)  # assuming ID 1
        if existing_user and existing_user.email == "landlord@test.com":
            print(f"Landlord user already exists: {existing_user.email}")
            # Update password to ensure it works
            existing_user.hashed_password = security.hash_password("password123")
            existing_user.is_active = True
            existing_user.status = UserStatus.ACTIVE
            await db.commit()
            print("Updated landlord password to: password123")
        else:
            # Create new landlord user
            landlord = User(
                email="landlord@test.com",
                hashed_password=security.hash_password("password123"),
                first_name="Test",
                last_name="Landlord",
                phone="555-0123",
                role=UserRole.LANDLORD,
                status=UserStatus.ACTIVE,
                is_active=True,
                email_verified=True
            )
            
            db.add(landlord)
            await db.commit()
            await db.refresh(landlord)
            print(f"Created landlord user: {landlord.email}")
            print("Password: password123")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_test_landlord())
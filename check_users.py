#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from src.models.user import User, UserRole
from src.core.config import settings

async def check_users():
    # Create database engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Check all users
        stmt = select(User)
        result = await db.execute(stmt)
        all_users = result.scalars().all()
        
        print(f"Total users: {len(all_users)}")
        print("\nAll users:")
        for user in all_users:
            print(f"  ID: {user.id}, Email: {user.email}, Role: {user.role}, Status: {user.status}, Active: {user.is_active}")
        
        # Check landlord accounts specifically
        stmt = select(User).where(User.role == UserRole.LANDLORD)
        result = await db.execute(stmt)
        landlords = result.scalars().all()
        
        print(f"\nLandlord accounts: {len(landlords)}")
        for user in landlords:
            print(f"  Email: {user.email}, Status: {user.status}, Active: {user.is_active}, Password set: {bool(user.hashed_password)}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_users())
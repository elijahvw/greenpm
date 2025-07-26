#!/usr/bin/env python3
"""
Create Alembic migration for multi-tenant support
"""
import os
import sys
sys.path.append('.')

from alembic.config import Config
from alembic import command

def create_migration():
    """Create the multi-tenant migration"""
    
    # Set up Alembic config
    alembic_cfg = Config("alembic.ini")
    
    # Create the migration
    command.revision(
        alembic_cfg,
        message="Add multi-tenant support - companies, plans, feature flags, contracts",
        autogenerate=True
    )
    
    print("✅ Multi-tenant migration created successfully!")
    print("📝 Review the generated migration file before running it")
    print("🚀 Run with: alembic upgrade head")

if __name__ == "__main__":
    create_migration()
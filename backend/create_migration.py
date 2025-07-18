#!/usr/bin/env python3
"""
Create migration files offline without database connection
"""
import os
import sys
from datetime import datetime

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from alembic import command
from alembic.config import Config

# Create Alembic config
config = Config("alembic.ini")

# Generate migration with fake database URL
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/dbname"

try:
    command.revision(config, autogenerate=True, message="Initial migration")
    print("Migration created successfully!")
except Exception as e:
    print(f"Error creating migration: {e}")
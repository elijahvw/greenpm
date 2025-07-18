#!/usr/bin/env python3
"""
Run database migrations
"""
import os
import sys
import subprocess

def run_migrations():
    """Run Alembic migrations"""
    try:
        # Check if DATABASE_URL is set
        if not os.getenv("DATABASE_URL"):
            print("ERROR: DATABASE_URL environment variable is not set")
            return False
            
        print("Running database migrations...")
        result = subprocess.run(
            ["python", "-m", "alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True
        )
        
        print("Migrations completed successfully!")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Migration failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
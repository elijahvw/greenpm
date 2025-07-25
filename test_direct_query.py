#!/usr/bin/env python3
"""
Test the validation query directly
"""
import asyncio
import asyncpg
import os

async def test_query():
    print("🔍 Testing validation query directly...")
    
    # Database connection details (from the working server)
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/greenpm"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Test the exact query used in validation
        query = """
            SELECT id FROM leases 
            WHERE property_id = $1 
            AND status::text = 'ACTIVE'
        """
        
        property_id = 408361
        result = await conn.fetch(query, property_id)
        
        print(f"Query result for property {property_id}: {result}")
        
        if result:
            print(f"✅ Found {len(result)} active lease(s) on property {property_id}")
            for row in result:
                print(f"   - Lease ID: {row['id']}")
        else:
            print(f"ℹ️  No active leases found on property {property_id}")
            
        await conn.close()
        
    except Exception as e:
        print(f"❌ Query error: {e}")

if __name__ == "__main__":
    asyncio.run(test_query())
#!/usr/bin/env python3
"""
Migrate existing single-tenant data to multi-tenant structure
"""
import asyncio
import json
import sys
sys.path.append('.')

from sqlalchemy import text
from src.core.database import AsyncSessionLocal

async def migrate_existing_data():
    """Migrate existing data to multi-tenant structure"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    async with AsyncSessionLocal() as db:
        try:
            print("🔄 Starting data migration to multi-tenant structure...")
            
            # Get or create default company
            result = await db.execute(
                text("SELECT id FROM companies WHERE subdomain = 'default'")
            )
            company_row = result.fetchone()
            
            if not company_row:
                print("❌ Default company not found. Run seed_multitenant_data.py first.")
                return
            
            default_company_id = company_row.id
            print(f"📋 Using default company ID: {default_company_id}")
            
            # Tables to update with company_id
            tables_to_update = [
                "users",
                "properties", 
                "leases",
                "payments",
                "maintenance_requests",
                "message_threads",
                "messages",
                "applications"
            ]
            
            # Update each table
            total_updated = 0
            for table in tables_to_update:
                try:
                    # Check if company_id column exists and has NULL values
                    result = await db.execute(
                        text(f"""
                            SELECT COUNT(*) as count 
                            FROM {table} 
                            WHERE company_id IS NULL
                        """)
                    )
                    null_count = result.fetchone().count
                    
                    if null_count == 0:
                        print(f"✅ {table}: No records to update")
                        continue
                    
                    # Update NULL company_id values to default company
                    result = await db.execute(
                        text(f"""
                            UPDATE {table} 
                            SET company_id = :company_id 
                            WHERE company_id IS NULL
                        """),
                        {"company_id": default_company_id}
                    )
                    
                    updated_count = result.rowcount
                    total_updated += updated_count
                    print(f"✅ {table}: Updated {updated_count} records")
                    
                except Exception as e:
                    print(f"⚠️  {table}: {e}")
                    continue
            
            # Special handling for users - update platform admin
            try:
                # Check if there's an admin user that should be platform admin
                result = await db.execute(
                    text("""
                        SELECT id, email, role 
                        FROM users 
                        WHERE email = 'admin@greenpm.com' OR role = 'ADMIN'
                        LIMIT 1
                    """)
                )
                admin_user = result.fetchone()
                
                if admin_user:
                    # Make this user a platform admin (no company association)
                    await db.execute(
                        text("""
                            UPDATE users 
                            SET role = 'PLATFORM_ADMIN', company_id = NULL
                            WHERE id = :user_id
                        """),
                        {"user_id": admin_user.id}
                    )
                    print(f"✅ Updated {admin_user.email} to PLATFORM_ADMIN")
                
            except Exception as e:
                print(f"⚠️  Error updating platform admin: {e}")
            
            # Create default plan assignment for the default company
            try:
                # Get the Starter plan
                result = await db.execute(
                    text("SELECT id FROM plans WHERE name = 'Starter' LIMIT 1")
                )
                starter_plan = result.fetchone()
                
                if starter_plan:
                    # Check if plan assignment already exists
                    result = await db.execute(
                        text("""
                            SELECT id FROM plan_assignments 
                            WHERE company_id = :company_id AND active = true
                        """),
                        {"company_id": default_company_id}
                    )
                    existing_assignment = result.fetchone()
                    
                    if not existing_assignment:
                        # Create plan assignment
                        await db.execute(
                            text("""
                                INSERT INTO plan_assignments (
                                    company_id, plan_id, start_at, active, 
                                    billing_cycle_start, next_billing_date, created_at
                                ) VALUES (
                                    :company_id, :plan_id, NOW(), true,
                                    NOW(), NOW() + INTERVAL '1 month', NOW()
                                )
                            """),
                            {
                                "company_id": default_company_id,
                                "plan_id": starter_plan.id
                            }
                        )
                        print(f"✅ Assigned Starter plan to default company")
                    else:
                        print(f"📋 Plan assignment already exists for default company")
                
            except Exception as e:
                print(f"⚠️  Error creating plan assignment: {e}")
            
            # Create default feature flags for the default company
            try:
                # Get Starter plan features
                result = await db.execute(
                    text("""
                        SELECT pf.module_key, pf.enabled, pf.default_config
                        FROM plan_features pf
                        JOIN plans p ON p.id = pf.plan_id
                        WHERE p.name = 'Starter'
                    """)
                )
                plan_features = result.fetchall()
                
                if plan_features:
                    # Check if feature flags already exist
                    result = await db.execute(
                        text("""
                            SELECT COUNT(*) as count 
                            FROM feature_flags 
                            WHERE company_id = :company_id
                        """),
                        {"company_id": default_company_id}
                    )
                    existing_flags = result.fetchone().count
                    
                    if existing_flags == 0:
                        # Create feature flags based on plan
                        for feature in plan_features:
                            await db.execute(
                                text("""
                                    INSERT INTO feature_flags (
                                        company_id, module_key, enabled, config, created_at
                                    ) VALUES (
                                        :company_id, :module_key, :enabled, :config, NOW()
                                    )
                                """),
                                {
                                    "company_id": default_company_id,
                                    "module_key": feature.module_key,
                                    "enabled": feature.enabled,
                                    "config": json.dumps(feature.default_config) if feature.default_config else '{}'
                                }
                            )
                        
                        print(f"✅ Created {len(plan_features)} feature flags for default company")
                    else:
                        print(f"📋 Feature flags already exist for default company ({existing_flags} flags)")
                
            except Exception as e:
                print(f"⚠️  Error creating feature flags: {e}")
            
            await db.commit()
            print(f"✅ Migration completed! Updated {total_updated} total records")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Migration failed: {e}")
            raise

async def verify_migration():
    """Verify the migration was successful"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    async with AsyncSessionLocal() as db:
        try:
            print("\n🔍 Verifying migration...")
            
            # Check company data
            result = await db.execute(
                text("SELECT COUNT(*) as count FROM companies")
            )
            company_count = result.fetchone().count
            print(f"📊 Companies: {company_count}")
            
            # Check plan assignments
            result = await db.execute(
                text("SELECT COUNT(*) as count FROM plan_assignments WHERE active = true")
            )
            assignment_count = result.fetchone().count
            print(f"📊 Active plan assignments: {assignment_count}")
            
            # Check feature flags
            result = await db.execute(
                text("SELECT COUNT(*) as count FROM feature_flags")
            )
            flag_count = result.fetchone().count
            print(f"📊 Feature flags: {flag_count}")
            
            # Check users with company_id
            result = await db.execute(
                text("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(company_id) as with_company,
                        COUNT(CASE WHEN role = 'PLATFORM_ADMIN' THEN 1 END) as platform_admins
                    FROM users
                """)
            )
            user_stats = result.fetchone()
            print(f"📊 Users: {user_stats.total} total, {user_stats.with_company} with company, {user_stats.platform_admins} platform admins")
            
            # Check for any NULL company_id values in main tables
            tables_to_check = ["properties", "leases", "payments", "maintenance_requests"]
            for table in tables_to_check:
                try:
                    result = await db.execute(
                        text(f"SELECT COUNT(*) as count FROM {table} WHERE company_id IS NULL")
                    )
                    null_count = result.fetchone().count
                    if null_count > 0:
                        print(f"⚠️  {table}: {null_count} records with NULL company_id")
                    else:
                        print(f"✅ {table}: All records have company_id")
                except:
                    print(f"⚠️  {table}: Could not verify (table may not exist yet)")
            
            print("✅ Migration verification completed")
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")

async def main():
    """Run migration and verification"""
    try:
        await migrate_existing_data()
        await verify_migration()
        return 0
    except Exception as e:
        print(f"❌ Migration process failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
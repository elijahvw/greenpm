#!/usr/bin/env python3
"""
Seed default multi-tenant data (plans, features, etc.)
"""
import asyncio
import json
import sys
sys.path.append('.')

from sqlalchemy import text
from src.core.database import AsyncSessionLocal
from src.models.plan import Plan, PlanStatus, BillingType
from src.models.feature_flag import PlanFeature, ModuleKey

async def seed_default_plans():
    """Create default subscription plans"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if plans already exist
            result = await db.execute(text("SELECT COUNT(*) as count FROM plans"))
            count = result.fetchone().count
            
            if count > 0:
                print(f"📋 Plans already exist ({count} plans found)")
                return
            
            # Create default plans
            plans_data = [
                {
                    "name": "Starter",
                    "description": "Perfect for small landlords with up to 10 properties",
                    "billing_type": BillingType.FLAT_MONTHLY,
                    "base_price": 29.00,
                    "max_properties": 10,
                    "max_users": 3,
                    "max_storage_gb": 5,
                    "max_api_calls_per_month": 1000,
                    "display_order": 1,
                    "is_popular": False
                },
                {
                    "name": "Growth",
                    "description": "Great for growing property management companies",
                    "billing_type": BillingType.PER_PROPERTY,
                    "base_price": 49.00,
                    "per_unit_price": 2.50,
                    "max_properties": 100,
                    "max_users": 10,
                    "max_storage_gb": 50,
                    "max_api_calls_per_month": 10000,
                    "display_order": 2,
                    "is_popular": True
                },
                {
                    "name": "Professional",
                    "description": "Advanced features for established property managers",
                    "billing_type": BillingType.PER_PROPERTY,
                    "base_price": 99.00,
                    "per_unit_price": 1.50,
                    "max_properties": 500,
                    "max_users": 25,
                    "max_storage_gb": 200,
                    "max_api_calls_per_month": 50000,
                    "display_order": 3,
                    "is_popular": False
                },
                {
                    "name": "Enterprise",
                    "description": "Unlimited everything for large property management companies",
                    "billing_type": BillingType.CUSTOM,
                    "base_price": 299.00,
                    "max_properties": 0,  # Unlimited
                    "max_users": 0,  # Unlimited
                    "max_storage_gb": 0,  # Unlimited
                    "max_api_calls_per_month": 0,  # Unlimited
                    "display_order": 4,
                    "is_popular": False
                }
            ]
            
            plan_ids = {}
            for plan_data in plans_data:
                result = await db.execute(
                    text("""
                        INSERT INTO plans (
                            name, description, billing_type, base_price, per_unit_price,
                            max_properties, max_users, max_storage_gb, max_api_calls_per_month,
                            display_order, is_popular, status, created_at
                        ) VALUES (
                            :name, :description, :billing_type, :base_price, :per_unit_price,
                            :max_properties, :max_users, :max_storage_gb, :max_api_calls_per_month,
                            :display_order, :is_popular, :status, NOW()
                        ) RETURNING id
                    """),
                    {
                        **plan_data,
                        "per_unit_price": plan_data.get("per_unit_price", 0),
                        "status": PlanStatus.ACTIVE
                    }
                )
                plan_id = result.fetchone().id
                plan_ids[plan_data["name"]] = plan_id
                print(f"✅ Created plan: {plan_data['name']} (ID: {plan_id})")
            
            await db.commit()
            print(f"✅ Created {len(plans_data)} default plans")
            return plan_ids
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating plans: {e}")
            raise

async def seed_plan_features():
    """Create default plan features"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    async with AsyncSessionLocal() as db:
        try:
            # Get plan IDs
            result = await db.execute(
                text("SELECT id, name FROM plans ORDER BY display_order")
            )
            plans = {row.name: row.id for row in result.fetchall()}
            
            if not plans:
                print("❌ No plans found. Run seed_default_plans() first.")
                return
            
            # Define features per plan
            plan_features = {
                "Starter": [
                    (ModuleKey.PROPERTY_MANAGEMENT, True, {}),
                    (ModuleKey.TENANT_MANAGEMENT, True, {}),
                    (ModuleKey.LEASE_MANAGEMENT, True, {}),
                    (ModuleKey.PAYMENTS, True, {"max_payment_methods": 2}),
                    (ModuleKey.MAINTENANCE_REQUESTS, True, {}),
                    (ModuleKey.MESSAGING, True, {"max_messages_per_month": 500}),
                    (ModuleKey.FILE_UPLOADS, True, {"max_file_size_mb": 10}),
                    (ModuleKey.MULTI_USER, True, {}),
                    # Disabled features
                    (ModuleKey.INSPECTIONS, False, {}),
                    (ModuleKey.ACCOUNTING, False, {}),
                    (ModuleKey.TENANT_PORTAL, False, {}),
                    (ModuleKey.REPORTING, False, {}),
                    (ModuleKey.ANALYTICS, False, {}),
                    (ModuleKey.API_ACCESS, False, {}),
                    (ModuleKey.WEBHOOKS, False, {}),
                ],
                "Growth": [
                    (ModuleKey.PROPERTY_MANAGEMENT, True, {}),
                    (ModuleKey.TENANT_MANAGEMENT, True, {}),
                    (ModuleKey.LEASE_MANAGEMENT, True, {}),
                    (ModuleKey.PAYMENTS, True, {"max_payment_methods": 5}),
                    (ModuleKey.MAINTENANCE_REQUESTS, True, {}),
                    (ModuleKey.INSPECTIONS, True, {}),
                    (ModuleKey.MESSAGING, True, {"max_messages_per_month": 2000}),
                    (ModuleKey.TENANT_PORTAL, True, {}),
                    (ModuleKey.NOTIFICATIONS, True, {}),
                    (ModuleKey.FILE_UPLOADS, True, {"max_file_size_mb": 25}),
                    (ModuleKey.MULTI_USER, True, {}),
                    (ModuleKey.ROLE_MANAGEMENT, True, {}),
                    (ModuleKey.REPORTING, True, {"max_reports_per_month": 50}),
                    # Disabled features
                    (ModuleKey.ACCOUNTING, False, {}),
                    (ModuleKey.ANALYTICS, False, {}),
                    (ModuleKey.API_ACCESS, False, {}),
                    (ModuleKey.WEBHOOKS, False, {}),
                ],
                "Professional": [
                    (ModuleKey.PROPERTY_MANAGEMENT, True, {}),
                    (ModuleKey.TENANT_MANAGEMENT, True, {}),
                    (ModuleKey.LEASE_MANAGEMENT, True, {}),
                    (ModuleKey.PAYMENTS, True, {}),
                    (ModuleKey.MAINTENANCE_REQUESTS, True, {}),
                    (ModuleKey.INSPECTIONS, True, {}),
                    (ModuleKey.ACCOUNTING, True, {}),
                    (ModuleKey.MESSAGING, True, {}),
                    (ModuleKey.TENANT_PORTAL, True, {}),
                    (ModuleKey.NOTIFICATIONS, True, {}),
                    (ModuleKey.REPORTING, True, {}),
                    (ModuleKey.ANALYTICS, True, {}),
                    (ModuleKey.FILE_UPLOADS, True, {"max_file_size_mb": 100}),
                    (ModuleKey.DOCUMENT_STORAGE, True, {}),
                    (ModuleKey.MULTI_USER, True, {}),
                    (ModuleKey.ROLE_MANAGEMENT, True, {}),
                    (ModuleKey.AUDIT_LOGS, True, {}),
                    (ModuleKey.API_ACCESS, True, {"max_api_calls_per_month": 50000}),
                    # Disabled features
                    (ModuleKey.WEBHOOKS, False, {}),
                    (ModuleKey.MOBILE_APP, False, {}),
                ],
                "Enterprise": [
                    # All features enabled
                    (ModuleKey.PROPERTY_MANAGEMENT, True, {}),
                    (ModuleKey.TENANT_MANAGEMENT, True, {}),
                    (ModuleKey.LEASE_MANAGEMENT, True, {}),
                    (ModuleKey.PAYMENTS, True, {}),
                    (ModuleKey.MAINTENANCE_REQUESTS, True, {}),
                    (ModuleKey.INSPECTIONS, True, {}),
                    (ModuleKey.ACCOUNTING, True, {}),
                    (ModuleKey.MESSAGING, True, {}),
                    (ModuleKey.TENANT_PORTAL, True, {}),
                    (ModuleKey.NOTIFICATIONS, True, {}),
                    (ModuleKey.REPORTING, True, {}),
                    (ModuleKey.ANALYTICS, True, {}),
                    (ModuleKey.FILE_UPLOADS, True, {}),
                    (ModuleKey.DOCUMENT_STORAGE, True, {}),
                    (ModuleKey.MULTI_USER, True, {}),
                    (ModuleKey.ROLE_MANAGEMENT, True, {}),
                    (ModuleKey.AUDIT_LOGS, True, {}),
                    (ModuleKey.API_ACCESS, True, {}),
                    (ModuleKey.WEBHOOKS, True, {}),
                    (ModuleKey.MOBILE_APP, True, {}),
                    (ModuleKey.STRIPE_INTEGRATION, True, {}),
                    (ModuleKey.TWILIO_INTEGRATION, True, {}),
                    (ModuleKey.SENDGRID_INTEGRATION, True, {}),
                ]
            }
            
            # Insert plan features
            total_features = 0
            for plan_name, features in plan_features.items():
                plan_id = plans.get(plan_name)
                if not plan_id:
                    continue
                
                for module_key, enabled, config in features:
                    await db.execute(
                        text("""
                            INSERT INTO plan_features (
                                plan_id, module_key, enabled, default_config, created_at
                            ) VALUES (
                                :plan_id, :module_key, :enabled, :default_config, NOW()
                            )
                        """),
                        {
                            "plan_id": plan_id,
                            "module_key": module_key,
                            "enabled": enabled,
                            "default_config": json.dumps(config) if config else '{}'
                        }
                    )
                    total_features += 1
                
                print(f"✅ Created {len(features)} features for {plan_name} plan")
            
            await db.commit()
            print(f"✅ Created {total_features} total plan features")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating plan features: {e}")
            raise

async def create_default_company():
    """Create a default company for existing data migration"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if default company exists
            result = await db.execute(
                text("SELECT id FROM companies WHERE subdomain = 'default'")
            )
            existing = result.fetchone()
            
            if existing:
                print(f"📋 Default company already exists (ID: {existing.id})")
                return existing.id
            
            # Create default company
            result = await db.execute(
                text("""
                    INSERT INTO companies (
                        name, subdomain, status, email, timezone, currency,
                        max_properties, max_users, max_storage_gb, max_api_calls_per_month,
                        created_at
                    ) VALUES (
                        'Default Company', 'default', 'ACTIVE', 'admin@greenpm.com', 'UTC', 'USD',
                        1000, 100, 100, 100000, NOW()
                    ) RETURNING id
                """)
            )
            company_id = result.fetchone().id
            
            await db.commit()
            print(f"✅ Created default company (ID: {company_id})")
            return company_id
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating default company: {e}")
            raise

async def main():
    """Run all seeding operations"""
    print("🌱 Seeding multi-tenant data...")
    
    try:
        # Create default company first
        await create_default_company()
        
        # Create default plans
        await seed_default_plans()
        
        # Create plan features
        await seed_plan_features()
        
        print("✅ Multi-tenant data seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
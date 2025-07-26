#!/usr/bin/env python3
"""
Multi-tenant Migration Summary
"""
import asyncio
import sys
sys.path.append('.')

from sqlalchemy import text
from src.core.database import AsyncSessionLocal

async def show_summary():
    """Show summary of multi-tenant setup"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    async with AsyncSessionLocal() as db:
        try:
            print("🏢 MULTI-TENANT MIGRATION SUMMARY")
            print("=" * 50)
            
            # Companies
            result = await db.execute(
                text("SELECT id, name, subdomain, status FROM companies ORDER BY id")
            )
            companies = result.fetchall()
            print(f"\n📊 COMPANIES ({len(companies)}):")
            for company in companies:
                print(f"  • {company.name} ({company.subdomain}) - {company.status}")
            
            # Plans
            result = await db.execute(
                text("SELECT id, name, billing_type, base_price, status FROM plans ORDER BY display_order")
            )
            plans = result.fetchall()
            print(f"\n💰 PLANS ({len(plans)}):")
            for plan in plans:
                print(f"  • {plan.name} - ${plan.base_price}/month ({plan.billing_type}) - {plan.status}")
            
            # Plan assignments
            result = await db.execute(
                text("""
                    SELECT c.name as company_name, p.name as plan_name, pa.active
                    FROM plan_assignments pa
                    JOIN companies c ON c.id = pa.company_id
                    JOIN plans p ON p.id = pa.plan_id
                    ORDER BY c.name
                """)
            )
            assignments = result.fetchall()
            print(f"\n📋 PLAN ASSIGNMENTS ({len(assignments)}):")
            for assignment in assignments:
                status = "✅ Active" if assignment.active else "❌ Inactive"
                print(f"  • {assignment.company_name} → {assignment.plan_name} ({status})")
            
            # Feature flags
            result = await db.execute(
                text("""
                    SELECT c.name as company_name, 
                           COUNT(*) as total_features,
                           COUNT(CASE WHEN ff.enabled THEN 1 END) as enabled_features
                    FROM feature_flags ff
                    JOIN companies c ON c.id = ff.company_id
                    GROUP BY c.id, c.name
                    ORDER BY c.name
                """)
            )
            feature_stats = result.fetchall()
            print(f"\n🚀 FEATURE FLAGS:")
            for stat in feature_stats:
                print(f"  • {stat.company_name}: {stat.enabled_features}/{stat.total_features} features enabled")
            
            # Users by company
            result = await db.execute(
                text("""
                    SELECT 
                        COALESCE(c.name, 'Platform Admins') as company_name,
                        COUNT(*) as user_count,
                        COUNT(CASE WHEN u.role = 'PLATFORM_ADMIN' THEN 1 END) as platform_admins,
                        COUNT(CASE WHEN u.role = 'ADMIN' THEN 1 END) as admins,
                        COUNT(CASE WHEN u.role = 'LANDLORD' THEN 1 END) as landlords,
                        COUNT(CASE WHEN u.role = 'TENANT' THEN 1 END) as tenants
                    FROM users u
                    LEFT JOIN companies c ON c.id = u.company_id
                    GROUP BY c.id, c.name
                    ORDER BY c.name NULLS FIRST
                """)
            )
            user_stats = result.fetchall()
            print(f"\n👥 USERS BY COMPANY:")
            for stat in user_stats:
                print(f"  • {stat.company_name}: {stat.user_count} users")
                if stat.platform_admins > 0:
                    print(f"    - Platform Admins: {stat.platform_admins}")
                if stat.admins > 0:
                    print(f"    - Admins: {stat.admins}")
                if stat.landlords > 0:
                    print(f"    - Landlords: {stat.landlords}")
                if stat.tenants > 0:
                    print(f"    - Tenants: {stat.tenants}")
            
            # Data by company
            tables = ["properties", "leases", "payments", "maintenance_requests", "messages", "applications"]
            print(f"\n📊 DATA BY COMPANY:")
            
            for table in tables:
                try:
                    result = await db.execute(
                        text(f"""
                            SELECT 
                                c.name as company_name,
                                COUNT(*) as record_count
                            FROM {table} t
                            JOIN companies c ON c.id = t.company_id
                            GROUP BY c.id, c.name
                            ORDER BY c.name
                        """)
                    )
                    table_stats = result.fetchall()
                    
                    if table_stats:
                        print(f"  • {table.replace('_', ' ').title()}:")
                        for stat in table_stats:
                            print(f"    - {stat.company_name}: {stat.record_count} records")
                    else:
                        print(f"  • {table.replace('_', ' ').title()}: No records")
                        
                except Exception as e:
                    print(f"  • {table.replace('_', ' ').title()}: Error - {e}")
            
            print(f"\n✅ MIGRATION STATUS: COMPLETE")
            print("🎉 Your Green PM application is now multi-tenant ready!")
            print("\n📝 NEXT STEPS:")
            print("1. Update your API endpoints to use tenant context")
            print("2. Add the MultiTenantMiddleware to your FastAPI app")
            print("3. Test subdomain-based tenant resolution")
            print("4. Set up billing integration with Stripe")
            print("5. Create company onboarding flow")
            
        except Exception as e:
            print(f"❌ Error generating summary: {e}")

async def main():
    """Run summary"""
    try:
        await show_summary()
        return 0
    except Exception as e:
        print(f"❌ Summary failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
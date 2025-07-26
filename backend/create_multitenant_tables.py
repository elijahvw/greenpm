#!/usr/bin/env python3
"""
Create multi-tenant tables manually
"""
import asyncio
import sys
sys.path.append('.')

from sqlalchemy import text
from src.core.database import AsyncSessionLocal

async def create_multitenant_tables():
    """Create all multi-tenant tables"""
    if not AsyncSessionLocal:
        print("❌ Database not configured")
        return
    
    async with AsyncSessionLocal() as db:
        try:
            print("🔄 Creating multi-tenant tables...")
            
            # 1. Create companies table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT gen_random_uuid()::text,
                    name VARCHAR(255) NOT NULL,
                    subdomain VARCHAR(100) UNIQUE NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'TRIAL',
                    email VARCHAR(255) NOT NULL,
                    phone VARCHAR(20),
                    website VARCHAR(255),
                    address_line1 VARCHAR(255),
                    address_line2 VARCHAR(255),
                    city VARCHAR(100),
                    state VARCHAR(50),
                    zip_code VARCHAR(20),
                    country VARCHAR(50) DEFAULT 'US',
                    logo_url VARCHAR(500),
                    primary_color VARCHAR(7),
                    secondary_color VARCHAR(7),
                    custom_css TEXT,
                    timezone VARCHAR(50) DEFAULT 'UTC',
                    currency VARCHAR(3) DEFAULT 'USD',
                    date_format VARCHAR(20) DEFAULT 'MM/DD/YYYY',
                    language VARCHAR(5) DEFAULT 'en',
                    max_properties INTEGER DEFAULT 10,
                    max_users INTEGER DEFAULT 5,
                    max_storage_gb INTEGER DEFAULT 1,
                    max_api_calls_per_month INTEGER DEFAULT 1000,
                    current_properties INTEGER DEFAULT 0,
                    current_users INTEGER DEFAULT 0,
                    current_storage_gb INTEGER DEFAULT 0,
                    current_api_calls_this_month INTEGER DEFAULT 0,
                    suspended_at TIMESTAMP WITH TIME ZONE,
                    suspended_reason VARCHAR(500),
                    suspended_by VARCHAR(255),
                    internal_notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            print("✅ Created companies table")
            
            # 2. Create plans table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS plans (
                    id SERIAL PRIMARY KEY,
                    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT gen_random_uuid()::text,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
                    billing_type VARCHAR(20) NOT NULL,
                    base_price DECIMAL(10,2) NOT NULL,
                    per_unit_price DECIMAL(10,2) DEFAULT 0,
                    setup_fee DECIMAL(10,2) DEFAULT 0,
                    max_properties INTEGER DEFAULT 0,
                    max_users INTEGER DEFAULT 0,
                    max_storage_gb INTEGER DEFAULT 0,
                    max_api_calls_per_month INTEGER DEFAULT 0,
                    features JSONB DEFAULT '{}',
                    overage_property_price DECIMAL(10,2) DEFAULT 0,
                    overage_user_price DECIMAL(10,2) DEFAULT 0,
                    overage_storage_price_per_gb DECIMAL(10,2) DEFAULT 0,
                    overage_api_price_per_1000 DECIMAL(10,2) DEFAULT 0,
                    display_order INTEGER DEFAULT 0,
                    is_popular BOOLEAN DEFAULT FALSE,
                    is_custom BOOLEAN DEFAULT FALSE,
                    stripe_price_id VARCHAR(255),
                    stripe_product_id VARCHAR(255),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            print("✅ Created plans table")
            
            # 3. Create plan_assignments table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS plan_assignments (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER NOT NULL REFERENCES companies(id),
                    plan_id INTEGER NOT NULL REFERENCES plans(id),
                    start_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    end_at TIMESTAMP WITH TIME ZONE,
                    active BOOLEAN DEFAULT TRUE,
                    custom_base_price DECIMAL(10,2),
                    custom_per_unit_price DECIMAL(10,2),
                    custom_limits JSONB DEFAULT '{}',
                    billing_cycle_start TIMESTAMP WITH TIME ZONE,
                    next_billing_date TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            print("✅ Created plan_assignments table")
            
            # 4. Create feature_flags table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS feature_flags (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER NOT NULL REFERENCES companies(id),
                    module_key VARCHAR(50) NOT NULL,
                    enabled BOOLEAN NOT NULL DEFAULT FALSE,
                    config JSONB DEFAULT '{}',
                    usage_limit INTEGER,
                    current_usage INTEGER DEFAULT 0,
                    override_reason VARCHAR(500),
                    override_by VARCHAR(255),
                    override_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            print("✅ Created feature_flags table")
            
            # 5. Create plan_features table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS plan_features (
                    id SERIAL PRIMARY KEY,
                    plan_id INTEGER NOT NULL REFERENCES plans(id),
                    module_key VARCHAR(50) NOT NULL,
                    enabled BOOLEAN NOT NULL DEFAULT FALSE,
                    default_config JSONB DEFAULT '{}',
                    default_usage_limit INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            print("✅ Created plan_features table")
            
            # 6. Create contracts table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS contracts (
                    id SERIAL PRIMARY KEY,
                    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT gen_random_uuid()::text,
                    company_id INTEGER NOT NULL REFERENCES companies(id),
                    contract_number VARCHAR(100) UNIQUE NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
                    start_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    end_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    renewal_type VARCHAR(20) NOT NULL DEFAULT 'MANUAL',
                    auto_renewal_notice_days INTEGER DEFAULT 30,
                    billing_cycle VARCHAR(20) NOT NULL DEFAULT 'MONTHLY',
                    currency VARCHAR(3) DEFAULT 'USD',
                    payment_terms_days INTEGER DEFAULT 30,
                    payment_method VARCHAR(50),
                    stripe_customer_id VARCHAR(255),
                    stripe_subscription_id VARCHAR(255),
                    terms_json JSONB DEFAULT '{}',
                    base_amount DECIMAL(10,2) NOT NULL,
                    setup_fee DECIMAL(10,2) DEFAULT 0,
                    discount_percent DECIMAL(5,2) DEFAULT 0,
                    discount_amount DECIMAL(10,2) DEFAULT 0,
                    signed_at TIMESTAMP WITH TIME ZONE,
                    signed_by_name VARCHAR(255),
                    signed_by_email VARCHAR(255),
                    signed_by_ip VARCHAR(45),
                    contract_pdf_url VARCHAR(500),
                    cancelled_at TIMESTAMP WITH TIME ZONE,
                    cancelled_by VARCHAR(255),
                    cancellation_reason TEXT,
                    internal_notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            print("✅ Created contracts table")
            
            # 7. Create invoices table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id SERIAL PRIMARY KEY,
                    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT gen_random_uuid()::text,
                    contract_id INTEGER NOT NULL REFERENCES contracts(id),
                    invoice_number VARCHAR(100) UNIQUE NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
                    subtotal DECIMAL(10,2) NOT NULL,
                    tax_amount DECIMAL(10,2) DEFAULT 0,
                    discount_amount DECIMAL(10,2) DEFAULT 0,
                    total_amount DECIMAL(10,2) NOT NULL,
                    currency VARCHAR(3) DEFAULT 'USD',
                    issued_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    due_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    paid_at TIMESTAMP WITH TIME ZONE,
                    period_start TIMESTAMP WITH TIME ZONE,
                    period_end TIMESTAMP WITH TIME ZONE,
                    line_items JSONB DEFAULT '[]',
                    payment_method VARCHAR(50),
                    payment_reference VARCHAR(255),
                    stripe_invoice_id VARCHAR(255) UNIQUE,
                    stripe_payment_intent_id VARCHAR(255),
                    pdf_url VARCHAR(500),
                    internal_notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            print("✅ Created invoices table")
            
            # 8. Add company_id to existing tables
            tables_to_update = [
                ("users", "ALTER TABLE users ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES companies(id)"),
                ("properties", "ALTER TABLE properties ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES companies(id)"),
                ("leases", "ALTER TABLE leases ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES companies(id)"),
                ("payments", "ALTER TABLE payments ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES companies(id)"),
                ("maintenance_requests", "ALTER TABLE maintenance_requests ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES companies(id)"),
                ("message_threads", "ALTER TABLE message_threads ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES companies(id)"),
                ("messages", "ALTER TABLE messages ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES companies(id)"),
                ("applications", "ALTER TABLE applications ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES companies(id)")
            ]
            
            for table_name, sql in tables_to_update:
                try:
                    await db.execute(text(sql))
                    print(f"✅ Added company_id to {table_name}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"📋 company_id already exists in {table_name}")
                    else:
                        print(f"⚠️  Error updating {table_name}: {e}")
            
            # 9. Update audit_logs table for multi-tenant support
            try:
                await db.execute(text("""
                    ALTER TABLE audit_logs 
                    ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES companies(id),
                    ADD COLUMN IF NOT EXISTS actor_email VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS actor_role VARCHAR(50),
                    ADD COLUMN IF NOT EXISTS impersonated_by_user_id INTEGER REFERENCES users(id),
                    ADD COLUMN IF NOT EXISTS is_impersonated_action BOOLEAN DEFAULT FALSE,
                    ADD COLUMN IF NOT EXISTS resource_name VARCHAR(255),
                    ADD COLUMN IF NOT EXISTS request_id VARCHAR(36),
                    ADD COLUMN IF NOT EXISTS severity VARCHAR(20) DEFAULT 'LOW',
                    ADD COLUMN IF NOT EXISTS category VARCHAR(50),
                    ADD COLUMN IF NOT EXISTS error_code VARCHAR(50),
                    ADD COLUMN IF NOT EXISTS retention_until TIMESTAMP WITH TIME ZONE,
                    ADD COLUMN IF NOT EXISTS is_sensitive BOOLEAN DEFAULT FALSE
                """))
                print("✅ Enhanced audit_logs table")
            except Exception as e:
                print(f"⚠️  Error enhancing audit_logs: {e}")
            
            # 10. Create indexes for performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_companies_subdomain ON companies(subdomain)",
                "CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(status)",
                "CREATE INDEX IF NOT EXISTS idx_plan_assignments_company ON plan_assignments(company_id)",
                "CREATE INDEX IF NOT EXISTS idx_plan_assignments_active ON plan_assignments(active)",
                "CREATE INDEX IF NOT EXISTS idx_feature_flags_company ON feature_flags(company_id)",
                "CREATE INDEX IF NOT EXISTS idx_feature_flags_module ON feature_flags(module_key)",
                "CREATE INDEX IF NOT EXISTS idx_feature_flags_enabled ON feature_flags(enabled)",
                "CREATE INDEX IF NOT EXISTS idx_users_company ON users(company_id)",
                "CREATE INDEX IF NOT EXISTS idx_properties_company ON properties(company_id)",
                "CREATE INDEX IF NOT EXISTS idx_leases_company ON leases(company_id)",
                "CREATE INDEX IF NOT EXISTS idx_payments_company ON payments(company_id)",
                "CREATE INDEX IF NOT EXISTS idx_maintenance_requests_company ON maintenance_requests(company_id)",
                "CREATE INDEX IF NOT EXISTS idx_messages_company ON messages(company_id)",
                "CREATE INDEX IF NOT EXISTS idx_applications_company ON applications(company_id)",
                "CREATE INDEX IF NOT EXISTS idx_audit_logs_company ON audit_logs(company_id)",
                "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action)",
                "CREATE INDEX IF NOT EXISTS idx_audit_logs_severity ON audit_logs(severity)"
            ]
            
            for index_sql in indexes:
                try:
                    await db.execute(text(index_sql))
                except Exception as e:
                    if "already exists" in str(e).lower():
                        continue
                    else:
                        print(f"⚠️  Error creating index: {e}")
            
            print("✅ Created performance indexes")
            
            await db.commit()
            print("✅ Multi-tenant tables created successfully!")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating tables: {e}")
            raise

async def main():
    """Run table creation"""
    try:
        await create_multitenant_tables()
        return 0
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
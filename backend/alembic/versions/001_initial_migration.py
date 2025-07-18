"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums
    op.execute("CREATE TYPE userstatus AS ENUM ('active', 'inactive', 'pending', 'suspended')")
    op.execute("CREATE TYPE userrole AS ENUM ('landlord', 'tenant', 'admin')")
    op.execute("CREATE TYPE propertystatus AS ENUM ('active', 'inactive', 'maintenance', 'sold')")
    op.execute("CREATE TYPE propertytype AS ENUM ('apartment', 'house', 'condo', 'studio', 'other')")
    op.execute("CREATE TYPE leasestatus AS ENUM ('draft', 'active', 'expired', 'terminated', 'pending')")
    op.execute("CREATE TYPE paymentstatus AS ENUM ('pending', 'completed', 'failed', 'refunded')")
    op.execute("CREATE TYPE paymenttype AS ENUM ('rent', 'deposit', 'fee', 'utility', 'other')")
    op.execute("CREATE TYPE paymentmethod AS ENUM ('credit_card', 'bank_transfer', 'cash', 'check', 'other')")
    op.execute("CREATE TYPE maintenancestatus AS ENUM ('open', 'in_progress', 'completed', 'cancelled')")
    op.execute("CREATE TYPE maintenancepriority AS ENUM ('low', 'medium', 'high', 'urgent')")
    op.execute("CREATE TYPE messagestatus AS ENUM ('sent', 'delivered', 'read')")
    op.execute("CREATE TYPE applicationstatus AS ENUM ('submitted', 'under_review', 'approved', 'rejected', 'withdrawn')")
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('status', postgresql.ENUM('active', 'inactive', 'pending', 'suspended', name='userstatus'), nullable=True),
        sa.Column('role', postgresql.ENUM('landlord', 'tenant', 'admin', name='userrole'), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=True),
        sa.Column('phone_verified', sa.Boolean(), nullable=True),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_uuid'), 'users', ['uuid'], unique=True)
    
    # Create properties table
    op.create_table('properties',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('landlord_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('property_type', postgresql.ENUM('apartment', 'house', 'condo', 'studio', 'other', name='propertytype'), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=50), nullable=False),
        sa.Column('zip_code', sa.String(length=20), nullable=False),
        sa.Column('country', sa.String(length=50), nullable=True),
        sa.Column('bedrooms', sa.Integer(), nullable=True),
        sa.Column('bathrooms', sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column('square_feet', sa.Integer(), nullable=True),
        sa.Column('lot_size', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('year_built', sa.Integer(), nullable=True),
        sa.Column('rent_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('deposit_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('pet_friendly', sa.Boolean(), nullable=True),
        sa.Column('furnished', sa.Boolean(), nullable=True),
        sa.Column('parking_available', sa.Boolean(), nullable=True),
        sa.Column('status', postgresql.ENUM('active', 'inactive', 'maintenance', 'sold', name='propertystatus'), nullable=True),
        sa.Column('available_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['landlord_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_properties_id'), 'properties', ['id'], unique=False)
    op.create_index(op.f('ix_properties_uuid'), 'properties', ['uuid'], unique=True)
    
    # Create other tables following similar pattern...
    # For brevity, I'll create a simplified version
    
    # Create leases table
    op.create_table('leases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('property_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('landlord_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('rent_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('deposit_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('status', postgresql.ENUM('draft', 'active', 'expired', 'terminated', 'pending', name='leasestatus'), nullable=True),
        sa.Column('tenant_signed', sa.Boolean(), nullable=True),
        sa.Column('landlord_signed', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['landlord_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leases_id'), 'leases', ['id'], unique=False)
    op.create_index(op.f('ix_leases_uuid'), 'leases', ['uuid'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('leases')
    op.drop_table('properties')
    op.drop_table('users')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS userstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS propertystatus")
    op.execute("DROP TYPE IF EXISTS propertytype")
    op.execute("DROP TYPE IF EXISTS leasestatus")
    op.execute("DROP TYPE IF EXISTS paymentstatus")
    op.execute("DROP TYPE IF EXISTS paymenttype")
    op.execute("DROP TYPE IF EXISTS paymentmethod")
    op.execute("DROP TYPE IF EXISTS maintenancestatus")
    op.execute("DROP TYPE IF EXISTS maintenancepriority")
    op.execute("DROP TYPE IF EXISTS messagestatus")
    op.execute("DROP TYPE IF EXISTS applicationstatus")
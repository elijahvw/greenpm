"""Add additional lease fields

Revision ID: 002_add_lease_fields
Revises: 001_initial_migration
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_lease_fields'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add additional lease fields
    op.add_column('leases', sa.Column('late_fee_penalty', sa.Numeric(precision=10, scale=2), nullable=True, server_default='0.00'))
    op.add_column('leases', sa.Column('grace_period_days', sa.Integer(), nullable=True, server_default='5'))
    op.add_column('leases', sa.Column('lease_type', sa.String(length=20), nullable=True, server_default='fixed'))
    op.add_column('leases', sa.Column('renewal_option', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('leases', sa.Column('pet_policy_allowed', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('leases', sa.Column('pet_policy_deposit', sa.Numeric(precision=10, scale=2), nullable=True, server_default='0.00'))
    op.add_column('leases', sa.Column('pet_policy_monthly_fee', sa.Numeric(precision=10, scale=2), nullable=True, server_default='0.00'))
    op.add_column('leases', sa.Column('pet_policy_restrictions', sa.Text(), nullable=True))
    op.add_column('leases', sa.Column('utilities_included', sa.JSON(), nullable=True))
    op.add_column('leases', sa.Column('tenant_responsibilities', sa.JSON(), nullable=True))
    op.add_column('leases', sa.Column('landlord_responsibilities', sa.JSON(), nullable=True))
    op.add_column('leases', sa.Column('special_terms', sa.Text(), nullable=True))
    op.add_column('leases', sa.Column('notes', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove additional lease fields
    op.drop_column('leases', 'notes')
    op.drop_column('leases', 'special_terms')
    op.drop_column('leases', 'landlord_responsibilities')
    op.drop_column('leases', 'tenant_responsibilities')
    op.drop_column('leases', 'utilities_included')
    op.drop_column('leases', 'pet_policy_restrictions')
    op.drop_column('leases', 'pet_policy_monthly_fee')
    op.drop_column('leases', 'pet_policy_deposit')
    op.drop_column('leases', 'pet_policy_allowed')
    op.drop_column('leases', 'renewal_option')
    op.drop_column('leases', 'lease_type')
    op.drop_column('leases', 'grace_period_days')
    op.drop_column('leases', 'late_fee_penalty')
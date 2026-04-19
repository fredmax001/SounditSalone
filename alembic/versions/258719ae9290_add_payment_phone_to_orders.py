"""add_payment_phone_to_orders

Revision ID: 258719ae9290
Revises: add_unique_constraints_001
Create Date: 2026-04-18 06:00:52.206851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '258719ae9290'
down_revision: Union[str, None] = 'add_unique_constraints_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add payment_phone column to orders table for Orange Money integration."""
    # Add payment_phone column (nullable, stores mobile money phone number)
    op.add_column('orders', sa.Column('payment_phone', sa.String(length=20), nullable=True))


def downgrade() -> None:
    """Remove payment_phone column from orders table."""
    op.drop_column('orders', 'payment_phone')

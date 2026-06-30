"""add_food_orders_and_reviews

Revision ID: 06e65ae09530
Revises: 8eef02a04421
Create Date: 2026-06-05 07:55:48.756717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '06e65ae09530'
down_revision: Union[str, None] = '8eef02a04421'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create food_orders table
    op.create_table('food_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('food_spot_id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(length=50), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('order_type', sa.String(length=20), nullable=True),
        sa.Column('delivery_address', sa.String(length=500), nullable=True),
        sa.Column('landmark', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'PREPARING', 'READY', 'DELIVERED', 'CANCELLED', name='foodorderstatus'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['food_spot_id'], ['food_spots.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number')
    )
    op.create_index(op.f('ix_food_orders_food_spot_id'), 'food_orders', ['food_spot_id'], unique=False)
    op.create_index(op.f('ix_food_orders_id'), 'food_orders', ['id'], unique=False)
    op.create_index(op.f('ix_food_orders_user_id'), 'food_orders', ['user_id'], unique=False)

    # Create reviews table
    op.create_table('reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('club_id', sa.Integer(), nullable=True),
        sa.Column('food_spot_id', sa.Integer(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['club_id'], ['clubs.id'], ),
        sa.ForeignKeyConstraint(['food_spot_id'], ['food_spots.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reviews_club_id'), 'reviews', ['club_id'], unique=False)
    op.create_index(op.f('ix_reviews_food_spot_id'), 'reviews', ['food_spot_id'], unique=False)
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], unique=False)
    op.create_index(op.f('ix_reviews_user_id'), 'reviews', ['user_id'], unique=False)

    # Create food_order_items table
    op.create_table('food_order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('menu_item_id', sa.String(length=100), nullable=True),
        sa.Column('menu_item_name', sa.String(length=200), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['food_orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_food_order_items_id'), 'food_order_items', ['id'], unique=False)
    op.create_index(op.f('ix_food_order_items_order_id'), 'food_order_items', ['order_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_food_order_items_order_id'), table_name='food_order_items')
    op.drop_index(op.f('ix_food_order_items_id'), table_name='food_order_items')
    op.drop_table('food_order_items')

    op.drop_index(op.f('ix_reviews_user_id'), table_name='reviews')
    op.drop_index(op.f('ix_reviews_id'), table_name='reviews')
    op.drop_index(op.f('ix_reviews_food_spot_id'), table_name='reviews')
    op.drop_index(op.f('ix_reviews_club_id'), table_name='reviews')
    op.drop_table('reviews')

    op.drop_index(op.f('ix_food_orders_user_id'), table_name='food_orders')
    op.drop_index(op.f('ix_food_orders_id'), table_name='food_orders')
    op.drop_index(op.f('ix_food_orders_food_spot_id'), table_name='food_orders')
    op.drop_table('food_orders')

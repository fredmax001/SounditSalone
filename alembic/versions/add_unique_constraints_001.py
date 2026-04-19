"""Add unique constraints to follow/like tables

Revision ID: add_unique_constraints_001
Revises: a10f3b388ca9
Create Date: 2026-04-08
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_unique_constraints_001'
down_revision = 'a10f3b388ca9'
branch_labels = None
depends_on = None


def upgrade():
    # Get database dialect
    conn = op.get_bind()
    dialect = conn.dialect.name
    
    # Add indexes to foreign keys for performance (works on all dialects)
    op.create_index('ix_bookings_venue_id', 'bookings', ['venue_id'])
    op.create_index('ix_sports_bookings_facility_id', 'sports_bookings', ['facility_id'])
    op.create_index('ix_sports_bookings_court_id', 'sports_bookings', ['court_id'])
    op.create_index('ix_venue_subscriptions_venue_id', 'venue_subscriptions', ['venue_id'])
    
    # Add indexes to event_follows foreign keys
    op.create_index('ix_event_follows_user_id', 'event_follows', ['user_id'])
    op.create_index('ix_event_follows_event_id', 'event_follows', ['event_id'])
    
    # SQLite doesn't support adding constraints via ALTER
    # For PostgreSQL/MySQL, we add unique constraints
    if dialect != 'sqlite':
        # Add unique constraints to prevent duplicate follows/likes
        
        # EventFollow - prevent duplicate event follows
        op.create_unique_constraint(
            'uq_event_follow_user_event', 
            'event_follows', 
            ['user_id', 'event_id']
        )
        
        # RecapLike - prevent duplicate likes
        op.create_unique_constraint(
            'uq_recap_like_user', 
            'recap_likes', 
            ['recap_id', 'user_id']
        )
        
        # VendorFollow - prevent duplicate vendor follows
        op.create_unique_constraint(
            'uq_vendor_follow_user', 
            'vendor_follows', 
            ['user_id', 'vendor_id']
        )
        
        # OrganizerFollow - prevent duplicate organizer follows  
        op.create_unique_constraint(
            'uq_organizer_follow_user', 
            'organizer_follows', 
            ['user_id', 'organizer_id']
        )
        
        # UserFavoriteTeam - prevent duplicate team favorites
        op.create_unique_constraint(
            'uq_user_favorite_team', 
            'user_favorite_teams', 
            ['user_id', 'team_id']
        )
    else:
        # For SQLite, we skip unique constraints in migration
        # They should be added in the model definition which SQLite will handle on create
        print("Skipping unique constraints for SQLite - add them via model definition or recreate tables")


def downgrade():
    # Get database dialect
    conn = op.get_bind()
    dialect = conn.dialect.name
    
    # Drop indexes
    op.drop_index('ix_bookings_venue_id', 'bookings')
    op.drop_index('ix_sports_bookings_facility_id', 'sports_bookings')
    op.drop_index('ix_sports_bookings_court_id', 'sports_bookings')
    op.drop_index('ix_venue_subscriptions_venue_id', 'venue_subscriptions')
    op.drop_index('ix_event_follows_user_id', 'event_follows')
    op.drop_index('ix_event_follows_event_id', 'event_follows')
    
    if dialect != 'sqlite':
        # Drop unique constraints
        op.drop_constraint('uq_event_follow_user_event', 'event_follows', type_='unique')
        op.drop_constraint('uq_recap_like_user', 'recap_likes', type_='unique')
        op.drop_constraint('uq_vendor_follow_user', 'vendor_follows', type_='unique')
        op.drop_constraint('uq_organizer_follow_user', 'organizer_follows', type_='unique')
        op.drop_constraint('uq_user_favorite_team', 'user_favorite_teams', type_='unique')

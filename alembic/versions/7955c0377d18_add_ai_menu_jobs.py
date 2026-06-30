"""add_ai_menu_jobs

Revision ID: 7955c0377d18
Revises: 06e65ae09530
Create Date: 2026-06-05 15:44:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7955c0377d18'
down_revision: Union[str, None] = '06e65ae09530'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('ai_menu_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('venue_profile_id', sa.Integer(), nullable=True),
        sa.Column('restaurant_profile_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='aimenustatus'), nullable=True),
        sa.Column('job_type', sa.String(length=50), nullable=True),
        sa.Column('original_filename', sa.String(length=255), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('raw_ocr_text', sa.Text(), nullable=True),
        sa.Column('structured_menu', sa.JSON(), nullable=True),
        sa.Column('ai_confidence_score', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('processing_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['restaurant_profile_id'], ['restaurant_profiles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['venue_profile_id'], ['venue_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_menu_jobs_id'), 'ai_menu_jobs', ['id'], unique=False)
    op.create_index(op.f('ix_ai_menu_jobs_restaurant_profile_id'), 'ai_menu_jobs', ['restaurant_profile_id'], unique=False)
    op.create_index(op.f('ix_ai_menu_jobs_user_id'), 'ai_menu_jobs', ['user_id'], unique=False)
    op.create_index(op.f('ix_ai_menu_jobs_venue_profile_id'), 'ai_menu_jobs', ['venue_profile_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ai_menu_jobs_venue_profile_id'), table_name='ai_menu_jobs')
    op.drop_index(op.f('ix_ai_menu_jobs_user_id'), table_name='ai_menu_jobs')
    op.drop_index(op.f('ix_ai_menu_jobs_restaurant_profile_id'), table_name='ai_menu_jobs')
    op.drop_index(op.f('ix_ai_menu_jobs_id'), table_name='ai_menu_jobs')
    op.drop_table('ai_menu_jobs')

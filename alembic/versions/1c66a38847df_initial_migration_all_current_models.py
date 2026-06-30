"""Initial migration - bootstrap all current models

Revision ID: 1c66a38847df
Revises: 
Create Date: 2026-03-26 18:39:58.650310

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '1c66a38847df'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables from the current SQLAlchemy model metadata.

    This bootstrap migration intentionally uses Base.metadata.create_all()
    because the project started without migrations. Future schema changes
    should use normal Alembic revision --autogenerate workflows.
    """
    # Import model modules to register all classes with Base.metadata
    import models  # noqa: F401
    import models_platform  # noqa: F401
    from database import Base

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    """Drop all tables created by this migration."""
    import models  # noqa: F401
    import models_platform  # noqa: F401
    from database import Base

    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)

"""adding feed_url to channel

Revision ID: 0277b62b5ddc
Revises: ace8be00714b
Create Date: 2026-04-25 10:43:33.426881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0277b62b5ddc'
down_revision: Union[str, Sequence[str], None] = 'ace8be00714b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE channel ADD COLUMN feed_url TEXT
    """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        ALTER TABLE channel DROP COLUMN feed_url
    """)
    pass

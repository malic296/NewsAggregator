"""adding channel logo url column

Revision ID: ace8be00714b
Revises: 3062b4f44e34
Create Date: 2026-04-25 09:59:42.751181

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ace8be00714b'
down_revision: Union[str, Sequence[str], None] = '3062b4f44e34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE channel ADD COLUMN logo_url TEXT NOT NULL
    """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        ALTER TABLE channel DROP COLUMN logo_url
   """)
    pass

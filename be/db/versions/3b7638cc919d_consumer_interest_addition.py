"""consumer_interest_addition

Revision ID: 3b7638cc919d
Revises: 1ed7b0be3777
Create Date: 2026-05-12 09:05:04.365596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b7638cc919d'
down_revision: Union[str, Sequence[str], None] = '1ed7b0be3777'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE consumer ADD COLUMN interest vector(384)
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        ALTER TABLE consumer DROP COLUMN interest
    """)

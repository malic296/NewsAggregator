"""coalesce index for channel

Revision ID: 1d2b8cd5a961
Revises: 0277b62b5ddc
Create Date: 2026-04-25 10:48:22.075237

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d2b8cd5a961'
down_revision: Union[str, Sequence[str], None] = '0277b62b5ddc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE UNIQUE INDEX idx_unique_channel_feed ON channel (COALESCE(feed_url, link));
    """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX idx_unique_channel_feed")
    pass

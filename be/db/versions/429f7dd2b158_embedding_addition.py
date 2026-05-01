"""embedding addition

Revision ID: 429f7dd2b158
Revises: ace8be00714b
Create Date: 2026-05-01 10:55:39.233678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '429f7dd2b158'
down_revision: Union[str, Sequence[str], None] = 'ace8be00714b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
    """)

    op.execute("""
        CREATE TABLE theme(id SERIAL PRIMARY KEY, uuid TEXT UNIQUE NOT NULL, newest_date TIMESTAMPTZ NOT NULL);
    """)

    op.execute("""
        ALTER TABLE article ADD COLUMN embedding vector(384), ADD COLUMN theme_id integer REFERENCES theme(id);
    """)

def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        ALTER TABLE article DROP COLUMN embedding, DROP COLUMN theme_id;
    """)

    op.execute("""
        DROP TABLE theme;
    """)

    op.execute("""
        DROP EXTENSION IF EXISTS vector;
    """)

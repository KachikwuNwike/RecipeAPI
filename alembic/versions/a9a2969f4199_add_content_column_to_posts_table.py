"""add content column to posts table

Revision ID: a9a2969f4199
Revises: 9cf625995e0a
Create Date: 2023-12-12 21:03:32.391116

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a9a2969f4199"
down_revision: Union[str, None] = "9cf625995e0a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column("posts", "content")
    pass

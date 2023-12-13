"""add phone number

Revision ID: 99305b4f23cd
Revises: 11546d894757
Create Date: 2023-12-12 21:39:25.276659

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99305b4f23cd'
down_revision: Union[str, None] = '11546d894757'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

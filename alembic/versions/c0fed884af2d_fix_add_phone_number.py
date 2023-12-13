"""fix add phone number

Revision ID: c0fed884af2d
Revises: 99305b4f23cd
Create Date: 2023-12-12 21:40:43.570952

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0fed884af2d'
down_revision: Union[str, None] = '99305b4f23cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

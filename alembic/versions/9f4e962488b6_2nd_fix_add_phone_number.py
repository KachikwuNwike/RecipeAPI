"""2nd fix add phone number

Revision ID: 9f4e962488b6
Revises: c0fed884af2d
Create Date: 2023-12-12 22:13:07.321573

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f4e962488b6'
down_revision: Union[str, None] = 'c0fed884af2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

"""Merging two alembic heads

Revision ID: f77be52db24e
Revises: 04da40f8060d
Create Date: 2025-03-11 06:58:38.633547

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f77be52db24e'
down_revision: Union[str, None] = '04da40f8060d'
branch_labels: Union[str, Sequence[str], None] = ('merge_04da_74a4',)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

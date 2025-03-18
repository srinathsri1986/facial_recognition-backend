"""Final Merge of Alembic Heads

Revision ID: be2d904fadde
Revises: f77be52db24e
Create Date: 2025-03-11 07:02:52.259247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be2d904fadde'
down_revision: Union[str, None] = 'f77be52db24e'
branch_labels: Union[str, Sequence[str], None] = ('final_merge_fix_1',)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

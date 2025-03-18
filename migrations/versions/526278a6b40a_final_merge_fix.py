"""Final Merge Fix

Revision ID: 526278a6b40a
Revises: ca98e0b50719
Create Date: 2025-03-11 07:17:34.159568

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '526278a6b40a'
down_revision: Union[str, None] = 'ca98e0b50719'
branch_labels: Union[str, Sequence[str], None] = ('final_merge_fixed',)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

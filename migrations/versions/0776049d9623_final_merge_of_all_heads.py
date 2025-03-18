"""Final Merge of All Heads

Revision ID: 0776049d9623
Revises: 74a45e98e554
Create Date: 2025-03-11 07:18:59.953742

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0776049d9623'
down_revision: Union[str, None] = '74a45e98e554'
branch_labels: Union[str, Sequence[str], None] = ('final_merge_all',)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

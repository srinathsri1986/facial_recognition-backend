"""Final Absolute Merge of Alembic Heads

Revision ID: ce80320a3c1b
Revises: ab692cc3e5ac
Create Date: 2025-03-11 07:23:56.804313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce80320a3c1b'
down_revision: Union[str, None] = 'ab692cc3e5ac'
branch_labels: Union[str, Sequence[str], None] = ('final_merge_absolute',)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

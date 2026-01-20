"""add_league_finished_at

Revision ID: 4a8b7c9d0e1f
Revises: 369fd3290e5a
Create Date: 2026-01-20 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4a8b7c9d0e1f"
down_revision: Union[str, None] = "369fd3290e5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("leagues", sa.Column("finished_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("leagues", "finished_at")

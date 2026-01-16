"""add current_knockout_round

Revision ID: a1b2c3d4e5f6
Revises: d135e2d41fb8
Create Date: 2026-01-16 16:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "278d90a8718e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "leagues",
        sa.Column("current_knockout_round", sa.String(20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("leagues", "current_knockout_round")

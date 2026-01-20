"""add_matchup_is_public

Revision ID: a7d82e4f9c31
Revises: 1870b61fe32b
Create Date: 2026-01-20 14:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a7d82e4f9c31"
down_revision: Union[str, None] = "1870b61fe32b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "matchups",
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="true"),
    )


def downgrade() -> None:
    op.drop_column("matchups", "is_public")

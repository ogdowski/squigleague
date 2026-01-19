"""add army_faction fields

Revision ID: 5049268fdcd4
Revises: 9aa13348795f
Create Date: 2026-01-19 11:37:39.985744

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5049268fdcd4"
down_revision: Union[str, None] = "9aa13348795f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "league_players", sa.Column("group_army_faction", sa.String(50), nullable=True)
    )
    op.add_column(
        "league_players",
        sa.Column("knockout_army_faction", sa.String(50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("league_players", "knockout_army_faction")
    op.drop_column("league_players", "group_army_faction")

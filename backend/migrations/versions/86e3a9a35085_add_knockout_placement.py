"""add knockout_placement

Revision ID: 86e3a9a35085
Revises: 5049268fdcd4
Create Date: 2026-01-19 13:12:35.925243

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "86e3a9a35085"
down_revision: Union[str, None] = "5049268fdcd4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "league_players", sa.Column("knockout_placement", sa.String(20), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("league_players", "knockout_placement")

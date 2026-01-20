"""add user discord and show_email

Revision ID: 2e9a9782c568
Revises: fb471ae52b7c
Create Date: 2026-01-19 14:08:34.133098

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2e9a9782c568"
down_revision: Union[str, None] = "fb471ae52b7c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("discord_username", sa.String(100), nullable=True))
    op.add_column(
        "users",
        sa.Column("show_email", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("users", "show_email")
    op.drop_column("users", "discord_username")

"""add_user_preferred_language

Revision ID: 1870b61fe32b
Revises: 4a8b7c9d0e1f
Create Date: 2026-01-20 09:42:28.794750

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1870b61fe32b"
down_revision: Union[str, None] = "4a8b7c9d0e1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "preferred_language", sa.String(5), nullable=False, server_default="en"
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "preferred_language")

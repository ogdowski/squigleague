"""add_user_avatar_url

Revision ID: 369fd3290e5a
Revises: 2e9a9782c568
Create Date: 2026-01-19 14:25:27.517324

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "369fd3290e5a"
down_revision: Union[str, None] = "2e9a9782c568"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("avatar_url", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "avatar_url")

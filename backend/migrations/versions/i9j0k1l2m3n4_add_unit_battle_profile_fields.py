"""Add unit battle profile fields

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-01-29

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "i9j0k1l2m3n4"
down_revision = "h8i9j0k1l2m3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "bsdata_units",
        sa.Column("base_size", sa.Text(), nullable=True),
    )
    op.add_column(
        "bsdata_units",
        sa.Column("unit_size", sa.Integer(), nullable=True),
    )
    op.add_column(
        "bsdata_units",
        sa.Column(
            "can_be_reinforced",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.add_column(
        "bsdata_units",
        sa.Column("notes", sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_column("bsdata_units", "notes")
    op.drop_column("bsdata_units", "can_be_reinforced")
    op.drop_column("bsdata_units", "unit_size")
    op.drop_column("bsdata_units", "base_size")

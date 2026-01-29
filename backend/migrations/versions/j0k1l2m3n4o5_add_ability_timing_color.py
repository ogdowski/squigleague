"""Add timing, declare, color to unit abilities

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2026-01-29

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "j0k1l2m3n4o5"
down_revision = "i9j0k1l2m3n4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "bsdata_unit_abilities",
        sa.Column("timing", sa.Text(), nullable=True),
    )
    op.add_column(
        "bsdata_unit_abilities",
        sa.Column("declare", sa.Text(), nullable=True),
    )
    op.add_column(
        "bsdata_unit_abilities",
        sa.Column("color", sa.String(30), nullable=True),
    )


def downgrade():
    op.drop_column("bsdata_unit_abilities", "color")
    op.drop_column("bsdata_unit_abilities", "declare")
    op.drop_column("bsdata_unit_abilities", "timing")

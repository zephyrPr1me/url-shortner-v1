"""initial_schema

Revision ID: cc6eeefbeaa1
Revises:
Create Date: 2026-06-14 22:47:07.264363

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cc6eeefbeaa1"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "urls",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("original_url", sa.String(), nullable=False, index=True),
        sa.Column("short_id", sa.String(), unique=True, nullable=False, index=True),
        sa.Column("clicks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("urls")

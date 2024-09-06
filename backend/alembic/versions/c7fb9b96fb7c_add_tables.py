"""add tables

Revision ID: c7fb9b96fb7c
Revises: 
Create Date: 2024-09-05 14:00:44.066269

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import TIMESTAMP

# revision identifiers, used by Alembic.
revision: str = "c7fb9b96fb7c"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "audio",
        sa.Column("id", sa.String(length=64), nullable=False, primary_key=True),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("root_dir_path", sa.String(length=255), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("created_at", TIMESTAMP(fsp=6), nullable=True),
        sa.Column("updated_at", TIMESTAMP(fsp=6), nullable=True),
    )
    op.create_table(
        "history",
        sa.Column("id", sa.String(length=64), nullable=False, primary_key=True),
        sa.Column("role", sa.String(length=64), nullable=True),
        sa.Column("data", sa.JSON, nullable=False),
        sa.Column("is_deleted", sa.Boolean, default=False, nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", TIMESTAMP(fsp=6), nullable=True),
        sa.Column("updated_at", TIMESTAMP(fsp=6), nullable=True),
    )


def downgrade():
    op.drop_table("audio")
    op.drop_table("history")

"""add google authentication fields

Revision ID: caf3686b13ff
Revises: bad86455a04e
Create Date: 2026-10-06 21:50:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "caf3686b13ff"
down_revision: Union[str, None] = "bad86455a04e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""

    # Google-authenticated users do not have a local password.
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(length=255),
        nullable=True,
    )

    # Store Google account ID.
    op.add_column(
        "users",
        sa.Column(
            "google_id",
            sa.String(length=255),
            nullable=True,
        ),
    )

    # Store authentication provider.
    # Existing users will receive "local".
    op.add_column(
        "users",
        sa.Column(
            "auth_provider",
            sa.String(length=20),
            nullable=False,
            server_default="local",
        ),
    )

    # Google IDs must be unique.
    op.create_index(
        "ix_users_google_id",
        "users",
        ["google_id"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade database schema."""

    op.drop_index(
        "ix_users_google_id",
        table_name="users",
    )

    op.drop_column(
        "users",
        "auth_provider",
    )

    op.drop_column(
        "users",
        "google_id",
    )

    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(length=255),
        nullable=False,
    )

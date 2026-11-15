"""Isolated expiring demo users; existing accounts are unchanged."""
from alembic import op
import sqlalchemy as sa

revision = "b17d8e0a1f42"
down_revision = "a09c3aa869a6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("demo_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_users_demo_expires_at", "users", ["demo_expires_at"])


def downgrade():
    op.drop_index("ix_users_demo_expires_at", table_name="users")
    op.drop_column("users", "demo_expires_at")
    op.drop_column("users", "is_demo")

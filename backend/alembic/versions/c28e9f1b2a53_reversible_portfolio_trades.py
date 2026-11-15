"""Add exact reversal snapshots; leave legacy trades and balances unchanged."""
from alembic import op
import sqlalchemy as sa
from app.db import ExactDecimal

revision = 'c28e9f1b2a53'
down_revision = 'b17d8e0a1f42'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('trades', sa.Column('sequence', sa.Integer(), nullable=True))
    for name in ('before_quantity', 'before_cost_basis', 'before_realized_gain'):
        op.add_column('trades', sa.Column(name, ExactDecimal(), nullable=True))


def downgrade():
    for name in ('before_realized_gain', 'before_cost_basis', 'before_quantity', 'sequence'):
        op.drop_column('trades', name)

"""Encrypted owner connections, shared admission and per-response provenance. No credential backfill."""
from alembic import op
import sqlalchemy as sa

revision = 'd39f0a2c3b64'
down_revision = 'c28e9f1b2a53'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('ai_consent_version', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('conversations', sa.Column('connection_identity', sa.String(64), nullable=True))
    op.add_column('messages', sa.Column('generation_metadata', sa.JSON(), nullable=True))
    op.create_table('ai_connections',
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('mode', sa.String(16), nullable=False),
        sa.Column('provider', sa.String(24)), sa.Column('base_url', sa.String(500)),
        sa.Column('model_id', sa.String(160)), sa.Column('encrypted_key', sa.Text()),
        sa.Column('revision', sa.String(36), nullable=False),
        sa.Column('test_status', sa.String(16), nullable=False),
        sa.Column('tested_at', sa.DateTime(timezone=True)), sa.Column('test_error', sa.String(48)))
    op.create_table('ai_usage',
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('minute_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('minute_count', sa.Integer(), nullable=False),
        sa.Column('day_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('day_count', sa.Integer(), nullable=False),
        sa.Column('lease_token', sa.String(36)), sa.Column('lease_until', sa.DateTime(timezone=True)))
    op.create_index('ix_ai_usage_lease_until', 'ai_usage', ['lease_until'])
    gate = op.create_table('ai_gate', sa.Column('id', sa.Integer(), primary_key=True))
    op.bulk_insert(gate, [{'id': 1}])


def downgrade():
    op.drop_table('ai_usage')
    op.drop_table('ai_connections')
    op.drop_table('ai_gate')
    op.drop_column('messages', 'generation_metadata')
    op.drop_column('conversations', 'connection_identity')
    op.drop_column('users', 'ai_consent_version')

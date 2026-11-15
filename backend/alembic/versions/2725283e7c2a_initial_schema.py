"""initial schema

Revision ID: 2725283e7c2a
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = '2725283e7c2a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('ads',
    sa.Column('title', sa.String(length=120), nullable=False),
    sa.Column('body', sa.String(length=500), nullable=False),
    sa.Column('url', sa.String(length=1000), nullable=False),
    sa.Column('context', sa.String(length=20), nullable=False),
    sa.Column('approved', sa.Boolean(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('starts_on', sa.Date(), nullable=True),
    sa.Column('ends_on', sa.Date(), nullable=True),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('causes',
    sa.Column('title', sa.String(length=120), nullable=False),
    sa.Column('category', sa.String(length=80), nullable=False),
    sa.Column('description', sa.String(length=1000), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('email', sa.String(length=254), nullable=False),
    sa.Column('password_hash', sa.Text(), nullable=False),
    sa.Column('display_name', sa.String(length=80), nullable=False),
    sa.Column('ai_consent', sa.Boolean(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('country', sa.String(length=2), nullable=False),
    sa.Column('timezone', sa.String(length=64), nullable=False),
    sa.Column('language', sa.String(length=10), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('accounts',
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('account_type', sa.String(length=20), nullable=False),
    sa.Column('balance', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.CheckConstraint('CAST(balance AS NUMERIC) >= 0', name='account_nonnegative'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_accounts_user_id'), ['user_id'], unique=False)

    op.create_table('ad_events',
    sa.Column('ad_id', sa.String(length=36), nullable=False),
    sa.Column('kind', sa.String(length=16), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['ad_id'], ['ads.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('ad_events', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_ad_events_user_id'), ['user_id'], unique=False)

    op.create_table('budgets',
    sa.Column('category', sa.String(length=80), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('amount', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=False),
    sa.Column('month', sa.String(length=7), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'category', 'currency', 'month', name='budget_unique')
    )
    with op.batch_alter_table('budgets', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_budgets_user_id'), ['user_id'], unique=False)

    op.create_table('conversations',
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_conversations_user_id'), ['user_id'], unique=False)

    op.create_table('donation_intents',
    sa.Column('cause_id', sa.String(length=36), nullable=False),
    sa.Column('amount', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['cause_id'], ['causes.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('donation_intents', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_donation_intents_user_id'), ['user_id'], unique=False)

    op.create_table('goals',
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('target_amount', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=False),
    sa.Column('saved_amount', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=False),
    sa.Column('target_date', sa.Date(), nullable=True),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('goals', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_goals_user_id'), ['user_id'], unique=False)

    op.create_table('password_resets',
    sa.Column('token_hash', sa.String(length=64), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('used', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token_hash')
    )
    with op.batch_alter_table('password_resets', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_password_resets_user_id'), ['user_id'], unique=False)

    op.create_table('portfolios',
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('portfolios', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_portfolios_user_id'), ['user_id'], unique=False)

    op.create_table('sessions',
    sa.Column('token_hash', sa.String(length=64), nullable=False),
    sa.Column('csrf_hash', sa.String(length=64), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token_hash')
    )
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_sessions_user_id'), ['user_id'], unique=False)

    op.create_table('zakat_history',
    sa.Column('profile', sa.JSON(), nullable=False),
    sa.Column('estimate', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('zakat_history', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_zakat_history_user_id'), ['user_id'], unique=False)

    op.create_table('zakat_profiles',
    sa.Column('data', sa.JSON(), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', name='zakat_profile_user')
    )
    with op.batch_alter_table('zakat_profiles', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_zakat_profiles_user_id'), ['user_id'], unique=False)

    op.create_table('contributions',
    sa.Column('goal_id', sa.String(length=36), nullable=False),
    sa.Column('amount', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('contributions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_contributions_user_id'), ['user_id'], unique=False)

    op.create_table('giving',
    sa.Column('kind', sa.String(length=16), nullable=False),
    sa.Column('amount', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('paid_on', sa.Date(), nullable=False),
    sa.Column('category', sa.String(length=80), nullable=False),
    sa.Column('recipient', sa.String(length=120), nullable=False),
    sa.Column('note', sa.String(length=500), nullable=False),
    sa.Column('history_id', sa.String(length=36), nullable=True),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['history_id'], ['zakat_history.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('giving', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_giving_user_id'), ['user_id'], unique=False)

    op.create_table('holdings',
    sa.Column('portfolio_id', sa.String(length=36), nullable=False),
    sa.Column('symbol', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('quantity', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=False),
    sa.Column('cost_basis', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=False),
    sa.Column('realized_gain', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=False),
    sa.Column('quote_price', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=True),
    sa.Column('quote_date', sa.Date(), nullable=True),
    sa.Column('quote_source', sa.String(length=200), nullable=True),
    sa.Column('screening_status', sa.String(length=48), nullable=False),
    sa.Column('screening_source', sa.String(length=200), nullable=True),
    sa.Column('screening_date', sa.Date(), nullable=True),
    sa.Column('screening_notes', sa.String(length=1000), nullable=True),
    sa.Column('screening_assessment', sa.JSON(), nullable=True),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.CheckConstraint('CAST(quantity AS NUMERIC) >= 0', name='holding_nonnegative'),
    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'portfolio_id', 'symbol', 'currency', name='holding_unique')
    )
    with op.batch_alter_table('holdings', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_holdings_user_id'), ['user_id'], unique=False)

    op.create_table('messages',
    sa.Column('conversation_id', sa.String(length=36), nullable=False),
    sa.Column('role', sa.String(length=16), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('is_demo', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_messages_user_id'), ['user_id'], unique=False)

    op.create_table('transactions',
    sa.Column('account_id', sa.String(length=36), nullable=False),
    sa.Column('kind', sa.String(length=20), nullable=False),
    sa.Column('amount', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('category', sa.String(length=80), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=False),
    sa.Column('occurred_on', sa.Date(), nullable=False),
    sa.Column('transfer_id', sa.String(length=36), nullable=True),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.CheckConstraint('CAST(amount AS NUMERIC) > 0', name='transaction_positive'),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_transactions_account_id'), ['account_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_transactions_user_id'), ['user_id'], unique=False)

    op.create_table('trades',
    sa.Column('holding_id', sa.String(length=36), nullable=False),
    sa.Column('side', sa.String(length=4), nullable=False),
    sa.Column('quantity', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=False),
    sa.Column('price', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=False),
    sa.Column('fees', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=False),
    sa.Column('realized_gain', sa.Numeric(24, 6).with_variant(sa.String(40), 'sqlite'), nullable=False),
    sa.Column('traded_on', sa.Date(), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['holding_id'], ['holdings.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('trades', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_trades_user_id'), ['user_id'], unique=False)



def downgrade():
    with op.batch_alter_table('trades', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_trades_user_id'))

    op.drop_table('trades')
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_transactions_user_id'))
        batch_op.drop_index(batch_op.f('ix_transactions_account_id'))

    op.drop_table('transactions')
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_messages_user_id'))

    op.drop_table('messages')
    with op.batch_alter_table('holdings', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_holdings_user_id'))

    op.drop_table('holdings')
    with op.batch_alter_table('giving', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_giving_user_id'))

    op.drop_table('giving')
    with op.batch_alter_table('contributions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_contributions_user_id'))

    op.drop_table('contributions')
    with op.batch_alter_table('zakat_profiles', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_zakat_profiles_user_id'))

    op.drop_table('zakat_profiles')
    with op.batch_alter_table('zakat_history', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_zakat_history_user_id'))

    op.drop_table('zakat_history')
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_sessions_user_id'))

    op.drop_table('sessions')
    with op.batch_alter_table('portfolios', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_portfolios_user_id'))

    op.drop_table('portfolios')
    with op.batch_alter_table('password_resets', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_password_resets_user_id'))

    op.drop_table('password_resets')
    with op.batch_alter_table('goals', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_goals_user_id'))

    op.drop_table('goals')
    with op.batch_alter_table('donation_intents', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_donation_intents_user_id'))

    op.drop_table('donation_intents')
    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_conversations_user_id'))

    op.drop_table('conversations')
    with op.batch_alter_table('budgets', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_budgets_user_id'))

    op.drop_table('budgets')
    with op.batch_alter_table('ad_events', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_ad_events_user_id'))

    op.drop_table('ad_events')
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_accounts_user_id'))

    op.drop_table('accounts')
    op.drop_table('users')
    op.drop_table('causes')
    op.drop_table('ads')

"""Add Billing Context tables: plans and subscriptions

Revision ID: 005
Revises: 004
Create Date: 2025-10-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 建立 plans 表
    op.create_table(
        'plans',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='方案 ID'),
        sa.Column('tier', sa.String(length=20), nullable=False, comment='方案等級: free/basic/pro/enterprise'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='方案名稱'),
        sa.Column('description', sa.Text, nullable=True, comment='方案描述'),
        sa.Column('price_amount', sa.Numeric(precision=10, scale=2), nullable=False, comment='價格金額'),
        sa.Column('price_currency', sa.String(length=3), nullable=False, server_default='TWD', comment='幣別'),
        sa.Column('billing_interval', sa.String(length=10), nullable=False, server_default='month', comment='計費週期: month/year'),
        sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=False, comment='方案功能'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='是否啟用'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tier', name='uq_plans_tier'),
        sa.CheckConstraint("tier IN ('free', 'basic', 'pro', 'enterprise')", name='chk_plan_tier'),
        sa.CheckConstraint("billing_interval IN ('month', 'year')", name='chk_plan_billing_interval'),
        comment='訂閱方案表'
    )
    
    # 建立索引
    op.create_index('idx_plans_tier', 'plans', ['tier'], unique=False)
    
    # 建立 subscriptions 表
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=False), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='訂閱 ID (UUID)'),
        sa.Column('merchant_id', postgresql.UUID(as_uuid=False), nullable=False, comment='商家 ID'),
        sa.Column('plan_id', sa.Integer(), nullable=False, comment='方案 ID'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='trialing', comment='訂閱狀態: active/past_due/cancelled/trialing'),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=False, comment='當前週期開始時間'),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True, comment='當前週期結束時間'),
        sa.Column('trial_end', sa.DateTime(timezone=True), nullable=True, comment='試用期結束時間'),
        sa.Column('stripe_subscription_id', sa.String(length=100), nullable=True, comment='Stripe 訂閱 ID'),
        sa.Column('stripe_customer_id', sa.String(length=100), nullable=True, comment='Stripe 客戶 ID'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True, comment='取消時間'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id']),
        sa.UniqueConstraint('stripe_subscription_id', name='uq_subscriptions_stripe_sub_id'),
        sa.CheckConstraint("status IN ('active', 'past_due', 'cancelled', 'trialing')", name='chk_subscription_status'),
        comment='訂閱表'
    )
    
    # 建立索引
    op.create_index('idx_subscriptions_merchant_status', 'subscriptions', ['merchant_id', 'status'], unique=False)
    op.create_index('idx_subscriptions_stripe_sub_id', 'subscriptions', ['stripe_subscription_id'], unique=False)


def downgrade() -> None:
    # 刪除索引
    op.drop_index('idx_subscriptions_stripe_sub_id', table_name='subscriptions')
    op.drop_index('idx_subscriptions_merchant_status', table_name='subscriptions')
    op.drop_index('idx_plans_tier', table_name='plans')
    
    # 刪除表
    op.drop_table('subscriptions')
    op.drop_table('plans')


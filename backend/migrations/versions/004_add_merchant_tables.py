"""Add Merchant Context tables

Revision ID: 004
Revises: 003
Create Date: 2025-10-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 建立 merchants 表
    op.create_table(
        'merchants',
        sa.Column('id', postgresql.UUID(as_uuid=False), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='商家 ID (UUID)'),
        sa.Column('slug', sa.String(length=100), nullable=False, comment='商家 slug（URL 友善識別碼）'),
        sa.Column('name', sa.String(length=200), nullable=False, comment='商家名稱'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active', comment='商家狀態: active/suspended/cancelled'),
        
        # LINE 整合
        sa.Column('line_channel_id', sa.String(length=100), nullable=True, comment='LINE Channel ID'),
        sa.Column('line_channel_secret', sa.Text, nullable=True, comment='LINE Channel Secret（加密）'),
        sa.Column('line_channel_access_token', sa.Text, nullable=True, comment='LINE Channel Access Token（加密）'),
        sa.Column('line_bot_basic_id', sa.String(length=100), nullable=True, comment='LINE Bot Basic ID'),
        
        # 設定
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='Asia/Taipei', comment='商家時區'),
        
        # 聯絡資訊
        sa.Column('address', sa.Text, nullable=True, comment='地址'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='電話'),
        
        # 擴充欄位
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}', comment='其他元資料（JSONB）'),
        
        # 審計欄位
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='建立時間'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新時間'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug', name='uq_merchants_slug'),
        sa.CheckConstraint("status IN ('active', 'suspended', 'cancelled')", name='chk_merchant_status'),
        sa.CheckConstraint("slug ~ '^[a-z0-9-]+$'", name='chk_merchant_slug_format'),
        comment='商家主檔表'
    )
    
    # 建立索引
    op.create_index('idx_merchants_slug', 'merchants', ['slug'], unique=False)
    op.create_index(
        'idx_merchants_status_active',
        'merchants',
        ['status'],
        unique=False,
        postgresql_where=sa.text("status = 'active'")
    )


def downgrade() -> None:
    # 刪除索引
    op.drop_index('idx_merchants_status_active', table_name='merchants')
    op.drop_index('idx_merchants_slug', table_name='merchants')
    
    # 刪除表
    op.drop_table('merchants')


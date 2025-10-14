"""Add Identity Context tables: users

Revision ID: 006
Revises: 005
Create Date: 2025-10-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 建立 users 表
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=False), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='用戶 ID (UUID)'),
        sa.Column('email', sa.String(length=255), nullable=True, comment='Email'),
        sa.Column('line_user_id', sa.String(length=100), nullable=True, comment='LINE User ID'),
        sa.Column('password_hash', sa.Text, nullable=True, comment='密碼雜湊'),
        sa.Column('name', sa.String(length=200), nullable=True, comment='姓名'),
        sa.Column('merchant_id', postgresql.UUID(as_uuid=False), nullable=True, comment='所屬商家 ID（租戶隔離）'),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='customer', comment='角色: admin/merchant_owner/merchant_staff/customer'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='是否啟用'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false', comment='Email 是否已驗證'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True, comment='最後登入時間'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='建立時間'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新時間'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email'),
        sa.UniqueConstraint('line_user_id', name='uq_users_line_user_id'),
        comment='用戶表'
    )
    
    # 建立索引
    op.create_index('idx_users_email', 'users', ['email'], unique=False)
    op.create_index('idx_users_line_user_id', 'users', ['line_user_id'], unique=False)
    op.create_index('idx_users_merchant_id', 'users', ['merchant_id'], unique=False)
    op.create_index('idx_users_merchant_role', 'users', ['merchant_id', 'role'], unique=False)


def downgrade() -> None:
    # 刪除索引
    op.drop_index('idx_users_merchant_role', table_name='users')
    op.drop_index('idx_users_merchant_id', table_name='users')
    op.drop_index('idx_users_line_user_id', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    
    # 刪除表
    op.drop_table('users')


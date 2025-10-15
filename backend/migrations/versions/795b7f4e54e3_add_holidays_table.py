"""Add holidays table

Revision ID: 795b7f4e54e3
Revises: 006
Create Date: 2025-10-15 10:08:43.025544

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '795b7f4e54e3'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 創建 holidays 表
    op.create_table(
        'holidays',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('merchant_id', UUID(as_uuid=False), nullable=False),
        sa.Column('holiday_date', sa.Date(), nullable=False, comment='休假日期'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='休假名稱'),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false', comment='是否每年重複'),
        sa.PrimaryKeyConstraint('id'),
        comment='休假日表'
    )
    
    # 創建索引
    op.create_index('idx_holidays_merchant_date', 'holidays', ['merchant_id', 'holiday_date'])
    op.create_index('uq_holidays_merchant_date', 'holidays', ['merchant_id', 'holiday_date'], unique=True)


def downgrade() -> None:
    # 刪除索引
    op.drop_index('uq_holidays_merchant_date', table_name='holidays')
    op.drop_index('idx_holidays_merchant_date', table_name='holidays')
    
    # 刪除表
    op.drop_table('holidays')


"""Add Catalog Context tables: services, service_options, staff, staff_working_hours

Revision ID: 003
Revises: 002
Create Date: 2025-10-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """建立 Catalog Context 資料表"""
    
    # === services 表 ===
    op.create_table(
        'services',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, comment='服務 ID'),
        sa.Column('merchant_id', postgresql.UUID(as_uuid=False), nullable=False, index=True, comment='商家 ID'),
        sa.Column('name', sa.String(100), nullable=False, comment='服務名稱'),
        sa.Column('category', sa.String(20), nullable=False, server_default='basic', comment='分類'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('base_price_amount', sa.Numeric(10, 2), nullable=False, comment='基礎價格'),
        sa.Column('base_price_currency', sa.String(3), nullable=False, server_default='TWD', comment='幣別'),
        sa.Column('base_duration_minutes', sa.Integer(), nullable=False, comment='基礎時長（分鐘）'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='是否啟用'),
        sa.Column('allow_stack', sa.Boolean(), nullable=False, server_default='true', comment='允許堆疊'),
        sa.CheckConstraint('base_price_amount >= 0', name='chk_service_price_positive'),
        sa.CheckConstraint('base_duration_minutes > 0', name='chk_service_duration_positive'),
        comment='服務表'
    )
    
    op.create_index('idx_services_merchant_active', 'services', ['merchant_id', 'is_active'])
    
    # === service_options 表 ===
    op.create_table(
        'service_options',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('service_id', sa.Integer(), sa.ForeignKey('services.id', ondelete='CASCADE'), nullable=False, comment='所屬服務 ID'),
        sa.Column('name', sa.String(100), nullable=False, comment='選項名稱'),
        sa.Column('add_price_amount', sa.Numeric(10, 2), nullable=False, comment='加價金額'),
        sa.Column('add_price_currency', sa.String(3), nullable=False, server_default='TWD'),
        sa.Column('add_duration_minutes', sa.Integer(), nullable=False, comment='增加時長'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0', comment='顯示順序'),
        sa.CheckConstraint('add_price_amount >= 0', name='chk_option_price_positive'),
        sa.CheckConstraint('add_duration_minutes >= 0', name='chk_option_duration_positive'),
        comment='服務加購選項表'
    )
    
    op.create_index('idx_service_options_service', 'service_options', ['service_id', 'is_active'])
    
    # === staff 表 ===
    op.create_table(
        'staff',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, comment='員工 ID'),
        sa.Column('merchant_id', postgresql.UUID(as_uuid=False), nullable=False, index=True, comment='商家 ID'),
        sa.Column('name', sa.String(100), nullable=False, comment='姓名'),
        sa.Column('email', sa.String(255), nullable=True, comment='Email'),
        sa.Column('phone', sa.String(20), nullable=True, comment='電話'),
        sa.Column('skills', postgresql.ARRAY(sa.Integer()), nullable=False, server_default='{}', comment='技能（service_id 陣列）'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='是否啟用'),
        comment='員工表'
    )
    
    op.create_index('idx_staff_merchant_active', 'staff', ['merchant_id', 'is_active'])
    
    # 建立 GIN 索引用於 ARRAY 查詢
    op.execute("CREATE INDEX idx_staff_skills ON staff USING gin(skills);")
    
    # === staff_working_hours 表 ===
    op.create_table(
        'staff_working_hours',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('staff_id', sa.Integer(), sa.ForeignKey('staff.id', ondelete='CASCADE'), nullable=False, comment='員工 ID'),
        sa.Column('day_of_week', sa.Integer(), nullable=False, comment='星期（0=Monday, 6=Sunday）'),
        sa.Column('start_time', sa.Time(), nullable=False, comment='開始時間'),
        sa.Column('end_time', sa.Time(), nullable=False, comment='結束時間'),
        sa.CheckConstraint('day_of_week >= 0 AND day_of_week <= 6', name='chk_day_of_week_range'),
        sa.CheckConstraint('start_time < end_time', name='chk_working_hours_time_order'),
        comment='員工工時表'
    )
    
    op.create_index('idx_staff_working_hours_staff_day', 'staff_working_hours', ['staff_id', 'day_of_week'])
    
    # 唯一約束：同一員工同一天不可有重複工時
    op.create_index('uq_staff_working_hours_staff_day', 'staff_working_hours', ['staff_id', 'day_of_week'], unique=True)


def downgrade() -> None:
    """移除 Catalog 表"""
    op.drop_table('staff_working_hours')
    op.drop_table('staff')
    op.drop_table('service_options')
    op.drop_table('services')


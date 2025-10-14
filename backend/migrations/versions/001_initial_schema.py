"""Initial schema: bookings and booking_locks tables

Revision ID: 001
Revises: 
Create Date: 2025-10-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """建立 bookings 和 booking_locks 表"""
    
    # === bookings 表 ===
    op.create_table(
        'bookings',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('gen_random_uuid()'), comment='預約 ID'),
        sa.Column('merchant_id', postgresql.UUID(as_uuid=False), nullable=False, index=True, comment='商家 ID'),
        sa.Column('staff_id', sa.Integer(), nullable=False, comment='員工 ID'),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending', comment='狀態'),
        sa.Column('start_at', sa.DateTime(timezone=True), nullable=False, comment='開始時間'),
        sa.Column('end_at', sa.DateTime(timezone=True), nullable=False, comment='結束時間'),
        sa.Column('customer', postgresql.JSON(astext_type=sa.Text()), nullable=False, comment='客戶資訊'),
        sa.Column('items', postgresql.JSON(astext_type=sa.Text()), nullable=False, comment='預約項目'),
        sa.Column('total_price_amount', sa.Numeric(10, 2), nullable=False, comment='總價'),
        sa.Column('total_price_currency', sa.String(3), nullable=False, server_default='TWD', comment='幣別'),
        sa.Column('total_duration_minutes', sa.Integer(), nullable=False, comment='總時長'),
        sa.Column('notes', sa.Text(), nullable=True, comment='備註'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('pending', 'confirmed', 'completed', 'cancelled')", name='chk_booking_status'),
        sa.CheckConstraint('start_at < end_at', name='chk_booking_time_order'),
        sa.CheckConstraint('total_duration_minutes > 0', name='chk_booking_duration_positive'),
        comment='預約主表'
    )
    
    # 建立索引
    op.create_index('idx_bookings_merchant_staff_time', 'bookings', ['merchant_id', 'staff_id', 'start_at'])
    op.create_index('idx_bookings_merchant_status', 'bookings', ['merchant_id', 'status'])
    op.create_index('idx_bookings_customer_line_id', 'bookings', [sa.text("(customer->>'line_user_id')")], postgresql_using='btree')
    
    # === booking_locks 表 ===
    op.create_table(
        'booking_locks',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('gen_random_uuid()'), comment='鎖定 ID'),
        sa.Column('merchant_id', postgresql.UUID(as_uuid=False), nullable=False, index=True, comment='商家 ID'),
        sa.Column('staff_id', sa.Integer(), nullable=False, comment='員工 ID'),
        sa.Column('start_at', sa.DateTime(timezone=True), nullable=False, comment='開始時間'),
        sa.Column('end_at', sa.DateTime(timezone=True), nullable=False, comment='結束時間'),
        sa.Column('booking_id', postgresql.UUID(as_uuid=False), sa.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=True, comment='關聯預約 ID'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('start_at < end_at', name='chk_lock_time_order'),
        comment='預約鎖定表'
    )
    
    # 建立索引
    op.create_index('idx_booking_locks_merchant_staff', 'booking_locks', ['merchant_id', 'staff_id'])


def downgrade() -> None:
    """移除表"""
    op.drop_table('booking_locks')
    op.drop_table('bookings')


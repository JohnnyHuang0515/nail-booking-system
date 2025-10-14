"""Add EXCLUDE constraint to prevent booking overlaps

Revision ID: 002
Revises: 001
Create Date: 2025-10-14

⚠️ 關鍵 Migration ⚠️
此遷移新增 PostgreSQL EXCLUDE USING GIST 約束，確保同一員工無時段重疊
這是系統強一致性的核心保證

ADR 參考: docs/04_architecture_decision_record_002_exclude_constraint.md
"""
from alembic import op

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """新增 EXCLUDE 約束"""
    
    # STEP 1: 安裝 btree_gist extension（tstzrange 重疊檢測需要）
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")
    
    # STEP 2: 新增 EXCLUDE 約束
    # 約束邏輯：同一商家、同一員工的時間範圍不可重疊
    op.execute("""
        ALTER TABLE booking_locks
        ADD CONSTRAINT no_overlap_booking_locks
        EXCLUDE USING gist (
            merchant_id WITH =,
            staff_id WITH =,
            tstzrange(start_at, end_at) WITH &&
        );
    """)
    
    # STEP 3: 新增註解
    op.execute("""
        COMMENT ON CONSTRAINT no_overlap_booking_locks ON booking_locks IS
        'EXCLUDE 約束：確保同一商家的同一員工在同一時間只能有一個預約鎖定（防重疊）';
    """)


def downgrade() -> None:
    """移除 EXCLUDE 約束"""
    op.execute("ALTER TABLE booking_locks DROP CONSTRAINT IF EXISTS no_overlap_booking_locks;")
    # 注意：不移除 btree_gist extension，因為可能被其他表使用


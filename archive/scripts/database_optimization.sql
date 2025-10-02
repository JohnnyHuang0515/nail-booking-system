-- 多商家美甲預約系統 - 資料庫優化腳本
-- 包含索引、約束和 Row Level Security 設定

-- ==============================================
-- 1. 索引優化 - 快速查詢同商家資料
-- ==============================================

-- 商家相關索引
CREATE INDEX IF NOT EXISTS idx_users_merchant ON users(merchant_id);
CREATE INDEX IF NOT EXISTS idx_users_merchant_line_user ON users(merchant_id, line_user_id);

CREATE INDEX IF NOT EXISTS idx_services_merchant ON services(merchant_id);
CREATE INDEX IF NOT EXISTS idx_services_merchant_active ON services(merchant_id, is_active);

CREATE INDEX IF NOT EXISTS idx_apts_merchant_date ON appointments(merchant_id, appointment_date);
CREATE INDEX IF NOT EXISTS idx_apts_merchant_user ON appointments(merchant_id, user_id);
CREATE INDEX IF NOT EXISTS idx_apts_merchant_service ON appointments(merchant_id, service_id);
CREATE INDEX IF NOT EXISTS idx_apts_merchant_branch ON appointments(merchant_id, branch_id);
CREATE INDEX IF NOT EXISTS idx_apts_merchant_staff ON appointments(merchant_id, staff_id);
CREATE INDEX IF NOT EXISTS idx_apts_merchant_status ON appointments(merchant_id, status);
CREATE INDEX IF NOT EXISTS idx_apts_date_time ON appointments(appointment_date, appointment_time);

CREATE INDEX IF NOT EXISTS idx_tx_merchant_created ON transactions(merchant_id, created_at);
CREATE INDEX IF NOT EXISTS idx_tx_merchant_user ON transactions(merchant_id, user_id);
CREATE INDEX IF NOT EXISTS idx_tx_merchant_appointment ON transactions(merchant_id, appointment_id);

CREATE INDEX IF NOT EXISTS idx_business_hours_merchant ON business_hours(merchant_id);
CREATE INDEX IF NOT EXISTS idx_business_hours_merchant_branch ON business_hours(merchant_id, branch_id);
CREATE INDEX IF NOT EXISTS idx_business_hours_day ON business_hours(day_of_week);

CREATE INDEX IF NOT EXISTS idx_time_off_merchant ON time_off(merchant_id);
CREATE INDEX IF NOT EXISTS idx_time_off_merchant_branch ON time_off(merchant_id, branch_id);
CREATE INDEX IF NOT EXISTS idx_time_off_merchant_staff ON time_off(merchant_id, staff_id);
CREATE INDEX IF NOT EXISTS idx_time_off_datetime ON time_off(start_datetime, end_datetime);

-- LINE Channel 快速查詢
CREATE INDEX IF NOT EXISTS idx_merchants_channel_id ON merchants(line_channel_id);
CREATE INDEX IF NOT EXISTS idx_merchants_active ON merchants(is_active);

-- ==============================================
-- 2. 唯一約束 - 去重與時段衝突防護
-- ==============================================

-- 多租戶唯一約束
CREATE UNIQUE INDEX IF NOT EXISTS uniq_user_per_merchant ON users(merchant_id, line_user_id);
CREATE UNIQUE INDEX IF NOT EXISTS uniq_service_name_per_merchant ON services(merchant_id, name);
CREATE UNIQUE INDEX IF NOT EXISTS uniq_slot_per_staff ON appointments(merchant_id, branch_id, appointment_date, appointment_time, staff_id);

-- 商家層級約束
CREATE UNIQUE INDEX IF NOT EXISTS uniq_merchant_channel ON merchants(line_channel_id);

-- ==============================================
-- 3. 外鍵約束與 CASCADE 策略
-- ==============================================

-- 商家刪除時的級聯策略
ALTER TABLE users DROP CONSTRAINT IF EXISTS fk_users_merchant_id;
ALTER TABLE users ADD CONSTRAINT fk_users_merchant_id 
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE;

ALTER TABLE services DROP CONSTRAINT IF EXISTS fk_services_merchant_id;
ALTER TABLE services ADD CONSTRAINT fk_services_merchant_id 
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE;

ALTER TABLE appointments DROP CONSTRAINT IF EXISTS fk_appointments_merchant_id;
ALTER TABLE appointments ADD CONSTRAINT fk_appointments_merchant_id 
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE;

ALTER TABLE transactions DROP CONSTRAINT IF EXISTS fk_transactions_merchant_id;
ALTER TABLE transactions ADD CONSTRAINT fk_transactions_merchant_id 
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE;

ALTER TABLE business_hours DROP CONSTRAINT IF EXISTS fk_business_hours_merchant_id;
ALTER TABLE business_hours ADD CONSTRAINT fk_business_hours_merchant_id 
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE;

ALTER TABLE time_off DROP CONSTRAINT IF EXISTS fk_time_off_merchant_id;
ALTER TABLE time_off ADD CONSTRAINT fk_time_off_merchant_id 
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE;

-- 用戶刪除時的約束
ALTER TABLE appointments DROP CONSTRAINT IF EXISTS fk_appointments_user_id;
ALTER TABLE appointments ADD CONSTRAINT fk_appointments_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE transactions DROP CONSTRAINT IF EXISTS fk_transactions_user_id;
ALTER TABLE transactions ADD CONSTRAINT fk_transactions_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 服務刪除時的約束
ALTER TABLE appointments DROP CONSTRAINT IF EXISTS fk_appointments_service_id;
ALTER TABLE appointments ADD CONSTRAINT fk_appointments_service_id 
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE RESTRICT;

-- 預約刪除時的約束
ALTER TABLE transactions DROP CONSTRAINT IF EXISTS fk_transactions_appointment_id;
ALTER TABLE transactions ADD CONSTRAINT fk_transactions_appointment_id 
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL;

-- ==============================================
-- 4. Row Level Security (RLS) 設定
-- ==============================================

-- 啟用 RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE services ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_hours ENABLE ROW LEVEL SECURITY;
ALTER TABLE time_off ENABLE ROW LEVEL SECURITY;

-- 創建 RLS 策略
-- Users 表策略
DROP POLICY IF EXISTS users_merchant_isolation ON users;
CREATE POLICY users_merchant_isolation ON users
    USING (merchant_id = current_setting('app.merchant_id', true)::uuid);

-- Services 表策略
DROP POLICY IF EXISTS services_merchant_isolation ON services;
CREATE POLICY services_merchant_isolation ON services
    USING (merchant_id = current_setting('app.merchant_id', true)::uuid);

-- Appointments 表策略
DROP POLICY IF EXISTS appointments_merchant_isolation ON appointments;
CREATE POLICY appointments_merchant_isolation ON appointments
    USING (merchant_id = current_setting('app.merchant_id', true)::uuid);

-- Transactions 表策略
DROP POLICY IF EXISTS transactions_merchant_isolation ON transactions;
CREATE POLICY transactions_merchant_isolation ON transactions
    USING (merchant_id = current_setting('app.merchant_id', true)::uuid);

-- Business Hours 表策略
DROP POLICY IF EXISTS business_hours_merchant_isolation ON business_hours;
CREATE POLICY business_hours_merchant_isolation ON business_hours
    USING (merchant_id = current_setting('app.merchant_id', true)::uuid);

-- Time Off 表策略
DROP POLICY IF EXISTS time_off_merchant_isolation ON time_off;
CREATE POLICY time_off_merchant_isolation ON time_off
    USING (merchant_id = current_setting('app.merchant_id', true)::uuid);

-- ==============================================
-- 5. 性能優化函數和觸發器
-- ==============================================

-- 創建更新時間戳的觸發器函數
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 為需要 updated_at 的表添加觸發器
-- (如果需要的話，可以在相關表添加 updated_at 欄位)

-- 創建商家統計視圖
CREATE OR REPLACE VIEW merchant_stats AS
SELECT 
    m.id as merchant_id,
    m.name as merchant_name,
    m.is_active,
    COUNT(DISTINCT u.id) as total_users,
    COUNT(DISTINCT s.id) as total_services,
    COUNT(DISTINCT a.id) as total_appointments,
    COUNT(DISTINCT CASE WHEN a.status = 'booked' THEN a.id END) as active_appointments,
    COUNT(DISTINCT CASE WHEN a.status = 'completed' THEN a.id END) as completed_appointments,
    COUNT(DISTINCT CASE WHEN a.status = 'cancelled' THEN a.id END) as cancelled_appointments,
    COALESCE(SUM(t.amount), 0) as total_revenue,
    COALESCE(AVG(t.amount), 0) as avg_transaction_amount,
    m.created_at
FROM merchants m
LEFT JOIN users u ON m.id = u.merchant_id
LEFT JOIN services s ON m.id = s.merchant_id
LEFT JOIN appointments a ON m.id = a.merchant_id
LEFT JOIN transactions t ON m.id = t.merchant_id
GROUP BY m.id, m.name, m.is_active, m.created_at;

-- ==============================================
-- 6. 資料驗證約束
-- ==============================================

-- 預約時間約束
ALTER TABLE appointments ADD CONSTRAINT chk_appointment_future_date 
    CHECK (appointment_date >= CURRENT_DATE);

-- 金額約束
ALTER TABLE transactions ADD CONSTRAINT chk_transaction_positive_amount 
    CHECK (amount > 0);

-- 服務價格約束
ALTER TABLE services ADD CONSTRAINT chk_service_positive_price 
    CHECK (price > 0);

-- 服務時長約束
ALTER TABLE services ADD CONSTRAINT chk_service_positive_duration 
    CHECK (duration_minutes > 0);

-- 營業時間約束
ALTER TABLE business_hours ADD CONSTRAINT chk_business_hours_valid_day 
    CHECK (day_of_week >= 0 AND day_of_week <= 6);

ALTER TABLE business_hours ADD CONSTRAINT chk_business_hours_valid_time 
    CHECK (start_time < end_time);

-- 休假時間約束
ALTER TABLE time_off ADD CONSTRAINT chk_time_off_valid_period 
    CHECK (start_datetime < end_datetime);

-- ==============================================
-- 7. 查詢優化建議的函數
-- ==============================================

-- 取得商家可用時段函數
CREATE OR REPLACE FUNCTION get_available_slots(
    p_merchant_id UUID,
    p_date DATE,
    p_service_id UUID
) RETURNS TABLE(
    time_slot TIME,
    is_available BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH service_info AS (
        SELECT duration_minutes 
        FROM services 
        WHERE id = p_service_id AND merchant_id = p_merchant_id
    ),
    business_hours AS (
        SELECT start_time, end_time
        FROM business_hours 
        WHERE merchant_id = p_merchant_id 
        AND day_of_week = EXTRACT(DOW FROM p_date)
    ),
    booked_slots AS (
        SELECT appointment_time, 
               appointment_time + INTERVAL '1 minute' * s.duration_minutes as end_time
        FROM appointments a
        CROSS JOIN service_info s
        WHERE a.merchant_id = p_merchant_id 
        AND a.appointment_date = p_date
        AND a.status IN ('booked', 'confirmed')
    )
    SELECT 
        generate_series(
            bh.start_time,
            bh.end_time - INTERVAL '1 minute' * si.duration_minutes,
            INTERVAL '30 minutes'
        )::TIME as time_slot,
        NOT EXISTS(
            SELECT 1 FROM booked_slots bs 
            WHERE bs.appointment_time <= time_slot 
            AND bs.end_time > time_slot
        ) as is_available
    FROM business_hours bh
    CROSS JOIN service_info si
    WHERE EXISTS (SELECT 1 FROM service_info);
END;
$$ LANGUAGE plpgsql;

-- 取得商家統計函數
CREATE OR REPLACE FUNCTION get_merchant_dashboard_stats(
    p_merchant_id UUID,
    p_start_date DATE DEFAULT NULL,
    p_end_date DATE DEFAULT NULL
) RETURNS TABLE(
    total_users BIGINT,
    total_appointments BIGINT,
    total_revenue NUMERIC,
    avg_rating NUMERIC,
    conversion_rate NUMERIC
) AS $$
DECLARE
    v_start_date DATE := COALESCE(p_start_date, CURRENT_DATE - INTERVAL '30 days');
    v_end_date DATE := COALESCE(p_end_date, CURRENT_DATE);
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT u.id) as total_users,
        COUNT(DISTINCT a.id) as total_appointments,
        COALESCE(SUM(t.amount), 0) as total_revenue,
        0.0 as avg_rating, -- 待實作評分系統
        CASE 
            WHEN COUNT(DISTINCT u.id) > 0 
            THEN (COUNT(DISTINCT a.id)::NUMERIC / COUNT(DISTINCT u.id)::NUMERIC) * 100
            ELSE 0.0
        END as conversion_rate
    FROM merchants m
    LEFT JOIN users u ON m.id = u.merchant_id
    LEFT JOIN appointments a ON m.id = a.merchant_id 
        AND a.created_at >= v_start_date 
        AND a.created_at <= v_end_date
    LEFT JOIN transactions t ON m.id = t.merchant_id 
        AND t.created_at >= v_start_date 
        AND t.created_at <= v_end_date
    WHERE m.id = p_merchant_id;
END;
$$ LANGUAGE plpgsql;

-- ==============================================
-- 8. 清理和維護函數
-- ==============================================

-- 清理過期資料函數
CREATE OR REPLACE FUNCTION cleanup_old_data(
    p_days_to_keep INTEGER DEFAULT 365
) RETURNS INTEGER AS $$
DECLARE
    v_deleted_count INTEGER := 0;
BEGIN
    -- 清理過期的取消預約記錄
    DELETE FROM appointments 
    WHERE status = 'cancelled' 
    AND created_at < NOW() - INTERVAL '1 day' * p_days_to_keep;
    
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    
    -- 清理過期的休假記錄
    DELETE FROM time_off 
    WHERE end_datetime < NOW() - INTERVAL '1 day' * p_days_to_keep;
    
    GET DIAGNOSTICS v_deleted_count = v_deleted_count + ROW_COUNT;
    
    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 創建定期清理任務（需要 pg_cron 擴展）
-- SELECT cron.schedule('cleanup-old-data', '0 2 * * *', 'SELECT cleanup_old_data(365);');

COMMENT ON DATABASE nail_booking IS '多商家美甲預約系統資料庫';
COMMENT ON TABLE merchants IS '商家與 LINE 憑證管理';
COMMENT ON TABLE users IS '用戶資料，支援多商家';
COMMENT ON TABLE services IS '服務項目，每商家獨立管理';
COMMENT ON TABLE appointments IS '預約記錄，包含時段衝突檢查';
COMMENT ON TABLE transactions IS '交易記錄，與預約關聯';
COMMENT ON TABLE business_hours IS '營業時間設定';
COMMENT ON TABLE time_off IS '休假時間管理';

-- 完成訊息
SELECT '資料庫優化腳本執行完成！' as message;

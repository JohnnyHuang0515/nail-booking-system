# 多商家美甲預約系統 - ERD 文檔

## 概述

本文檔詳細描述多商家美甲預約系統的資料庫實體關係圖 (ERD)，包含完整的表結構、約束、索引和安全設定。

## 系統架構原則

### 1. 多租戶架構
- 所有業務資料都與 `merchant_id` 關聯
- 嚴格的資料隔離，防止跨商家存取
- 支援 Row Level Security (RLS) 確保資料安全

### 2. 擴展性設計
- 預留分店支援 (`branch_id`)
- 預留員工管理 (`staff_id`)
- 靈活的營業時間和休假管理

### 3. LINE 整合
- 每個商家獨立的 LINE Channel
- 支援多個 LINE 官方帳號
- 完整的憑證管理

## 實體關係圖

```
┌─────────────────────────────────────────────────────────────────┐
│                        MERCHANTS                                │
├─────────────────────────────────────────────────────────────────┤
│ merchant_id (PK)     │ UUID, Primary Key                        │
│ name                 │ VARCHAR(100), NOT NULL                   │
│ line_channel_id      │ VARCHAR(64), UNIQUE, NOT NULL           │
│ line_channel_secret  │ VARCHAR(64), NOT NULL                   │
│ line_channel_token   │ TEXT, NOT NULL                          │
│ timezone             │ VARCHAR(50), DEFAULT 'Asia/Taipei'     │
│ is_active            │ BOOLEAN, DEFAULT TRUE                   │
│ created_at           │ TIMESTAMP WITH TIME ZONE                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ 1:N
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                          USERS                                  │
├─────────────────────────────────────────────────────────────────┤
│ user_id (PK)         │ UUID, Primary Key                        │
│ merchant_id (FK)     │ UUID, Foreign Key → merchants.id        │
│ line_user_id         │ VARCHAR(64), NOT NULL                   │
│ name                 │ VARCHAR(100), NULLABLE                  │
│ phone                │ VARCHAR(20), NULLABLE                   │
│ created_at           │ TIMESTAMP WITH TIME ZONE                │
│                                                                 │
│ UNIQUE(merchant_id, line_user_id)                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ 1:N
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        SERVICES                                 │
├─────────────────────────────────────────────────────────────────┤
│ service_id (PK)      │ UUID, Primary Key                        │
│ merchant_id (FK)     │ UUID, Foreign Key → merchants.id        │
│ branch_id (FK)       │ UUID, NULLABLE, Foreign Key → branches  │
│ name                 │ VARCHAR(100), NOT NULL                   │
│ price                │ NUMERIC(10,2), NOT NULL                  │
│ duration_minutes     │ INTEGER, NOT NULL                        │
│ is_active            │ BOOLEAN, DEFAULT TRUE                   │
│                                                                 │
│ UNIQUE(merchant_id, name)                                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ 1:N
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       APPOINTMENTS                              │
├─────────────────────────────────────────────────────────────────┤
│ appointment_id (PK)  │ UUID, Primary Key                        │
│ merchant_id (FK)     │ UUID, Foreign Key → merchants.id        │
│ branch_id (FK)       │ UUID, NULLABLE, Foreign Key → branches  │
│ user_id (FK)         │ UUID, Foreign Key → users.id            │
│ service_id (FK)      │ UUID, Foreign Key → services.id         │
│ appointment_date     │ DATE, NOT NULL                           │
│ appointment_time     │ TIME, NOT NULL                           │
│ staff_id (FK)        │ UUID, NULLABLE, Foreign Key → staff     │
│ status               │ ENUM('booked','completed','cancelled')  │
│ created_at           │ TIMESTAMP WITH TIME ZONE                │
│                                                                 │
│ UNIQUE(merchant_id, branch_id, date, time, staff_id)          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ 1:1
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TRANSACTIONS                               │
├─────────────────────────────────────────────────────────────────┤
│ transaction_id (PK)  │ UUID, Primary Key                        │
│ merchant_id (FK)     │ UUID, Foreign Key → merchants.id        │
│ user_id (FK)         │ UUID, Foreign Key → users.id            │
│ appointment_id (FK)  │ UUID, NULLABLE, Foreign Key → appointments│
│ amount               │ NUMERIC(10,2), NOT NULL                  │
│ notes                │ TEXT, NULLABLE                          │
│ created_at           │ TIMESTAMP WITH TIME ZONE                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      BUSINESS_HOURS                             │
├─────────────────────────────────────────────────────────────────┤
│ business_hour_id (PK)│ UUID, Primary Key                        │
│ merchant_id (FK)     │ UUID, Foreign Key → merchants.id        │
│ branch_id (FK)       │ UUID, NULLABLE, Foreign Key → branches  │
│ day_of_week          │ INTEGER, NOT NULL (0=Sunday, 6=Saturday)│
│ start_time           │ TIME, NOT NULL                           │
│ end_time             │ TIME, NOT NULL                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         TIME_OFF                                │
├─────────────────────────────────────────────────────────────────┤
│ time_off_id (PK)     │ UUID, Primary Key                        │
│ merchant_id (FK)     │ UUID, Foreign Key → merchants.id        │
│ branch_id (FK)       │ UUID, NULLABLE, Foreign Key → branches  │
│ staff_id (FK)        │ UUID, NULLABLE, Foreign Key → staff     │
│ start_datetime       │ TIMESTAMP WITH TIME ZONE                │
│ end_datetime         │ TIMESTAMP WITH TIME ZONE                │
│ reason               │ TEXT, NULLABLE                          │
└─────────────────────────────────────────────────────────────────┘
```

## 表結構詳解

### 1. MERCHANTS (商家表)
**用途**: 管理商家基本資訊和 LINE 憑證

**關鍵欄位**:
- `line_channel_id`: LINE Channel ID，用於識別商家
- `line_channel_secret`: LINE Channel Secret，用於簽名驗證
- `line_channel_access_token`: LINE Access Token，用於 API 調用

**約束**:
- `line_channel_id` 必須唯一
- 所有欄位都是必填的（除了 `timezone` 有預設值）

### 2. USERS (用戶表)
**用途**: 管理用戶資訊，支援同一人在多商家有不同的記錄

**關鍵特性**:
- 同一 `line_user_id` 可以在不同商家有不同記錄
- 每個商家內的 `line_user_id` 必須唯一
- 支援用戶基本資訊（姓名、電話）

**約束**:
- `UNIQUE(merchant_id, line_user_id)`: 確保同一人在同一商家只有一筆記錄

### 3. SERVICES (服務表)
**用途**: 管理每個商家的服務項目

**關鍵特性**:
- 每個商家可以有自己的服務項目
- 支援分店層級的服務（通過 `branch_id`）
- 包含價格和時長資訊

**約束**:
- `UNIQUE(merchant_id, name)`: 確保同一商家內服務名稱唯一

### 4. APPOINTMENTS (預約表)
**用途**: 管理預約記錄

**關鍵特性**:
- 支援分店和員工層級的預約
- 時段衝突檢查
- 預約狀態管理

**約束**:
- `UNIQUE(merchant_id, branch_id, appointment_date, appointment_time, staff_id)`: 防止時段衝突

### 5. TRANSACTIONS (交易表)
**用途**: 管理交易記錄

**關鍵特性**:
- 與預約關聯（可選）
- 支援交易金額和備註
- 完整的交易歷史

### 6. BUSINESS_HOURS (營業時間表)
**用途**: 管理營業時間設定

**關鍵特性**:
- 支援分店層級的營業時間
- 每週七天獨立設定
- 靈活的時間管理

### 7. TIME_OFF (休假時間表)
**用途**: 管理休假和暫停服務時間

**關鍵特性**:
- 支援分店和員工層級的休假
- 時間範圍管理
- 休假原因記錄

## 索引設計

### 1. 性能優化索引
```sql
-- 商家相關快速查詢
CREATE INDEX idx_users_merchant ON users(merchant_id);
CREATE INDEX idx_services_merchant ON services(merchant_id);
CREATE INDEX idx_apts_merchant_date ON appointments(merchant_id, appointment_date);
CREATE INDEX idx_tx_merchant_created ON transactions(merchant_id, created_at);

-- LINE Channel 快速查詢
CREATE INDEX idx_merchants_channel_id ON merchants(line_channel_id);
```

### 2. 唯一性約束索引
```sql
-- 多租戶唯一約束
CREATE UNIQUE INDEX uniq_user_per_merchant ON users(merchant_id, line_user_id);
CREATE UNIQUE INDEX uniq_service_name_per_merchant ON services(merchant_id, name);
CREATE UNIQUE INDEX uniq_slot_per_staff ON appointments(merchant_id, branch_id, appointment_date, appointment_time, staff_id);
```

## 安全設計

### 1. Row Level Security (RLS)
```sql
-- 啟用 RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE services ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- 創建 RLS 策略
CREATE POLICY users_merchant_isolation ON users
    USING (merchant_id = current_setting('app.merchant_id', true)::uuid);
```

### 2. 資料隔離策略
- 所有查詢都必須包含 `merchant_id` 篩選
- 應用層面自動設定 RLS 上下文
- 外鍵約束確保資料一致性

## 擴展性設計

### 1. 分店支援
- 所有相關表都預留 `branch_id` 欄位
- 支援分店層級的服務、預約、營業時間管理

### 2. 員工管理
- 預留 `staff_id` 欄位支援員工排班
- 支援員工層級的休假和預約分配

### 3. 多語言支援
- 預留擴展欄位支援多語言內容
- 靈活的模板系統

## 資料完整性

### 1. 外鍵約束
```sql
-- CASCADE 策略
ALTER TABLE users ADD CONSTRAINT fk_users_merchant_id 
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE;

-- RESTRICT 策略（保護重要資料）
ALTER TABLE appointments ADD CONSTRAINT fk_appointments_service_id 
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE RESTRICT;
```

### 2. 檢查約束
```sql
-- 業務邏輯約束
ALTER TABLE appointments ADD CONSTRAINT chk_appointment_future_date 
    CHECK (appointment_date >= CURRENT_DATE);

ALTER TABLE transactions ADD CONSTRAINT chk_transaction_positive_amount 
    CHECK (amount > 0);
```

## 性能優化

### 1. 查詢優化
- 複合索引支援常見查詢模式
- 分區表支援大數據量（可選）
- 視圖提供常用統計資料

### 2. 快取策略
- Redis 快取商家資訊
- 快取 LINE 用戶資料
- 快取服務列表和營業時間

## 監控與維護

### 1. 統計視圖
```sql
CREATE VIEW merchant_stats AS
SELECT 
    m.id as merchant_id,
    m.name as merchant_name,
    COUNT(DISTINCT u.id) as total_users,
    COUNT(DISTINCT a.id) as total_appointments,
    COALESCE(SUM(t.amount), 0) as total_revenue
FROM merchants m
LEFT JOIN users u ON m.id = u.merchant_id
LEFT JOIN appointments a ON m.id = a.merchant_id
LEFT JOIN transactions t ON m.id = t.merchant_id
GROUP BY m.id, m.name;
```

### 2. 清理函數
```sql
CREATE FUNCTION cleanup_old_data(p_days_to_keep INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
-- 清理過期資料的邏輯
$$;
```

## 部署建議

### 1. 環境配置
- 使用 PostgreSQL 12+ 版本
- 啟用 RLS 和相關擴展
- 配置適當的記憶體和儲存

### 2. 備份策略
- 定期全量備份
- 增量備份和 WAL 歸檔
- 跨區域備份複製

### 3. 監控指標
- 資料庫連接數
- 查詢性能
- 磁碟使用量
- 錯誤率統計

## 總結

這個 ERD 設計完全符合多商家美甲預約系統的需求：

✅ **多租戶架構**: 完整的資料隔離機制  
✅ **LINE 整合**: 支援多個官方帳號  
✅ **擴展性**: 預留分店和員工管理  
✅ **安全性**: RLS 和多重約束保護  
✅ **性能**: 優化的索引和查詢設計  
✅ **維護性**: 完整的監控和清理機制  

這個設計可以支援數千個商家，每個商家管理數萬個用戶和預約，同時保持高性能和資料安全。

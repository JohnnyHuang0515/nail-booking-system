---
title: 美甲 LINE 官方帳號預約系統設計文件 (v2)
---

# 一、系統需求

## 1. 主要功能

- **預約系統**：顧客可透過 LIFF 介面選擇日期、時段與服務項目，並收到 LINE 確認與提醒通知。
- **消費紀錄**：顧客可查詢歷史消費，店家可透過後台輸入消費金額與備註。
- **LINE 官方帳號整合**：使用 Rich Menu 引導操作，Webhook 處理後端互動，Push API 發送通知。
- **IG 作品集**：不需後台管理，直接從 LINE Rich Menu 導向店家的 Instagram 頁面。

## 2. 使用者對象

- **顧客**：使用 LINE 預約服務、查詢紀錄。
- **店家（美甲師）**：使用網頁後台管理預約、服務項目、營業時間與顧客資料。

# 二、架構設計

## 1. 前端

- **顧客端 (LINE)**：
  - **Rich Menu**：作為主要入口，提供「我要預約」、「消費紀錄」、「IG 作品集」、「常見問題」等按鈕。
  - **LIFF (LINE Front-end Framework)**：用於預約流程、新使用者資料填寫。提供比純聊天機器人更佳的 UI/UX。
  - **自動回覆訊息**：處理常見問題或非預約相關的互動。
- **店家端 (Web)**：
  - 一個獨立的**網頁版後台管理介面**，供店家管理所有業務。

## 2. 後端服務

- **框架**：FastAPI (Python) 或 NestJS (Node.js)
- **功能模組**：
  - **預約管理**：處理預約的建立、查詢、取消。其核心是動態計算可預約時段，詳細邏輯如下：
          1. **定義固定時段**：系統預先定義好每天的固定可預約時間點，即 **12:00、15:00、18:00**。
          2. **檢查營業時間**：確認這些時段是否在店家設定的當日 `business_hours` 範圍內。
          3. **排除休息時段**：過濾掉與店家在 `time_off` 表中設定的特殊休假（如：私人事務、度假）重疊的時段。
          4. **排除已預約時段**：過濾掉在 `appointments` 表中已被預約的時段。
          5. **提供最終選項**：將剩餘的可用時段提供給前端 LIFF 介面，供顧客選擇。
          *註：每個時段的長度隱含為 3 小時（例如從 12:00 到 15:00）。`services.duration_minutes` 用於確保所選服務能在此時間內完成。*
  - **會員系統**：管理顧客基本資料。
  - **消費紀錄**：記錄與查詢每筆交易。
  - **通知推播**：發送各類提醒與通知。
    - **對顧客**：預約成功、預約提醒（24小時前）、取消確認。
    - **對店家**：新預約成立通知、顧客取消預約通知。
  - **後台管理 API**：提供店家後台所需的所有 API，包含服務項目、營業時間、特殊休假日的 CRUD (建立、讀取、更新、刪除) 操作。
- **安全性**：
  - LINE Webhook 必須驗證 `X-Line-Signature` 簽章，防止未經授權的請求。
  - 店家後台需有登入驗證機制。

## 3. 資料庫

- **主要資料庫**：PostgreSQL
- **快取/排程**：Redis，用於快取常用資料（如營業時間）與處理預約排程提醒。

## 4. 部署方式

需常駐上線，可選：
- 雲端伺服器（AWS / GCP / 台智雲）
- VPS（Linode, DigitalOcean）
- Serverless（AWS Lambda + API Gateway），適合事件驅動的架構。

# 三、店家管理後台 (Admin Panel) 核心功能

- **儀表板 (Dashboard)**：顯示今日預約數、待處理事項等關鍵資訊。
- **行事曆管理**：
  - 以日/週/月檢視所有預約。
  - 可直接在日曆上點擊新增或修改預約。
- **預約管理**：
  - 查看所有預約列表。
  - 手動新增、修改或取消預約。
  - 標記預約狀態（如：已完成、No-Show）。
- **時段管理**：
  - 設定每週的固定營業時間 (`business_hours`)。
  - 新增或刪除特殊休假日 (`time_off`)。
- **服務管理**：新增、修改、刪除服務項目及其價格、所需時間 (`duration_minutes`)。
- **顧客管理**：查看顧客列表、聯絡方式及過往消費紀錄。

# 四、PostgreSQL 資料表 Schema

```sql
-- 使用者(顧客)表
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    line_user_id VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 服務項目表
CREATE TABLE services (
    service_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    duration_minutes INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE -- 可用來暫時下架服務
);

-- 預約表
CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    service_id INT NOT NULL REFERENCES services(service_id) ON DELETE RESTRICT,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    -- 狀態：booked(已預約), completed(已完成), cancelled(已取消), no-show(未到)
    status VARCHAR(20) NOT NULL DEFAULT 'booked',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 交易(消費紀錄)表
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    appointment_id INT REFERENCES appointments(appointment_id) ON DELETE SET NULL,
    amount NUMERIC(10, 2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 營業時間表
CREATE TABLE business_hours (
    hour_id SERIAL PRIMARY KEY,
    -- 0=週日, 1=週一, ..., 6=週六
    day_of_week INT NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    UNIQUE(day_of_week, start_time, end_time)
);

-- 特殊休假表
CREATE TABLE time_off (
    off_id SERIAL PRIMARY KEY,
    start_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    end_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    reason TEXT
);
```

# 五、領域模型 (Domain-Driven Design)

為了讓系統能精準反映業務，我們採用 DDD 的核心思想來指導設計與開發。

## 1. 通用語言 (Ubiquitous Language)

以下是團隊成員（開發者與業務方）之間溝通時應共同遵守的核心詞彙：

- **User**: 使用系統預約服務的顧客。
- **Service**: 美甲師提供的具體服務項目，包含價格和標準時長。
- **Appointment**: 一次完整的預約事件，是系統的核心物件。它代表了特定 User 在特定時間點 (TimeSlot) 預約了特定的 Service。
- **TimeSlot**: 一個可供預約的時間單位。在我們的系統中，特指 `12:00`, `15:00`, `18:00` 這三個固定時間點。
- **BusinessHours**: 店家設定的每週固定營業時間範圍。
- **TimeOff**: 店家因個人事務、休假等原因設定的「不可預約」時間區塊。

## 2. 限界上下文 (Bounded Context)

我們將系統劃分為以下幾個核心上下文，每個上下文有自己專注的領域模型：

- **預約上下文 (Booking Context)**：核心領域。負責處理所有與預約相關的業務邏輯，包括計算可用的 `TimeSlot`、建立 `Appointment`、處理狀態變更等。此上下文是系統最複雜、最有價值的部分。
- **會員上下文 (Membership Context)**：支撐領域。負責管理 `User` 的基本資料（如 LINE ID、姓名、電話）和消費紀錄 (`Transaction`)。

## 3. 聚合 (Aggregate)

聚合是我們操作資料、強制執行業務規則的單位。每個聚合都有一個「聚合根」(Aggregate Root) 作為操作的唯一入口。

- **Appointment Aggregate**:
  - **聚合根**: `Appointment`
  - **描述**: 這是最重要的聚合。所有對預約的操作，例如取消預約 (`cancel`)、標記為完成 (`complete`)，都必須透過 `Appointment` 物件來執行。這樣可以確保在執行操作時，所有相關的業務規則（如：只有在特定狀態下才能取消）都能被一致地應用。

- **User Aggregate**:
  - **聚合根**: `User`
  - **描述**: 代表一個獨立的顧客。未來如果有效費點數、會員等級等功能，相關的規則也會在此聚合內被保護。
# 開發流程總覽手冊 (Development Workflow Cookbook)

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-10-13`
**主要作者 (Lead Author):** `VibeCoding AI`
**狀態 (Status):** `活躍 (Active)`

---

## Ⅰ. 核心理念：從商業價值到高品質程式碼

### 專案使命
**為美甲產業提供一站式預約管理解決方案，透過 LINE 整合降低客戶預約門檻，提升商家經營效率。**

### 第一性原理推演

```
商業目標：提升美甲店營收與客戶滿意度
    ↓
用戶需求：快速預約、避免衝突、即時通知
    ↓
設計策略：強一致性預約 + LINE 整合 + 多租戶隔離
    ↓
架構決策：DDD 領域模型 + CQRS + 事件驅動
    ↓
實作方式：BDD 可執行規格 + TDD 紅綠重構
```

### 品質內建原則

1. **DDD 定義邊界**
   - 6 個 Bounded Context 清晰劃分
   - 聚合內部強一致，聚合間最終一致
   - 不變式由測試守護

2. **BDD 驅動行為**
   - Gherkin 語法定義可執行規格
   - Given-When-Then 對齊業務語言
   - Feature 檔案即活文檔

3. **TDD 保證正確性**
   - 紅→綠→重構循環
   - 單元測試覆蓋率 > 80%
   - 整合測試覆蓋關鍵路徑

---

## Ⅱ. 開發階段與文件產出

### 第一階段：規劃 (Planning) - 定義「為何」與「什麼」

#### 1. 專案簡報與產品需求 (PRD)
**目的：** 定義專案的「為何」與「為誰」
**產出：** `docs/02_project_brief_and_prd.md`

**核心內容：**
- 商業目標：提升美甲店預約效率 30%
- 目標用戶：美甲店老闆、美甲師、終端客戶
- 成功指標：
  - 預約成功率 > 99%
  - 預約衝突率 < 0.1%
  - LINE 推播到達率 > 95%

#### 2. 行為驅動情境 (BDD Scenarios)
**目的：** 將 PRD 轉化為精確、無歧義的自然語言規格
**產出：** `features/*.feature` + `docs/03_behavior_driven_development_guide.md`

**範例 Feature：**
```gherkin
Feature: 可訂時段查詢
  Scenario: 客戶查看特定日期的可預約時段
    Given 商家 "nail-abc" 狀態為 active
    And 員工 "Amy" 在 "2025-10-15" 的工作時間為 "10:00" 到 "18:00"
    And 已存在預約從 "2025-10-15T13:00+08:00" 到 "14:30+08:00" 給 "Amy"
    When 我查詢 "2025-10-15" 員工 "Amy" 的可訂時段
    Then 我不應看到任何與 "13:00-14:30" 重疊的時段
    And 我應至少看到一個時段 "10:00-11:00"
```

---

### 第二階段：設計 (Design) - 定義「如何」的藍圖

#### 3. 架構與設計文檔 (SAD & SDD)
**目的：** 建立系統的結構（架構）並填充具體的實現細節（設計）
**產出：** `docs/05_architecture_and_design_document.md`

**DDD 戰略設計：**

| Bounded Context | 職責 | 主要聚合 |
|----------------|------|---------|
| Identity & Access | 使用者、角色、授權 | User, Role, Permission |
| Merchant (Tenant) | 商家主檔、LINE 憑證 | Merchant, ApiKey |
| Catalog | 服務、員工、工時 | Service, Staff, WorkingHours |
| Booking | 預約建立/變更/鎖定 | Booking, BookingLock |
| Billing | 訂閱、帳單、金流 | Subscription, Invoice |
| Notification | LINE 推播、Webhook | MessageTemplate |

**架構決策記錄 (ADR)：**
- `docs/04_architecture_decision_record_001_postgresql.md`
- `docs/04_architecture_decision_record_002_exclude_constraint.md`
- `docs/04_architecture_decision_record_003_fastapi.md`

---

### 第三階段：開發 (Development) - 精確實現

#### 4. 模組規格與測試
**目的：** 將高層次的 BDD 情境分解到具體的模組層級
**產出：** `docs/07_module_specification_and_tests.md`

**契約式設計範例：**

```python
class BookingService:
    """
    前置條件：
    - merchant 必須為 active
    - staff 必須為 active 且有對應技能
    - 時段不可與現有預約重疊
    
    後置條件：
    - booking_lock 與 booking 同時存在
    - 狀態為 confirmed
    - 發送 BookingConfirmed 事件
    
    不變式：
    - 任一 staff 同時間僅能服務一筆預約
    - total_price = sum(service_price + option_prices)
    """
    
    def create_booking(self, request: BookingRequest) -> Booking:
        # TDD 驅動實作
        pass
```

#### 5. API 設計規格
**目的：** 定義前後端的介面契約
**產出：** `docs/06_api_design_specification.md`

**核心端點：**

| Method | Path | 目的 |
|--------|------|------|
| GET | `/public/merchants/{slug}/slots` | 可訂時段查詢 |
| POST | `/liff/bookings` | 建立預約 |
| DELETE | `/liff/bookings/{id}` | 取消預約 |
| GET | `/merchant/calendar` | 商家日曆 |
| POST | `/admin/merchants` | 建立商家 |

---

### 第四階段：品質與部署 (Quality & Deployment)

#### 6. 安全與上線檢查清單
**目的：** 在設計階段與部署前進行全面的審查
**產出：** `docs/13_security_and_readiness_checklists.md`

**關鍵檢查項：**
- [ ] JWT 認證機制完整
- [ ] 租戶隔離策略驗證
- [ ] LINE 憑證加密儲存
- [ ] Webhook 驗簽機制
- [ ] PG EXCLUDE 約束測試通過
- [ ] 備份策略已啟用

---

## Ⅲ. TDD 實踐流程

### 紅→綠→重構循環

#### Step 1: 寫失敗測試（紅）

```python
def test_booking_prevents_overlap():
    # Arrange
    existing = create_booking(
        staff_id=1,
        start_at=dt(2025,10,16,10,0),
        end_at=dt(2025,10,16,11,0)
    )
    
    # Act & Assert
    with pytest.raises(BookingOverlapError):
        create_booking(
            staff_id=1,
            start_at=dt(2025,10,16,10,30),
            end_at=dt(2025,10,16,11,30)
        )
```

#### Step 2: 最小實作（綠）

```python
def create_booking(self, request):
    # 1. 驗證時段不重疊
    if self._has_overlap(request.staff_id, request.start_at, request.end_at):
        raise BookingOverlapError()
    
    # 2. 建立預約
    booking = Booking(...)
    self.repository.save(booking)
    return booking
```

#### Step 3: 重構

```python
def create_booking(self, request):
    self._validate_no_overlap(request)
    self._validate_merchant_active(request.merchant_id)
    
    booking = self._build_booking(request)
    self.repository.save(booking)
    self.event_bus.publish(BookingConfirmed(booking.id))
    
    return booking
```

---

## Ⅳ. 支援文件

### 專案結構指南
**檔案：** `docs/08_project_structure_guide.md`

```
nail-booking-system/
├── backend/
│   ├── src/
│   │   ├── identity/          # Identity & Access Context
│   │   ├── merchant/          # Merchant Context
│   │   ├── catalog/           # Catalog Context
│   │   ├── booking/           # Booking Context (核心)
│   │   ├── billing/           # Billing Context
│   │   └── notification/      # Notification Context
│   └── tests/
│       ├── features/          # BDD Feature 檔案
│       ├── unit/              # 單元測試
│       └── integration/       # 整合測試
├── frontend/
│   ├── admin/                 # 管理員後台
│   ├── merchant/              # 商家後台
│   └── liff/                  # LINE LIFF 客戶端
└── docs/                      # 所有文檔
```

### 前端架構規範
**檔案：** `docs/12_frontend_architecture_specification.md`

**三前端策略：**
1. **Admin (Next.js)：** 系統管理、商家管理、計費管理
2. **Merchant (Next.js)：** 預約日曆、員工管理、服務設定
3. **LIFF (React)：** 客戶預約、查詢紀錄、LINE 整合

---

## Ⅴ. 開發順序建議

### Week 1-2: DDD 基礎
1. 定義 Ubiquitous Language
2. 劃分 6 個 Bounded Context
3. 設計核心聚合（Booking, Catalog）
4. 撰寫 BDD Feature 檔案

### Week 3-4: TDD 實作
1. 實作 Booking 聚合（紅→綠→重構）
2. 實作 PG EXCLUDE 約束
3. 實作可訂時段計算邏輯
4. 單元測試覆蓋率 > 80%

### Week 5: 前端開發
1. Admin 商家管理功能
2. Merchant 日曆檢視
3. LIFF 預約流程

### Week 6: 整合與上線
1. 整合測試（DB 約束、Webhook）
2. E2E 測試（關鍵路徑）
3. LINE 推播測試
4. 效能測試與優化
5. 上線部署

---

## Ⅵ. 品質指標

### 程式碼品質
- 單元測試覆蓋率：> 80%
- 整合測試：核心路徑 100%
- E2E 測試：關鍵業務流程
- 靜態分析：無 Critical 問題

### 效能指標
- 預約建立 P95：< 300ms
- 可訂查詢 P95：< 200ms
- LINE 推播延遲：< 2s
- 資料庫查詢：< 100ms

### 可靠性指標
- 預約成功率：> 99%
- API 可用性：> 99.9%
- 預約衝突率：< 0.1%
- 推播成功率：> 95%

---

**記住：文檔即契約，測試即規格，品質內建於流程。**


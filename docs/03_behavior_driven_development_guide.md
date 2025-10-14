# 行為驅動情境 (BDD) 指南與範本 - LINE 美甲預約系統

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-10-13`
**主要作者 (Lead Author):** `技術負責人, 產品經理`
**狀態 (Status):** `活躍 (Active)`

---

## Ⅰ. BDD 核心原則

### 1.1 專案特定的 Ubiquitous Language

**核心術語（Booking Domain）：**
- **時段 (Slot)：** 由 `start_at` 和 `end_at` 定義的時間區間
- **佔檔 (BookingLock)：** 建立 Booking 前的暫時鎖定，防止重疊
- **可訂 (Available)：** 員工營業時間 ∩ 無衝突 ∩ 服務能力匹配
- **商家 (Merchant/Tenant)：** 多租戶系統中的獨立商家實體
- **服務 (Service)：** 美甲項目（如：凝膠指甲、光療）
- **選項 (ServiceOption)：** 服務的加購項（如：延長、彩繪）
- **員工 (Staff)：** 提供服務的美甲師

### 1.2 BDD 在本專案的價值

1. **對齊業務語言：** 讓 PM、開發、測試使用相同術語
2. **可執行規格：** Feature 檔案即為活文檔，可直接執行測試
3. **驅動設計：** 從業務行為出發，避免過度設計
4. **迴歸保護：** 每個 Scenario 都是一個自動化測試

---

## Ⅱ. Gherkin 語法速查

### 2.1 基本結構

```gherkin
Feature: 功能名稱
  [功能描述]
  
  Background:
    [所有 Scenario 共用的前置條件]
  
  Scenario: 具體場景名稱
    Given [前置條件]
    When [觸發動作]
    Then [預期結果]
    And [額外條件/結果]
  
  Scenario Outline: 參數化場景
    Given [參數化條件 <param>]
    When [參數化動作 <param>]
    Then [參數化結果 <param>]
    
    Examples:
      | param1 | param2 | param3 |
      | value1 | value2 | value3 |
```

### 2.2 專案特定的步驟慣例

**Given (前置條件)：**
- `Given merchant "{slug}" is active`
- `Given staff "{name}" is active with skills ["{skill1}", "{skill2}"]`
- `Given service "{name}" with base_price {amount} and duration {minutes}`
- `Given a booking exists from "{start_time}" to "{end_time}" for staff "{name}"`

**When (觸發動作)：**
- `When I query available slots for date "{date}" and staff "{name}"`
- `When I create a booking with start_at "{datetime}"`
- `When the user cancels booking "{booking_id}"`
- `When merchant "{slug}" subscription becomes "past_due"`

**Then (驗證結果)：**
- `Then I should see at least {count} available slot(s)`
- `Then I should not see any slot overlapping "{time_range}"`
- `Then booking status becomes "{status}"`
- `Then LINE sends a notification to user "{user_id}"`
- `Then API responds with status code {code} and reason "{reason}"`

---

## Ⅲ. BDD 範本（實際 Feature 檔案）

### 3.1 可訂時段查詢 (Available Slots)

**檔案名稱：** `features/bookable_slots.feature`

```gherkin
# Feature: 可訂時段查詢
# 目的: 客戶能夠查看特定日期、員工的可預約時段
# 對應 PRD: US-001

Feature: Query Bookable Slots

  Background:
    Given merchant "nail-abc" is active
    And merchant "nail-abc" has valid LINE credentials
    And merchant "nail-abc" subscription is "active"

  @happy-path @smoke-test
  Scenario: 客戶查看特定日期的可訂時段（無預約衝突）
    Given staff "Amy" is active with working hours on "2025-10-15" from "10:00" to "18:00"
    And service "Gel Basic" with duration 60 minutes exists
    And staff "Amy" can perform service "Gel Basic"
    And no existing bookings for staff "Amy" on "2025-10-15"
    When I query available slots for date "2025-10-15" and staff "Amy" and service "Gel Basic"
    Then I should see slots:
      | start_time | end_time |
      | 10:00      | 18:00    |
    And slot count should be at least 7

  @edge-case
  Scenario: 可訂時段需排除已佔檔區間
    Given staff "Amy" is active with working hours on "2025-10-15" from "10:00" to "18:00"
    And a booking exists from "2025-10-15T13:00+08:00" to "2025-10-15T14:30+08:00" for staff "Amy"
    When I query available slots for date "2025-10-15" and staff "Amy" and service "Gel Basic"
    Then I should not see any slot overlapping "13:00-14:30"
    And I should see at least one slot "10:00-11:00"
    And I should see at least one slot "15:00-16:00"

  @edge-case
  Scenario: 員工不在班時段不應出現
    Given staff "Amy" is active with working hours on "2025-10-15" from "14:00" to "20:00"
    When I query available slots for date "2025-10-15" and staff "Amy"
    Then I should not see any slot before "14:00"
    And I should not see any slot after "20:00"

  Scenario Outline: 不同服務時長影響可訂時段
    Given staff "Amy" is active with working hours on "2025-10-15" from "10:00" to "12:00"
    And service "<service_name>" with duration <duration> minutes exists
    When I query available slots for date "2025-10-15" and staff "Amy" and service "<service_name>"
    Then I should see approximately <expected_slots> available slot(s)

    Examples:
      | service_name | duration | expected_slots |
      | Quick Polish | 30       | 4              |
      | Gel Basic    | 60       | 2              |
      | Gel Deluxe   | 90       | 1              |
      | Full Set     | 120      | 1              |
```

---

### 3.2 建立預約 (Create Booking)

**檔案名稱：** `features/create_booking.feature`

```gherkin
# Feature: 建立預約
# 目的: 客戶透過 LIFF 建立預約，系統確保無衝突
# 對應 PRD: US-002

Feature: Create Booking

  Background:
    Given merchant "nail-abc" is active
    And merchant "nail-abc" subscription is "active"

  @critical @happy-path
  Scenario: 成功建立無衝突預約
    Given service "Gel Basic" with base_price 800 and duration 60 minutes
    And service option "French" with add_price 200 and duration 15 minutes for "Gel Basic"
    And staff "Amy" is active and can perform "Gel Basic"
    And staff "Amy" is working on "2025-10-16" from "10:00" to "18:00"
    And no existing booking overlaps "2025-10-16T10:00+08:00" to "2025-10-16T11:15+08:00" for "Amy"
    When I create a booking with:
      | field         | value                        |
      | merchant_slug | nail-abc                     |
      | customer      | {"line_user_id": "U123"}     |
      | staff_id      | 1                            |
      | start_at      | 2025-10-16T10:00:00+08:00    |
      | items         | [{"service_id":1,"option_ids":[1]}] |
    Then booking is created with status "confirmed"
    And booking total_price equals 1000
    And booking total_duration equals 75 minutes
    And a booking_lock exists for time range "2025-10-16T10:00+08:00" to "2025-10-16T11:15+08:00"
    And LINE notification is sent to user "U123"

  @critical @sad-path
  Scenario: 時段衝突應拒絕預約
    Given a confirmed booking exists:
      | staff_id | start_at                  | end_at                    |
      | 1        | 2025-10-16T10:00:00+08:00 | 2025-10-16T11:00:00+08:00 |
    When I create a booking with:
      | field         | value                     |
      | staff_id      | 1                         |
      | start_at      | 2025-10-16T10:30:00+08:00 |
      | service_ids   | [1]                       |
    Then API responds with status code 409
    And response contains error_code "booking_overlap"
    And no new booking_lock is created

  @edge-case
  Scenario: 商家訂閱逾期應拒絕新預約
    Given merchant "nail-abc" subscription is "past_due"
    When I create a booking for merchant "nail-abc"
    Then API responds with status code 403
    And response contains error_code "subscription_past_due"

  @edge-case
  Scenario: 員工停用應無法被預約
    Given staff "Amy" is inactive
    When I create a booking with staff "Amy"
    Then API responds with status code 400
    And response contains error_code "staff_inactive"
```

---

### 3.3 取消預約 (Cancel Booking)

**檔案名稱：** `features/cancel_booking.feature`

```gherkin
# Feature: 取消預約
# 目的: 客戶可在 LINE 中取消預約，釋放時段
# 對應 PRD: US-011

Feature: Cancel Booking

  @happy-path
  Scenario: 客戶成功取消已確認預約
    Given a confirmed booking "B123" exists for user "U1"
    And booking "B123" is scheduled for "2025-10-16T14:00+08:00"
    When the user "U1" cancels booking "B123"
    Then booking "B123" status becomes "cancelled"
    And the time slot is released for staff
    And LINE sends a cancellation confirmation to user "U1"
    And the cancelled_at timestamp is recorded

  @sad-path
  Scenario: 無法取消已完成的預約
    Given a completed booking "B456" exists for user "U1"
    When the user "U1" attempts to cancel booking "B456"
    Then API responds with status code 400
    And response contains error_code "cannot_cancel_completed"
    And booking "B456" status remains "completed"

  @edge-case
  Scenario: 僅預約擁有者可取消
    Given a confirmed booking "B789" exists for user "U1"
    When user "U2" attempts to cancel booking "B789"
    Then API responds with status code 403
    And response contains error_code "unauthorized_cancellation"
```

---

### 3.4 訂閱計費與降級 (Subscription Billing)

**檔案名稱：** `features/subscription_billing.feature`

```gherkin
# Feature: 訂閱計費與降級
# 目的: 商家訂閱逾期時限制功能
# 對應 PRD: US-005, Billing Context

Feature: Subscription Billing and Downgrade

  @critical
  Scenario: 訂閱逾期禁止新預約
    Given merchant "nail-abc" subscription is "past_due"
    When a LIFF user tries to create a booking for "nail-abc"
    Then API responds with status code 403
    And response contains reason "subscription_past_due"
    And existing bookings remain accessible

  @happy-path
  Scenario: 訂閱付款後恢復功能
    Given merchant "nail-abc" subscription is "past_due"
    When payment webhook confirms invoice "INV001" is paid
    Then merchant "nail-abc" subscription becomes "active"
    And merchant "nail-abc" can accept new bookings
    And a SubscriptionActivated event is published

  Scenario Outline: 訂閱狀態與功能限制
    Given merchant "nail-abc" subscription is "<status>"
    When checking feature availability for "<feature>"
    Then feature is "<availability>"

    Examples:
      | status    | feature         | availability |
      | active    | create_booking  | enabled      |
      | active    | view_calendar   | enabled      |
      | past_due  | create_booking  | disabled     |
      | past_due  | view_calendar   | enabled      |
      | cancelled | create_booking  | disabled     |
      | cancelled | view_calendar   | disabled     |
```

---

### 3.5 LINE 推播通知 (LINE Notifications)

**檔案名稱：** `features/line_notification.feature`

```gherkin
# Feature: LINE 推播通知
# 目的: 預約狀態變更時自動推播 LINE 訊息
# 對應 PRD: US-010

Feature: LINE Push Notifications

  Background:
    Given merchant "nail-abc" has valid LINE channel_access_token
    And LINE Messaging API is available

  @critical @happy-path
  Scenario: 預約確認後推播通知
    Given a booking is created successfully with id "B001"
    And booking "B001" belongs to user "U123"
    When the booking is confirmed
    Then a LINE push message is sent to user "U123" within 2 seconds
    And the message contains:
      | field         | value                         |
      | template_type | booking_confirmed             |
      | booking_id    | B001                          |
      | merchant_name | Nail ABC                      |
      | start_at      | 2025-10-16 14:00              |
      | staff_name    | Amy                           |
      | service_names | Gel Basic, French (add-on)    |
    And push_notification record is created with status "sent"

  @edge-case
  Scenario: LINE API 失敗時重試機制
    Given LINE Messaging API returns 429 (rate_limited)
    When attempting to send booking confirmation for "B002"
    Then the system retries up to 3 times with exponential backoff
    And if all retries fail, the notification status is "failed"
    And an alert is sent to operations team

  @sad-path
  Scenario: 無效 LINE token 應記錄錯誤
    Given merchant "nail-xyz" has invalid LINE credentials
    When attempting to send notification for a booking
    Then notification status is "failed"
    And error_reason is "invalid_channel_token"
    And merchant admin is notified to update credentials
```

---

## Ⅳ. 步驟定義骨架 (Step Definitions Scaffold)

### 4.1 Python/Behave 範例

```python
# features/steps/booking_steps.py

from behave import given, when, then
from datetime import datetime, timezone, timedelta
import requests

TZ = timezone(timedelta(hours=8))

@given('merchant "{slug}" is active')
def step_merchant_active(context, slug):
    context.merchant = create_test_merchant(slug=slug, status='active')

@given('staff "{name}" is active with working hours on "{date}" from "{start}" to "{end}"')
def step_staff_working_hours(context, name, date, start, end):
    context.staff = create_test_staff(
        name=name,
        is_active=True,
        merchant_id=context.merchant.id
    )
    create_working_hours(
        staff_id=context.staff.id,
        date=date,
        start_time=start,
        end_time=end
    )

@given('a booking exists from "{start_dt}" to "{end_dt}" for staff "{name}"')
def step_existing_booking(context, start_dt, end_dt, name):
    staff = get_staff_by_name(name)
    context.existing_booking = create_booking(
        merchant_id=context.merchant.id,
        staff_id=staff.id,
        start_at=parse_datetime(start_dt),
        end_at=parse_datetime(end_dt),
        status='confirmed'
    )

@when('I query available slots for date "{date}" and staff "{name}" and service "{service}"')
def step_query_slots(context, date, name, service):
    staff = get_staff_by_name(name)
    service_obj = get_service_by_name(service)
    
    response = requests.get(
        f"/public/merchants/{context.merchant.slug}/slots",
        params={
            'date': date,
            'staff_id': staff.id,
            'service_ids': [service_obj.id]
        }
    )
    context.response = response
    context.slots = response.json()['data']

@then('I should not see any slot overlapping "{time_range}"')
def step_no_overlap(context, time_range):
    start_str, end_str = time_range.split('-')
    for slot in context.slots:
        slot_start = parse_time(slot['start_time'])
        slot_end = parse_time(slot['end_time'])
        conflict_start = parse_time(start_str)
        conflict_end = parse_time(end_str)
        
        # Check no overlap
        assert not (slot_start < conflict_end and slot_end > conflict_start), \
            f"Slot {slot} overlaps with {time_range}"

@then('booking is created with status "{status}"')
def step_booking_created(context, status):
    assert context.response.status_code == 201
    booking = context.response.json()['data']
    assert booking['status'] == status
    context.booking_id = booking['id']

@then('a booking_lock exists for time range "{start}" to "{end}"')
def step_booking_lock_exists(context, start, end):
    lock = get_booking_lock(
        staff_id=context.staff.id,
        start_at=parse_datetime(start),
        end_at=parse_datetime(end)
    )
    assert lock is not None, "BookingLock not found"
```

---

## Ⅴ. 最佳實踐

### 5.1 Scenario 設計原則

1. **一個 Scenario 只測一件事：** 保持專注性
2. **使用業務語言：** 避免技術細節（如 SQL、HTTP）
3. **可重現性：** 每次執行結果一致
4. **獨立性：** Scenario 間不互相依賴

### 5.2 避免的反模式

**❌ 不好的範例：**
```gherkin
When I click the blue "Submit" button with id "btn-submit-123"
Then the database table "bookings" should have a new row
```

**✅ 好的範例：**
```gherkin
When I submit the booking request
Then a new booking is created
```

### 5.3 參數化與資料驅動

使用 `Scenario Outline` + `Examples` 避免重複：

```gherkin
Scenario Outline: 驗證不同服務價格計算
  Given service "<service>" with base_price <base> and option "<option>" with add_price <add>
  When I calculate total price
  Then total should be <expected>

  Examples:
    | service    | base | option  | add | expected |
    | Gel Basic  | 800  | French  | 200 | 1000     |
    | Gel Deluxe | 1200 | Artwork | 500 | 1700     |
```

---

## Ⅵ. 執行與整合

### 6.1 執行 BDD 測試

```bash
# 安裝 behave
pip install behave

# 執行所有 Feature
behave features/

# 執行特定 Feature
behave features/bookable_slots.feature

# 執行特定 Tag
behave --tags=critical
behave --tags=happy-path
```

### 6.2 CI/CD 整合

```yaml
# .github/workflows/bdd-tests.yml
name: BDD Tests

on: [push, pull_request]

jobs:
  bdd:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install behave
      - name: Run BDD tests
        run: behave features/ --format json --outfile bdd-results.json
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: bdd-results
          path: bdd-results.json
```

---

## Ⅶ. LLM Prompting Guide

**Prompt 範例：**
```
請根據以下的 BDD 情境，使用 DDD 和 TDD 方法，為我生成：
1. Booking 聚合的領域模型（Python Pydantic）
2. 對應的 Repository 介面
3. 一個初步的、會失敗的單元測試

BDD 情境如下：
[貼上 Gherkin Scenario 文本]
```

---

**記住：BDD 是溝通工具，不只是測試工具。讓業務、開發、測試說同一種語言。**


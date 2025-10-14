# 模組規格與測試案例 - Booking Service

---

**文件版本:** `v1.0`
**最後更新:** `2025-10-13`
**主要作者:** `後端開發工程師`
**審核者:** `技術負責人`
**狀態:** `開發中 (In Progress)`

---

## 模組: `BookingService`

**對應架構文件:** [05_architecture_and_design_document.md](./05_architecture_and_design_document.md#booking-context)
**對應 BDD Feature:** [features/create_booking.feature](../features/create_booking.feature)

---

## 規格 1: `create_booking`

### 描述 (Description)
建立新預約，確保無時段衝突、計算正確價格與時長、發送確認通知。

### 契約式設計 (Design by Contract)

#### 前置條件 (Preconditions):
1. `merchant_id` 對應的商家必須存在且狀態為 `active`
2. `merchant` 的訂閱狀態不可為 `past_due` 或 `cancelled`
3. `staff_id` 對應的員工必須存在、`is_active = true`、屬於該商家
4. `start_at` 必須為未來時間（> now）
5. 所有 `service_id` 必須存在、`is_active = true`、屬於該商家
6. 所有 `option_id` 必須存在、屬於對應的 service
7. `start_at` 必須在員工工作時間內
8. 時段不可與現有 `booking_locks` 重疊

#### 後置條件 (Postconditions):
1. 成功時返回 `Booking` 物件，`status = 'confirmed'`
2. `booking_locks` 表新增一筆記錄，範圍為 `[start_at, end_at)`
3. `bookings` 表新增一筆記錄
4. `booking_locks.booking_id` 指向新建立的 `booking.id`
5. 發布 `BookingConfirmed` 領域事件
6. 觸發 LINE 推播（異步）
7. 失敗時交易完全回滾，無殘留 lock

#### 不變性 (Invariants):
1. `total_price = Σ(service.base_price + Σ option.add_price)`
2. `total_duration = Σ(service.base_duration + Σ option.add_duration)`
3. `end_at = start_at + timedelta(minutes=total_duration)`
4. 同一 `(merchant_id, staff_id)` 的時間範圍不可重疊（由 EXCLUDE 約束保證）

---

## 測試情境與案例 (Test Scenarios & Cases)

### 情境 1: 正常路徑 (Happy Path)

#### TC-Booking-001: 成功建立單一服務預約

**描述：** 客戶選擇單一服務，無加購選項，時段無衝突。

**測試步驟 (Arrange-Act-Assert):**

1. **Arrange:**
   - 建立測試商家（active）
   - 建立測試員工（active，工時 10:00-18:00）
   - 建立測試服務（凝膠指甲，800元，60分鐘）
   - 確認該時段無現有預約

2. **Act:**
   ```python
   request = CreateBookingRequest(
       merchant_id=1,
       customer={"line_user_id": "U123", "name": "王小明"},
       staff_id=1,
       start_at=datetime(2025, 10, 16, 14, 0, tzinfo=TZ),
       items=[{"service_id": 1, "option_ids": []}]
   )
   
   booking = booking_service.create_booking(request)
   ```

3. **Assert:**
   - `booking.id` 不為 None
   - `booking.status == "confirmed"`
   - `booking.total_price.amount == 800`
   - `booking.total_duration.minutes == 60`
   - `booking.end_at == datetime(2025, 10, 16, 15, 0, tzinfo=TZ)`
   - 資料庫存在對應的 `booking_lock`
   - `BookingConfirmed` 事件已發布

---

#### TC-Booking-002: 建立含多個加購選項的預約

**描述：** 客戶選擇服務 + 2 個加購選項，價格與時長正確計算。

**測試步驟:**

1. **Arrange:**
   - 服務：凝膠指甲（800元，60分鐘）
   - 選項1：法式（200元，15分鐘）
   - 選項2：彩繪（300元，20分鐘）

2. **Act:**
   ```python
   request = CreateBookingRequest(
       items=[{
           "service_id": 1,
           "option_ids": [1, 2]
       }],
       # ... 其他欄位
   )
   
   booking = booking_service.create_booking(request)
   ```

3. **Assert:**
   - `booking.total_price.amount == 1300`  # 800 + 200 + 300
   - `booking.total_duration.minutes == 95`  # 60 + 15 + 20
   - `booking.end_at == start_at + timedelta(minutes=95)`

---

### 情境 2: 邊界情況 (Edge Cases)

#### TC-Booking-003: 邊界時段預約（貼著工時結束）

**描述：** 預約時段剛好在員工下班前結束。

**測試步驟:**

1. **Arrange:**
   - 員工工時：10:00-18:00
   - 服務時長：60分鐘

2. **Act:**
   - 預約時間：17:00-18:00

3. **Assert:**
   - 預約成功建立
   - `booking.end_at == datetime(..., 18, 0)`

---

#### TC-Booking-004: 多項服務堆疊

**描述：** 客戶同時預約 2 個服務（allow_stack=true）。

**測試步驟:**

1. **Arrange:**
   - 服務1：凝膠指甲（60分鐘）
   - 服務2：手部保養（45分鐘）

2. **Act:**
   ```python
   request = CreateBookingRequest(
       items=[
           {"service_id": 1, "option_ids": []},
           {"service_id": 2, "option_ids": []}
       ]
   )
   ```

3. **Assert:**
   - `booking.total_duration.minutes == 105`  # 60 + 45
   - `booking.items` 包含 2 個項目

---

### 情境 3: 無效輸入（違反前置條件）

#### TC-Booking-005: 時段重疊應拋出異常

**描述：** 嘗試預約已被佔用的時段。

**測試步驟:**

1. **Arrange:**
   - 已存在預約：Amy, 2025-10-16 14:00-15:00

2. **Act:**
   - 嘗試建立：Amy, 2025-10-16 14:30-15:30

3. **Assert:**
   - 拋出 `BookingOverlapError`
   - 錯誤訊息包含衝突資訊
   - 資料庫無新增任何記錄

---

#### TC-Booking-006: 商家停用應拋出異常

```python
def test_merchant_inactive_raises_error():
    # Arrange
    merchant = create_test_merchant(status='suspended')
    
    # Act & Assert
    with pytest.raises(MerchantInactiveError) as exc:
        booking_service.create_booking(
            CreateBookingRequest(merchant_id=merchant.id, ...)
        )
    
    assert "商家已停用" in str(exc.value)
```

---

#### TC-Booking-007: 員工停用應拋出異常

```python
def test_staff_inactive_raises_error():
    # Arrange
    staff = create_test_staff(is_active=False)
    
    # Act & Assert
    with pytest.raises(StaffInactiveError):
        booking_service.create_booking(
            CreateBookingRequest(staff_id=staff.id, ...)
        )
```

---

#### TC-Booking-008: 訂閱逾期應拒絕

```python
def test_subscription_past_due_rejects_booking():
    # Arrange
    merchant = create_test_merchant()
    create_subscription(merchant_id=merchant.id, status='past_due')
    
    # Act & Assert
    with pytest.raises(SubscriptionPastDueError) as exc:
        booking_service.create_booking(
            CreateBookingRequest(merchant_id=merchant.id, ...)
        )
    
    assert exc.value.status_code == 403
    assert exc.value.error_code == "subscription_past_due"
```

---

### 情境 4: 併發情境（整合測試）

#### TC-Booking-009: PostgreSQL EXCLUDE 約束防護

**描述：** 驗證資料庫層的 EXCLUDE 約束能防止併發寫入導致的重疊。

```python
import pytest
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ExclusionViolation
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_exclude_constraint_prevents_concurrent_overlap():
    """
    模擬 2 個客戶同時預約同一時段
    預期：其中一個成功，另一個因 EXCLUDE 約束失敗
    """
    
    # Arrange
    merchant_id = 1
    staff_id = 1
    start_at = datetime(2025, 10, 16, 14, 0, tzinfo=TZ)
    end_at = datetime(2025, 10, 16, 15, 0, tzinfo=TZ)
    
    def attempt_booking(customer_id):
        try:
            request = CreateBookingRequest(
                merchant_id=merchant_id,
                staff_id=staff_id,
                start_at=start_at,
                customer={"line_user_id": f"U{customer_id}"},
                items=[{"service_id": 1, "option_ids": []}]
            )
            return booking_service.create_booking(request)
        except BookingOverlapError as e:
            return e
    
    # Act: 並發執行 2 個預約
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(attempt_booking, i)
            for i in range(2)
        ]
        results = [future.result() for future in as_completed(futures)]
    
    # Assert
    successes = [r for r in results if isinstance(r, Booking)]
    failures = [r for r in results if isinstance(r, BookingOverlapError)]
    
    assert len(successes) == 1, "應該只有 1 個預約成功"
    assert len(failures) == 1, "應該有 1 個預約因重疊失敗"
    
    # 驗證資料庫只有 1 筆
    db_bookings = db.query(Booking).filter(
        Booking.staff_id == staff_id,
        Booking.start_at == start_at
    ).all()
    assert len(db_bookings) == 1
```

---

## 規格 2: `calculate_available_slots`

### 描述
計算特定員工、特定日期的所有可預約時段。

### 契約式設計

#### 前置條件:
1. `staff_id` 對應的員工必須存在
2. `date` 必須為有效日期
3. `service_duration_min > 0`

#### 後置條件:
1. 返回的所有時段長度 >= `service_duration_min`
2. 所有時段在員工工作時間內
3. 所有時段不與現有預約重疊

#### 不變性:
1. 返回的時段按時間排序
2. 時段之間不重疊

---

### 測試案例

#### TC-Slots-001: 無預約時返回完整工時切片

```python
def test_no_bookings_returns_full_day_slots():
    # Arrange
    staff = create_test_staff(id=1)
    create_working_hours(
        staff_id=1,
        day_of_week=2,  # Wednesday
        start_time=time(10, 0),
        end_time=time(18, 0)
    )
    
    # Act
    slots = calculate_available_slots(
        merchant_id=1,
        staff_id=1,
        target_date=date(2025, 10, 15),  # Wednesday
        service_duration_min=60,
        interval_min=30
    )
    
    # Assert
    assert len(slots) >= 15  # 8小時 / 30分鐘間隔
    assert slots[0]['start_time'] == "10:00"
    assert slots[-1]['end_time'] <= "18:00"
```

---

#### TC-Slots-002: 已訂時段應排除

```python
def test_occupied_slot_is_excluded():
    # Arrange
    create_booking(
        staff_id=1,
        start_at=datetime(2025, 10, 15, 13, 0, tzinfo=TZ),
        end_at=datetime(2025, 10, 15, 14, 30, tzinfo=TZ)
    )
    
    # Act
    slots = calculate_available_slots(
        staff_id=1,
        target_date=date(2025, 10, 15),
        service_duration_min=60
    )
    
    # Assert
    for slot in slots:
        slot_start = parse_time(slot['start_time'])
        slot_end = parse_time(slot['end_time'])
        
        # 確保不與 13:00-14:30 重疊
        assert not (
            slot_start < time(14, 30) and
            slot_end > time(13, 0)
        ), f"Slot {slot} overlaps with booked period"
```

---

#### TC-Slots-003: 時間複雜度驗證（效能測試）

```python
import time

def test_performance_with_many_bookings():
    """驗證在大量預約下的查詢效能"""
    
    # Arrange: 建立 100 筆歷史預約
    for i in range(100):
        create_booking(
            staff_id=1,
            start_at=datetime(2025, 10, 1 + i // 10, 10 + (i % 8), 0, tzinfo=TZ),
            end_at=datetime(2025, 10, 1 + i // 10, 11 + (i % 8), 0, tzinfo=TZ)
        )
    
    # Act
    start_time = time.time()
    slots = calculate_available_slots(
        staff_id=1,
        target_date=date(2025, 10, 16),
        service_duration_min=60
    )
    end_time = time.time()
    
    # Assert
    execution_time_ms = (end_time - start_time) * 1000
    assert execution_time_ms < 200, f"查詢時間 {execution_time_ms}ms 超過 200ms"
```

---

## 規格 3: `cancel_booking`

### 契約式設計

#### 前置條件:
1. `booking_id` 對應的預約必須存在
2. 預約狀態不可為 `completed` 或 `cancelled`
3. 請求者為預約擁有者（customer.line_user_id 一致）

#### 後置條件:
1. `booking.status = 'cancelled'`
2. `booking.cancelled_at` 被設定為當前時間
3. 發布 `BookingCancelled` 事件
4. 觸發取消通知

---

### 測試案例

#### TC-Cancel-001: 成功取消確認預約

```python
def test_cancel_confirmed_booking():
    # Arrange
    booking = create_booking(status='confirmed')
    
    # Act
    result = booking_service.cancel_booking(
        booking_id=booking.id,
        requester_line_id=booking.customer['line_user_id']
    )
    
    # Assert
    assert result.status == 'cancelled'
    assert result.cancelled_at is not None
    assert (datetime.utcnow() - result.cancelled_at).seconds < 5
```

---

#### TC-Cancel-002: 無法取消已完成預約

```python
def test_cannot_cancel_completed_booking():
    # Arrange
    booking = create_booking(status='completed')
    
    # Act & Assert
    with pytest.raises(InvalidStatusTransitionError) as exc:
        booking_service.cancel_booking(booking_id=booking.id)
    
    assert "無法取消已完成的預約" in str(exc.value)
    
    # 驗證狀態未變更
    db_booking = db.query(Booking).get(booking.id)
    assert db_booking.status == 'completed'
```

---

#### TC-Cancel-003: 僅擁有者可取消

```python
def test_only_owner_can_cancel():
    # Arrange
    booking = create_booking(customer={"line_user_id": "U111"})
    
    # Act & Assert
    with pytest.raises(PermissionDeniedError):
        booking_service.cancel_booking(
            booking_id=booking.id,
            requester_line_id="U222"  # 不同用戶
        )
```

---

## 規格 4: 值物件測試

### TC-Money-001: 金額加法

```python
from domain.value_objects import Money

def test_money_addition():
    m1 = Money(amount=Decimal("800"), currency="TWD")
    m2 = Money(amount=Decimal("200"), currency="TWD")
    
    result = m1 + m2
    
    assert result.amount == Decimal("1000")
    assert result.currency == "TWD"

def test_money_different_currency_raises():
    m1 = Money(amount=100, currency="TWD")
    m2 = Money(amount=10, currency="USD")
    
    with pytest.raises(ValueError, match="不同幣別"):
        m1 + m2
```

### TC-Duration-001: 時長加法

```python
from domain.value_objects import Duration

def test_duration_addition():
    d1 = Duration(minutes=60)
    d2 = Duration(minutes=15)
    
    result = d1 + d2
    
    assert result.minutes == 75
```

---

## 規格 5: 時間區間運算

### TC-TimeRange-001: 重疊檢測

```python
def test_overlaps_true():
    a_start = datetime(2025, 10, 16, 10, 0, tzinfo=TZ)
    a_end = datetime(2025, 10, 16, 11, 0, tzinfo=TZ)
    b_start = datetime(2025, 10, 16, 10, 30, tzinfo=TZ)
    b_end = datetime(2025, 10, 16, 11, 30, tzinfo=TZ)
    
    assert overlaps(a_start, a_end, b_start, b_end) is True

def test_overlaps_false_adjacent():
    a_start = datetime(2025, 10, 16, 10, 0, tzinfo=TZ)
    a_end = datetime(2025, 10, 16, 11, 0, tzinfo=TZ)
    b_start = datetime(2025, 10, 16, 11, 0, tzinfo=TZ)  # 緊鄰
    b_end = datetime(2025, 10, 16, 12, 0, tzinfo=TZ)
    
    assert overlaps(a_start, a_end, b_start, b_end) is False
```

---

## 測試覆蓋率目標

| 模組 | 目標覆蓋率 | 當前覆蓋率 | 狀態 |
|------|-----------|-----------|------|
| domain/models.py | 90% | 85% | 🔄 進行中 |
| domain/value_objects.py | 100% | 100% | ✅ 完成 |
| application/booking_service.py | 85% | 75% | 🔄 進行中 |
| infrastructure/repositories.py | 80% | 70% | 🔄 進行中 |

---

**LLM Prompting Guide:**

```
請根據以下測試案例規格，為我生成一個會失敗的 TDD 單元測試。

目標函式：BookingService.create_booking
測試案例 ID：TC-Booking-001
規格如下：[貼上測試案例文本]
```

---

**測試執行指令:**

```bash
# 執行所有單元測試
pytest tests/unit/booking/ -v

# 執行特定測試案例
pytest tests/unit/booking/test_booking_service.py::test_create_booking_success -v

# 生成覆蓋率報告
pytest --cov=src/booking --cov-report=html
```


# Code Review 與重構指南 - LINE 美甲預約系統

---

**文件版本:** `v1.0`
**最後更新:** `2025-10-13`
**狀態:** `活躍 (Active)`

---

## 🎯 專案特定 Code Review 重點

### 1. DDD 設計檢查

#### 1.1 聚合邊界
- [ ] 聚合根是否清晰？（Booking 為根）
- [ ] 不變式是否由聚合根保護？
- [ ] 是否避免跨聚合的直接引用？

**範例：**
```python
# ❌ 錯誤：直接引用其他聚合
class Booking:
    def __init__(self, staff: Staff):  # 不應直接持有 Staff 聚合
        self.staff = staff

# ✅ 正確：僅持有 ID
class Booking:
    def __init__(self, staff_id: int):
        self.staff_id = staff_id
```

#### 1.2 值物件不變性
- [ ] 值物件是否為 immutable？
- [ ] 相等性比較是否基於值？

```python
# ✅ 正確的值物件
from pydantic import BaseModel

class Money(BaseModel):
    amount: Decimal
    currency: str
    
    class Config:
        frozen = True  # 不可變
```

---

### 2. Repository Pattern 檢查

- [ ] Repository 介面是否定義在 Domain 層？
- [ ] 實作是否在 Infrastructure 層？
- [ ] 是否避免將 ORM 模型洩漏到 Domain？

```python
# ❌ 錯誤：在 Domain Service 中使用 ORM
from sqlalchemy.orm import Session

class BookingService:
    def create(self, db: Session):  # 不應依賴 SQLAlchemy
        db.add(...)

# ✅ 正確：依賴介面
class BookingService:
    def create(self, repo: BookingRepository):  # 依賴抽象
        repo.save(...)
```

---

### 3. API 設計檢查

- [ ] 端點是否遵循 RESTful 約定？
- [ ] 錯誤回應是否標準化？
- [ ] 是否正確使用 HTTP 狀態碼？

```python
# ✅ 正確的錯誤處理
from fastapi import HTTPException

@router.post("/bookings")
async def create_booking(request: CreateBookingRequest):
    try:
        booking = service.create_booking(request)
        return {"success": True, "data": booking}
    except BookingOverlapError as e:
        raise HTTPException(
            status_code=409,  # Conflict
            detail={
                "code": "booking_overlap",
                "message": str(e)
            }
        )
```

---

### 4. 測試覆蓋檢查

- [ ] 單元測試覆蓋率 > 80%？
- [ ] 是否測試不變式？
- [ ] 是否有整合測試驗證 EXCLUDE 約束？

**必測項目：**
```python
# 必須測試的不變式
def test_booking_invariants():
    # 1. 總價 = Σ(服務價 + 選項價)
    # 2. 總時長 = Σ(服務時長 + 選項時長)
    # 3. end_at = start_at + total_duration
    pass

# 必須測試的約束
def test_exclude_constraint():
    # 驗證 PostgreSQL EXCLUDE 防止重疊
    pass
```

---

## 🔄 重構策略

### 策略 1: 提取值物件

**Before:**
```python
class Booking:
    def calculate_total_price(self):
        total = 0
        for item in self.items:
            total += item['service_price']
            for opt in item['options']:
                total += opt['add_price']
        return total
```

**After:**
```python
class Booking:
    def calculate_total_price(self) -> Money:
        total = Money(amount=Decimal(0), currency="TWD")
        for item in self.items:
            total += item.total_price()
        return total

class BookingItem:
    def total_price(self) -> Money:
        total = self.service_price
        for opt_price in self.option_prices:
            total += opt_price
        return total
```

---

### 策略 2: 提取領域服務

**Before:**
```python
class BookingService:
    def create_booking(self, request):
        # 100 行程式碼...
        # 驗證、計算、儲存、發事件全在一起
```

**After:**
```python
class BookingService:
    def create_booking(self, request):
        self._validate_merchant(request.merchant_id)
        self._validate_staff(request.staff_id)
        
        booking = self._build_booking(request)
        booking.validate_invariants()
        
        self._create_lock_and_save(booking)
        self._publish_events(booking)
        
        return booking
    
    def _validate_merchant(self, merchant_id):
        # 專注於商家驗證
        pass
    
    def _build_booking(self, request) -> Booking:
        # 專注於建構預約物件
        pass
```

---

## 📋 Pull Request 模板

```markdown
## 🎯 變更摘要
簡要描述此 PR 的目的與變更內容

## 🏗️ 變更類型
- [ ] 新功能 (New Feature)
- [ ] Bug 修復 (Bug Fix)
- [ ] 重構 (Refactoring)
- [ ] 文檔更新 (Documentation)
- [ ] 效能優化 (Performance)

## 🧪 測試
- [ ] 單元測試通過
- [ ] 整合測試通過
- [ ] BDD Feature 測試通過
- [ ] 手動測試完成

## ✅ DDD/Clean Architecture 檢查清單
- [ ] 領域模型純淨（無框架依賴）
- [ ] Repository 介面在 Domain 層
- [ ] 依賴方向正確（Infrastructure → Application → Domain）
- [ ] 不變式有測試保護

## 📊 效能影響
- [ ] 無效能退化
- [ ] 若有新查詢，已建立適當索引
- [ ] 若有複雜運算，已進行效能測試

## 🔒 安全檢查
- [ ] 無 SQL Injection 風險
- [ ] 無敏感資訊洩漏
- [ ] 租戶隔離正確
```

---

## 🎯 Review Checklist

### Domain Layer Review
- [ ] 無 `import sqlalchemy`
- [ ] 無 `import fastapi`
- [ ] 所有類別有型別提示
- [ ] 值物件為 `frozen=True`

### Application Layer Review
- [ ] Use Case 職責單一
- [ ] 依賴注入正確
- [ ] 異常處理完整

### Infrastructure Layer Review
- [ ] ORM 模型與 Domain 模型分離
- [ ] 實作符合介面契約
- [ ] 資料庫查詢有索引支援

---

**Code Review 原則：嚴格但友善，聚焦設計與可維護性。**


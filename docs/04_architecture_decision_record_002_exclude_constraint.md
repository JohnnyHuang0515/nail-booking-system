# ADR-002: 使用 PostgreSQL EXCLUDE 約束防止預約重疊

---

**狀態 (Status):** `已接受 (Accepted)`
**決策者 (Deciders):** `技術負責人, DBA, 後端架構師`
**日期 (Date):** `2025-10-13`
**技術顧問 (Consulted):** `PostgreSQL 專家, QA Lead`
**受影響團隊 (Informed):** `後端開發團隊, 測試團隊`

---

## 1. 背景與問題陳述 (Context and Problem Statement)

### 上下文 (Context)
美甲預約系統的核心需求是**防止預約衝突**：同一位美甲師在同一時間只能服務一位客戶。這是業務的核心不變式。

### 問題陳述 (Problem Statement)
如何在高併發情況下（多個客戶同時預約同一時段），保證絕對不會出現重疊預約？

**量化問題嚴重性：**
- 若使用應用層邏輯檢查，在高併發下（每秒 10+ 預約）可能出現 Race Condition
- 預約衝突會直接導致客戶體驗極差，可能造成商家信譽損失
- 目標：預約衝突率 < 0.1%（理想為 0%）

### 驅動因素/約束條件
**驅動因素：**
1. 必須保證強一致性（CP，而非 AP）
2. 不能依賴分散式鎖（Redis SETNX）的可靠性
3. 需要在資料庫層面提供最後一道防線

**約束條件：**
1. 必須使用關聯式資料庫（已選定 PostgreSQL）
2. 不能大幅增加回應延遲（目標 P95 < 300ms）
3. 需要支援多租戶（merchant_id 隔離）

---

## 2. 考量的選項 (Considered Options)

### 選項一：應用層樂觀鎖 + 唯一索引

**描述：**
在應用層查詢是否重疊，使用版本號樂觀鎖，配合唯一索引防止衝突。

```python
# 應用層檢查
existing = db.query(Booking).filter(
    Booking.staff_id == staff_id,
    Booking.start_at < end_at,
    Booking.end_at > start_at
).first()

if existing:
    raise BookingOverlapError()

# 建立預約
booking = Booking(...)
db.add(booking)
db.commit()  # 可能因唯一索引失敗
```

**優點 (Pros)：**
- ✅ 實作簡單，容易理解
- ✅ 跨資料庫通用（MySQL, PostgreSQL）

**缺點 (Cons)：**
- ❌ **Race Condition：** 查詢與寫入之間存在時間窗口
- ❌ **無法防止邊界重疊：** 需要複雜的時間比較邏輯
- ❌ **需要分散式鎖：** 在多實例部署下需要 Redis SETNX（又引入新依賴）
- ❌ **測試困難：** 難以模擬高併發場景

**成本/複雜度評估：** 中（開發） / 高（維護）

---

### 選項二：PostgreSQL EXCLUDE USING gist（推薦）

**描述：**
使用 PostgreSQL 的 EXCLUDE 約束配合 GiST 索引，在資料庫層面保證時間區間不重疊。

```sql
ALTER TABLE booking_locks
  ADD CONSTRAINT no_overlap
  EXCLUDE USING gist (
    merchant_id WITH =,
    staff_id WITH =,
    tstzrange(start_at, end_at) WITH &&
  );
```

**語意：** 對於相同 merchant_id 和 staff_id，任何兩筆記錄的時間範圍（tstzrange）不可重疊（`&&` 運算子）。

**優點 (Pros)：**
- ✅ **絕對保證：** 資料庫層約束，無 Race Condition
- ✅ **原子性：** INSERT 失敗會拋出 `ExclusionViolation`，交易回滾
- ✅ **效能優異：** GiST 索引對範圍查詢優化良好
- ✅ **簡化應用層：** 不需要複雜的重疊檢查邏輯
- ✅ **多租戶原生支援：** merchant_id 條件自動隔離

**缺點 (Cons)：**
- ❌ **PostgreSQL 專屬：** 無法移植到其他資料庫
- ❌ **需要 GiST 擴展：** 預設未啟用，需要 `CREATE EXTENSION btree_gist;`
- ❌ **學習曲線：** 團隊需要理解 Range Types 和 GiST

**成本/複雜度評估：** 低（開發） / 低（維護）

---

### 選項三：分散式鎖（Redis SETNX）

**描述：**
使用 Redis 的 SETNX 指令建立分散式鎖，鎖定時段後再寫入資料庫。

```python
lock_key = f"booking_lock:{merchant_id}:{staff_id}:{start_at}:{end_at}"
acquired = redis.set(lock_key, "1", nx=True, ex=10)  # 10秒過期

if not acquired:
    raise BookingOverlapError()

try:
    # 建立預約
    booking = Booking(...)
    db.add(booking)
    db.commit()
finally:
    redis.delete(lock_key)
```

**優點 (Pros)：**
- ✅ 跨資料庫通用
- ✅ 效能優異（記憶體操作）

**缺點 (Cons)：**
- ❌ **單點故障：** Redis 故障會影響預約功能
- ❌ **鎖粒度難控制：** 時段切片問題複雜
- ❌ **增加依賴：** 系統複雜度上升
- ❌ **鎖過期問題：** 若交易超過過期時間，仍可能重疊

**成本/複雜度評估：** 高（開發） / 高（維護）

---

## 3. 決策 (Decision Outcome)

### 最終選擇的方案：
**選項二：PostgreSQL EXCLUDE USING gist**

### 選擇理由 (Rationale)

1. **根本性解決問題：**
   - 在資料庫層面保證不變式，而非依賴應用層邏輯
   - 符合「縮深防禦」原則：即使應用層有 bug，資料庫仍能防護

2. **簡化應用層設計：**
   ```python
   # 無需複雜的重疊檢查
   try:
       lock = BookingLock(...)
       db.add(lock)
       db.commit()
   except IntegrityError as e:
       if isinstance(e.orig, ExclusionViolation):
           raise BookingOverlapError()
   ```
   - 程式碼更簡潔、可讀性更高
   - 錯誤處理清晰明確

3. **效能驗證：**
   - 在 10,000 筆歷史預約下，INSERT 延遲 < 10ms
   - GiST 索引查詢效能優於應用層全掃描

4. **與 DDD 哲學契合：**
   - 不變式應由聚合根保護，資料庫約束是最後保障
   - 領域模型更純粹，不需混入鎖定邏輯

5. **長期維護性：**
   - 無需維護複雜的分散式鎖邏輯
   - 新人理解門檻低（SQL 約束直觀）

### 與其他選項的權衡：

**vs 樂觀鎖：**
- 犧牲跨資料庫相容性，換取絕對正確性
- 接受 PostgreSQL 綁定，因長期無遷移計劃

**vs 分散式鎖：**
- 犧牲理論上的極致效能，換取系統簡單性
- 避免引入額外依賴（Redis 作為關鍵路徑）

---

## 4. 決策的後果與影響 (Consequences)

### 正面影響：

1. **預約衝突率降至理論 0%：**
   - 資料庫層約束提供終極保證
   - 即使應用層有 bug，也不會造成衝突

2. **開發速度提升：**
   - 無需實作複雜的併發控制邏輯
   - 測試更簡單（直接驗證約束）

3. **降低技術債：**
   - 避免未來重構併發控制邏輯
   - 系統架構更清晰

### 負面影響：

1. **PostgreSQL 綁定：**
   - 未來若需遷移至其他資料庫，需重新設計
   - **可接受性：** 短中期無遷移計劃，長期可評估 CockroachDB（相容 PostgreSQL）

2. **需要專業知識：**
   - 團隊需要學習 Range Types 和 GiST
   - **緩解措施：** 建立內部文檔與培訓

3. **歷史資料清理：**
   - GiST 索引在千萬級資料下可能變慢
   - **緩解措施：** 定期歸檔舊預約（> 1 年）

### 對其他組件的影響：

- **Booking Service：** 需捕獲 ExclusionViolation 並轉為業務異常
- **QA 團隊：** 需建立併發測試案例驗證約束
- **DevOps：** 需監控 GiST 索引效能

---

## 5. 執行計畫 (Implementation Plan)

1. **Step 1：** 啟用 btree_gist 擴展
   ```sql
   CREATE EXTENSION IF NOT EXISTS btree_gist;
   ```

2. **Step 2：** 建立 booking_locks 表與 EXCLUDE 約束

3. **Step 3：** 撰寫整合測試驗證約束
   ```python
   def test_exclude_constraint_prevents_overlap():
       # 建立第一筆鎖定
       lock1 = BookingLock(staff_id=1, start_at=..., end_at=...)
       db.add(lock1)
       db.commit()
       
       # 嘗試建立重疊鎖定
       lock2 = BookingLock(staff_id=1, start_at=..., end_at=...)
       db.add(lock2)
       
       with pytest.raises(IntegrityError) as exc:
           db.commit()
       
       assert isinstance(exc.value.orig, ExclusionViolation)
   ```

4. **Step 4：** 修改 BookingService 捕獲異常

5. **Step 5：** 效能測試（模擬 100 TPS 併發預約）

6. **Step 6：** 建立監控與告警（追蹤 ExclusionViolation 頻率）

---

## 6. 相關參考 (References)

- [PostgreSQL Exclusion Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-EXCLUSION)
- [Range Types and GiST Indexes](https://www.postgresql.org/docs/current/rangetypes.html)
- [解決預約重疊問題的最佳實踐（2ndQuadrant Blog）](https://www.2ndquadrant.com/)
- 內部 PoC 結果：`docs/poc/exclude_constraint_benchmark.md`

---

## ADR 審核記錄:

| 日期       | 審核人     | 角色       | 備註/主要問題 |
| :--------- | :--------- | :--------- | :------------ |
| 2025-10-13 | 技術負責人 | 技術負責人 | 同意方案，已確認 EXCLUDE 可防止 Race Condition |
| 2025-10-13 | DBA | 資料庫管理員 | 建議加上 merchant_id 條件以支援多租戶 |
| 2025-10-13 | QA Lead | 測試主管 | 要求建立併發測試案例 |

# ADR-001: 選擇 PostgreSQL 作為主資料庫

---

**狀態 (Status):** `已接受 (Accepted)`
**決策者 (Deciders):** `技術負責人, 後端架構師, DBA`
**日期 (Date):** `2025-10-13`
**技術顧問 (Consulted):** `DevOps Team`
**受影響團隊 (Informed):** `前端團隊, QA 團隊`

---

## 1. 背景與問題陳述 (Context and Problem Statement)

### 上下文 (Context)
LINE 美甲預約系統需要一個可靠的關聯式資料庫來支援：
- 多租戶（Multi-tenant）資料隔離
- 強一致性的預約防衝突機制
- 複雜查詢（可訂時段計算、日曆檢視）
- 訂閱計費與帳單管理

### 問題陳述 (Problem Statement)
我們需要選擇一個資料庫系統，能夠：
1. **保證預約無重疊：** 透過資料庫層級約束防止同一員工同時間被預約兩次
2. **支援多租戶隔離：** Schema-level 或 Row-level 安全性
3. **高效能查詢：** 複雜的時間區間查詢與聚合
4. **成熟的生態：** 豐富的工具鏈與社群支援

### 驅動因素/約束條件 (Drivers / Constraints)
**驅動因素：**
- 預約系統對資料一致性要求極高（CAP 理論選擇 CP）
- 需要複雜的時間區間運算（範圍查詢、重疊檢測）
- 團隊對 SQL 資料庫有豐富經驗

**約束條件：**
- 初期預算有限，優先考慮開源方案
- 需支援 ACID 交易
- 必須有成熟的 Python ORM 支援（團隊使用 Python/FastAPI）
- 部署在 AWS/GCP 等雲平台

---

## 2. 考量的選項 (Considered Options)

### 選項一：PostgreSQL 14+

**描述：**
開源關聯式資料庫，強調標準相容性與擴展性。提供豐富的資料型別（如 `tstzrange`）與約束機制（如 `EXCLUDE USING gist`）。

**優點 (Pros)：**
- ✅ **EXCLUDE 約束：** 原生支援防止時間區間重疊（使用 GiST 索引）
- ✅ **時區支援：** `timestamptz` 與 `tstzrange` 完美處理跨時區場景
- ✅ **JSON 支援：** `jsonb` 型別適合儲存動態結構（如服務選項）
- ✅ **成熟的 ORM：** SQLAlchemy、Django ORM 完整支援
- ✅ **多租戶策略：** Row-Level Security (RLS) 或 Schema-per-Tenant
- ✅ **開源免費：** 無授權成本
- ✅ **雲端託管：** AWS RDS、GCP Cloud SQL 完整支援

**缺點 (Cons)：**
- ❌ 寫入效能略遜於 MySQL（對於極高 TPS 場景）
- ❌ 複雜查詢需要良好的索引設計
- ❌ 初學者學習曲線稍高

**成本/複雜度評估：**
- 開發成本：中（團隊需熟悉 EXCLUDE 等進階功能）
- 維護成本：低（成熟穩定）
- 基礎設施成本：中（AWS RDS 按需計費）

---

### 選項二：MySQL 8.0+

**描述：**
流行的開源關聯式資料庫，強調效能與易用性。

**優點 (Pros)：**
- ✅ 讀寫效能優異（尤其是簡單查詢）
- ✅ 社群龐大，資源豐富
- ✅ 雲端託管選擇多（AWS RDS、Azure Database）

**缺點 (Cons)：**
- ❌ **缺乏 EXCLUDE 約束：** 無法在資料庫層防止時間重疊，需在應用層實作（樂觀鎖 + 唯一索引）
- ❌ 時區處理較弱（無 `tstzrange` 等型別）
- ❌ JSON 功能不如 PostgreSQL jsonb
- ❌ 多租戶 RLS 支援不成熟

**成本/複雜度評估：**
- 開發成本：高（需自行實作重疊防護）
- 維護成本：中
- 基礎設施成本：中

---

### 選項三：MongoDB (NoSQL)

**描述：**
文件型 NoSQL 資料庫，強調彈性與水平擴展。

**優點 (Pros)：**
- ✅ Schema-free，適合快速迭代
- ✅ 水平擴展能力強

**缺點 (Cons)：**
- ❌ **無 ACID 跨文件交易：** 預約系統需要強一致性
- ❌ **無約束機制：** 無法在資料庫層防止重疊
- ❌ 複雜查詢效能不佳（如時間區間聚合）
- ❌ 團隊缺乏 NoSQL 經驗

**成本/複雜度評估：**
- 開發成本：極高（需重新學習 + 自行保證一致性）
- 維護成本：高
- 基礎設施成本：高（MongoDB Atlas 費用）

---

## 3. 決策 (Decision Outcome)

### 最終選擇的方案：
**選項一：PostgreSQL 14+**

### 選擇理由 (Rationale)

1. **技術契合度最高：**
   - **EXCLUDE 約束：** 完美解決預約重疊問題，無需在應用層實作複雜邏輯
   ```sql
   ALTER TABLE booking_locks
     ADD CONSTRAINT no_overlap
     EXCLUDE USING gist (
       merchant_id WITH =,
       staff_id WITH =,
       tstzrange(start_at, end_at) WITH &&
     );
   ```
   - 上述約束在資料庫層面保證：同一商家的同一員工，時間區間不可重疊

2. **多租戶支援：**
   - Row-Level Security (RLS) 可強制執行租戶隔離
   - Schema-per-Tenant 策略靈活性高

3. **時區處理：**
   - `timestamptz` 自動處理時區轉換
   - `tstzrange` 完美支援時間區間運算

4. **團隊熟悉度：**
   - 團隊已有 PostgreSQL + SQLAlchemy 經驗
   - 開發速度快，學習成本低

5. **成本效益：**
   - 開源免費，無授權費用
   - AWS RDS PostgreSQL 按需計費，初期成本可控

### 權衡分析 (Trade-off Analysis)

| 面向 | PostgreSQL | MySQL | MongoDB |
|------|-----------|-------|---------|
| **重疊防護** | ✅ DB 層約束 | ❌ 需應用層 | ❌ 需應用層 |
| **一致性** | ✅ ACID | ✅ ACID | ❌ 弱一致性 |
| **時區支援** | ✅ 原生 | ⚠️ 有限 | ❌ 無 |
| **多租戶** | ✅ RLS | ⚠️ 有限 | ⚠️ 需自建 |
| **團隊熟悉度** | ✅ 高 | ⚠️ 中 | ❌ 低 |
| **寫入效能** | ⚠️ 中 | ✅ 高 | ✅ 高 |

**結論：** 對於預約系統，資料一致性與約束能力遠比寫入效能重要，PostgreSQL 是最佳選擇。

---

## 4. 決策的後果與影響 (Consequences)

### 正面影響 / 預期收益：

1. **資料一致性保證：**
   - 預期可將預約衝突率降至 < 0.1%
   - 無需在應用層實作複雜的分散式鎖

2. **開發效率提升：**
   - 利用 PostgreSQL 豐富功能（jsonb、陣列、全文檢索）
   - SQLAlchemy ORM 成熟穩定

3. **運維成本降低：**
   - AWS RDS 提供自動備份、自動容錯移轉
   - 監控工具完善（CloudWatch、pg_stat_statements）

### 負面影響 / 引入的風險：

1. **寫入效能瓶頸（未來）：**
   - 若單一商家每秒預約量 > 100，可能需要分片（Sharding）
   - **緩解措施：** 初期使用 Read Replica 分流查詢，未來考慮 Citus 擴展

2. **EXCLUDE 約束效能：**
   - GiST 索引在大量資料下可能變慢
   - **緩解措施：** 定期清理歷史預約（歸檔策略）

3. **團隊深度：**
   - 需深入理解 EXCLUDE、RLS 等進階功能
   - **緩解措施：** 建立內部知識庫與最佳實踐文檔

### 對其他組件/團隊的影響：

- **前端團隊：** 無影響，透過 REST API 存取
- **DevOps：** 需學習 PostgreSQL 調校與監控
- **QA：** 需建立 EXCLUDE 約束的測試案例

### 未來可能需要重新評估的觸發條件：

1. **TPS > 1000：** 考慮引入 Citus（分散式 PostgreSQL）
2. **多地區部署：** 考慮 CockroachDB（相容 PostgreSQL，支援地理分散）
3. **成本壓力：** 考慮自建 PostgreSQL Cluster（節省雲端費用）

---

## 5. 執行計畫概要 (Implementation Plan Outline)

1. **Week 1：** 建立 AWS RDS PostgreSQL 14 實例（Multi-AZ 部署）
2. **Week 2：** 設計 Schema，實作 EXCLUDE 約束與 RLS 策略
3. **Week 3：** 整合 SQLAlchemy ORM，撰寫 Repository 層
4. **Week 4：** 效能測試與調校（索引優化、Query Plan 分析）
5. **Week 5：** 建立監控與告警（CloudWatch + pg_stat_statements）
6. **Week 6：** 建立備份與災難復原流程（PITR 測試）

---

## 6. 相關參考 (References)

- [PostgreSQL EXCLUDE Constraint 官方文檔](https://www.postgresql.org/docs/14/ddl-constraints.html#DDL-CONSTRAINTS-EXCLUSION)
- [PostgreSQL Range Types](https://www.postgresql.org/docs/14/rangetypes.html)
- [Row-Level Security (RLS) 指南](https://www.postgresql.org/docs/14/ddl-rowsecurity.html)
- [AWS RDS PostgreSQL 最佳實踐](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [SQLAlchemy PostgreSQL Dialect](https://docs.sqlalchemy.org/en/14/dialects/postgresql.html)

---

## ADR 審核記錄 (Review History):

| 日期       | 審核人     | 角色       | 備註/主要問題 |
| :--------- | :--------- | :--------- | :------------ |
| 2025-10-13 | 技術負責人 | 技術負責人 | 同意採用 PostgreSQL，已確認 EXCLUDE 約束可行性 |
| 2025-10-13 | DBA | 資料庫管理員 | 建議使用 RDS Multi-AZ 確保高可用性 |
| 2025-10-13 | DevOps Lead | DevOps | 同意方案，需建立監控與備份流程 |


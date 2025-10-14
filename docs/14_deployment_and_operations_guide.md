# 部署與運維指南 - LINE 美甲預約系統

---

**文件版本:** `v1.0`
**最後更新:** `2025-10-13`
**狀態:** `活躍 (Active)`

---

## 🏗️ 部署架構

### 環境策略

```
Development (本地) → Staging (AWS) → Production (AWS)
       ↓                ↓               ↓
   Docker Compose    ECS Fargate     ECS Fargate
   PostgreSQL 本地   RDS (t3.large)  RDS (r6g.xlarge Multi-AZ)
```

### 基礎設施組件

| 組件 | 技術 | 規格 | 用途 |
|------|------|------|------|
| **Load Balancer** | AWS ALB | - | HTTPS 終止、路由 |
| **Application** | ECS Fargate | 3 Tasks x 1vCPU/2GB | API 服務 |
| **Database** | RDS PostgreSQL 14 | r6g.xlarge Multi-AZ | 主資料庫 |
| **Cache** | ElastiCache Redis 7 | cache.r6g.large | 快取/佇列 |
| **Object Storage** | S3 | Standard | 上傳檔案 |
| **CDN** | CloudFront | - | 靜態資源 |
| **Monitoring** | Grafana + Prometheus | t3.medium | 監控視覺化 |

---

## 🔄 CI/CD Pipeline

### 後端 Pipeline

```yaml
# .github/workflows/backend-deploy.yml
name: Backend Deploy

on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest behave
      
      - name: Run linting
        run: |
          cd backend
          ruff check src/
          black --check src/
          mypy src/
      
      - name: Run unit tests
        run: |
          cd backend
          pytest tests/unit/ -v --cov=src --cov-report=xml
      
      - name: Run integration tests
        run: |
          cd backend
          docker-compose -f docker-compose.test.yml up -d
          pytest tests/integration/ -v
          docker-compose -f docker-compose.test.yml down
      
      - name: Run BDD tests
        run: |
          cd backend
          behave features/ --format json --outfile bdd-results.json
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-1
      
      - name: Login to ECR
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push image
        run: |
          cd backend
          docker build -t nailbook-api:${{ github.sha }} .
          docker tag nailbook-api:${{ github.sha }} $ECR_REPO:latest
          docker tag nailbook-api:${{ github.sha }} $ECR_REPO:${{ github.sha }}
          docker push $ECR_REPO:latest
          docker push $ECR_REPO:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster nailbook-prod \
            --service api \
            --force-new-deployment \
            --region ap-northeast-1
      
      - name: Wait for deployment
        run: |
          aws ecs wait services-stable \
            --cluster nailbook-prod \
            --services api \
            --region ap-northeast-1
      
      - name: Smoke tests
        run: |
          curl -f https://api.nailbook.com/health || exit 1
      
      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "✅ Backend deployed successfully to production"
            }
```

---

## 📋 部署檢查清單

### Pre-Deployment

- [x] Code review 完成且批准
- [x] 所有測試通過（Unit + Integration + BDD）
- [x] 安全掃描通過（Snyk, OWASP ZAP）
- [x] 效能測試達標（Locust）
- [x] 資料庫遷移腳本已準備
- [x] Runbook 已更新
- [x] 監控告警已配置
- [x] 團隊通知已發送

### During Deployment

- [ ] 監控部署進度（ECS Console）
- [ ] 驗證健康檢查（/health 端點）
- [ ] 檢查應用日誌（CloudWatch Logs）
- [ ] 驗證關鍵功能（Smoke Tests）
- [ ] 監控系統指標（Grafana）

### Post-Deployment

- [ ] Smoke tests 執行成功
- [ ] 效能指標正常（P95 < 300ms）
- [ ] 錯誤率正常（< 0.1%）
- [ ] 資料庫連線正常
- [ ] LINE 推播功能正常
- [ ] 前端三端可正常存取

---

## 🔧 部署策略：Blue-Green

### 流程

```bash
# 1. 部署 Green 環境
aws ecs create-service \
  --cluster nailbook-prod \
  --service-name api-green \
  --task-definition api:latest \
  --desired-count 3 \
  --load-balancers targetGroupArn=$GREEN_TG_ARN,containerName=api,containerPort=8000

# 2. 驗證 Green 環境健康
curl https://green.api.nailbook.com/health

# 3. 執行 Smoke Tests
pytest tests/smoke/ --base-url=https://green.api.nailbook.com

# 4. 切換流量（ALB Target Group）
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,TargetGroupArn=$GREEN_TG_ARN

# 5. 監控 15 分鐘
watch -n 10 'aws cloudwatch get-metric-statistics ...'

# 6. 若正常，縮減 Blue 環境
aws ecs update-service --service api-blue --desired-count 0

# 7. 若異常，快速切回 Blue
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,TargetGroupArn=$BLUE_TG_ARN
```

---

## 📊 監控與告警

### 關鍵指標

#### Application Metrics

```python
# Prometheus 指標暴露
from prometheus_client import Counter, Histogram

booking_created = Counter(
    'booking_created_total',
    'Total bookings created',
    ['merchant_id', 'status']
)

booking_duration = Histogram(
    'booking_creation_duration_seconds',
    'Time to create a booking',
    buckets=[0.1, 0.2, 0.3, 0.5, 1.0, 2.0]
)

# 使用
with booking_duration.time():
    booking = service.create_booking(request)
    booking_created.labels(
        merchant_id=request.merchant_id,
        status='success'
    ).inc()
```

#### Grafana Dashboard

**Panel 1: Booking Success Rate**
```promql
sum(rate(booking_created_total{status="success"}[5m]))
/
sum(rate(booking_created_total[5m]))
* 100
```

**Panel 2: P95 Latency**
```promql
histogram_quantile(0.95, 
  sum(rate(booking_creation_duration_seconds_bucket[5m])) by (le)
)
```

**Panel 3: Overlap Error Rate**
```promql
sum(rate(booking_created_total{status="overlap_error"}[5m]))
/
sum(rate(booking_created_total[5m]))
* 100
```

### Alert Rules

```yaml
# alerts.yml
groups:
  - name: booking
    interval: 30s
    rules:
      - alert: HighBookingErrorRate
        expr: |
          sum(rate(booking_created_total{status!="success"}[5m]))
          /
          sum(rate(booking_created_total[5m]))
          > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "預約錯誤率過高"
          description: "過去 5 分鐘預約錯誤率 > 5%"
      
      - alert: HighP95Latency
        expr: |
          histogram_quantile(0.95,
            sum(rate(booking_creation_duration_seconds_bucket[5m])) by (le)
          ) > 0.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "預約建立延遲過高"
          description: "P95 延遲 > 500ms"
      
      - alert: DatabaseConnectionPoolExhausted
        expr: |
          sqlalchemy_pool_size - sqlalchemy_pool_checkedout < 5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "資料庫連線池即將耗盡"
```

---

## 🔄 回滾程序

### 自動回滾觸發條件

- 錯誤率 > 10%（連續 5 分鐘）
- P95 延遲 > 1 秒（連續 10 分鐘）
- 健康檢查失敗率 > 50%

### 手動回滾步驟

```bash
# 1. 識別最後可用版本
aws ecs list-task-definitions --family-prefix api --sort DESC

# 2. 切換至前一版本
aws ecs update-service \
  --cluster nailbook-prod \
  --service api \
  --task-definition api:N-1 \
  --force-new-deployment

# 3. 驗證回滾成功
aws ecs wait services-stable --cluster nailbook-prod --service api

# 4. 監控應用健康
watch -n 5 'curl -s https://api.nailbook.com/health | jq'

# 5. 回滾資料庫遷移（若需要）
cd backend
alembic downgrade -1

# 6. 通知團隊
slack-notify "#engineering" "⚠️ Rolled back to version N-1"
```

---

## 🛠️ Runbook（操作手冊）

### 常見問題與處理

#### 問題 1: 預約衝突率突增

**症狀：**
- CloudWatch 顯示 `booking_overlap` 錯誤增加
- Grafana 顯示衝突率 > 1%

**診斷步驟：**
```bash
# 1. 檢查 PostgreSQL EXCLUDE 約束是否存在
psql -h $DB_HOST -U postgres -d nailbook -c "
  SELECT conname, contype
  FROM pg_constraint
  WHERE conname = 'no_overlap_bookings';
"

# 2. 檢查是否有大量併發請求
SELECT merchant_id, staff_id, COUNT(*)
FROM booking_locks
WHERE created_at > NOW() - INTERVAL '10 minutes'
GROUP BY merchant_id, staff_id
HAVING COUNT(*) > 10;

# 3. 檢查應用層是否繞過 Lock 機制
grep -r "INSERT INTO bookings" backend/src/
```

**解決方案：**
- 若約束遺失：立即重新建立
- 若併發過高：增加 ECS Task 數量
- 若程式碼繞過：立即回滾並修復

---

#### 問題 2: LINE 推播失敗率高

**症狀：**
- notification_logs 顯示大量 `status=failed`
- 客戶回報未收到通知

**診斷步驟：**
```bash
# 1. 檢查 LINE API 回應
SELECT error_reason, COUNT(*)
FROM notification_logs
WHERE status = 'failed'
  AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY error_reason;

# 2. 驗證 LINE Token 有效性
curl -H "Authorization: Bearer $LINE_TOKEN" \
  https://api.line.me/v2/bot/info

# 3. 檢查速率限制
# LINE Messaging API 限制：500 msg/sec
```

**解決方案：**
- 若 Token 過期：更新商家 LINE 憑證
- 若速率限制：實作批次推播與 Queue
- 若 API 故障：啟用重試機制（已實作）

---

## 🔐 機密管理

### AWS Secrets Manager

```bash
# 建立 Secret
aws secretsmanager create-secret \
  --name nailbook/database \
  --secret-string '{
    "username":"postgres",
    "password":"xxx",
    "host":"nailbook-prod.xxx.rds.amazonaws.com",
    "port":5432,
    "database":"nailbook"
  }'

# 建立 LINE Secret
aws secretsmanager create-secret \
  --name nailbook/line \
  --secret-string '{
    "channel_secret":"xxx",
    "channel_access_token":"xxx"
  }'

# 在 ECS Task Definition 中引用
{
  "secrets": [
    {
      "name": "DATABASE_URL",
      "valueFrom": "arn:aws:secretsmanager:region:account:secret:nailbook/database"
    }
  ]
}
```

---

## 📝 資料庫維護

### 定期任務

#### 每日備份驗證

```bash
# 驗證 RDS 自動備份
aws rds describe-db-snapshots \
  --db-instance-identifier nailbook-prod \
  --snapshot-type automated \
  --max-records 1

# 測試 PITR（每月演練）
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier nailbook-prod \
  --target-db-instance-identifier nailbook-pitr-test \
  --restore-time 2025-10-13T10:00:00Z
```

#### 每週清理歷史資料

```sql
-- 歸檔 1 年前的已完成預約
INSERT INTO bookings_archive
SELECT * FROM bookings
WHERE status = 'completed'
  AND completed_at < NOW() - INTERVAL '1 year';

DELETE FROM bookings
WHERE status = 'completed'
  AND completed_at < NOW() - INTERVAL '1 year';

-- 清理舊的 booking_locks（已關聯預約）
DELETE FROM booking_locks
WHERE created_at < NOW() - INTERVAL '7 days'
  AND booking_id IS NOT NULL;

-- 清理孤立的 locks（無關聯預約，可能是失敗交易）
DELETE FROM booking_locks
WHERE created_at < NOW() - INTERVAL '1 day'
  AND booking_id IS NULL;
```

#### 每月索引維護

```bash
# 連線至 RDS
psql $DATABASE_URL

# 重建索引（避免膨脹）
REINDEX TABLE CONCURRENTLY bookings;
REINDEX TABLE CONCURRENTLY booking_locks;

# 更新統計資訊
ANALYZE bookings;
ANALYZE booking_locks;

# 檢查索引使用率
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC
LIMIT 10;
```

---

## 🔍 故障排查

### 常見故障處理

#### 資料庫連線池耗盡

**症狀：**
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 20 overflow 10 reached
```

**緊急處理：**
```python
# 1. 臨時增加連線池大小
engine = create_engine(
    DATABASE_URL,
    pool_size=30,  # 從 20 增加
    max_overflow=20  # 從 10 增加
)

# 2. 檢查是否有慢查詢
SELECT pid, age(clock_timestamp(), query_start), usename, query 
FROM pg_stat_activity 
WHERE state != 'idle' 
  AND query NOT ILIKE '%pg_stat_activity%' 
ORDER BY query_start;

# 3. 終止長時間查詢
SELECT pg_terminate_backend(pid);
```

#### EXCLUDE 約束效能下降

**症狀：** 預約建立延遲 > 500ms

**診斷：**
```sql
-- 檢查 GiST 索引大小
SELECT schemaname, tablename, indexname, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes
WHERE indexname LIKE '%gist%';

-- 檢查索引膨脹
SELECT * FROM pgstattuple('idx_booking_locks_gist');

-- 若 dead_tuple_percent > 20%，重建索引
REINDEX INDEX CONCURRENTLY idx_booking_locks_gist;
```

---

## 🚀 擴展策略

### 垂直擴展（短期）

**當前：** db.r6g.xlarge (4 vCPU, 32GB)
**升級路徑：**
1. db.r6g.2xlarge (8 vCPU, 64GB) - 支援 500 TPS
2. db.r6g.4xlarge (16 vCPU, 128GB) - 支援 1000 TPS

### 水平擴展（長期）

**Read Replica（優先）：**
```bash
aws rds create-db-instance-read-replica \
  --db-instance-identifier nailbook-prod-replica-1 \
  --source-db-instance-identifier nailbook-prod \
  --availability-zone ap-northeast-1c
```

**應用層配置：**
```python
# 讀寫分離
PRIMARY_DB = create_engine(PRIMARY_URL)
REPLICA_DB = create_engine(REPLICA_URL)

def get_db(readonly=False):
    return REPLICA_DB if readonly else PRIMARY_DB

# 使用
@router.get("/bookings")
def list_bookings(db: Session = Depends(lambda: get_db(readonly=True))):
    # 使用 Replica 查詢
    pass
```

**Sharding（未來）：**
- 按 `merchant_id` 分片
- 使用 Citus 擴展（相容 PostgreSQL）

---

## 📞 On-call 指南

### Incident Response

**Severity 定義：**
- **P0 (Critical)：** 服務完全中斷，影響所有用戶
- **P1 (High)：** 核心功能異常，影響 > 50% 用戶
- **P2 (Medium)：** 部分功能異常，有替代方案
- **P3 (Low)：** 小問題，不影響核心流程

**P0 處理流程：**
1. **0-5 min：** 確認問題範圍與影響
2. **5-15 min：** 嘗試快速修復或回滾
3. **15-30 min：** 召集團隊進行根因分析
4. **30+ min：** 實施永久修復

**聯絡清單：**
- **Backend On-call：** +886-XXX-XXXX
- **DevOps On-call：** +886-XXX-XXXX
- **Tech Lead：** +886-XXX-XXXX

---

**維護者：** DevOps Team
**最後演練：** 2025-10-10（Blue-Green 部署演練）
**下次演練：** 2025-11-10（災難恢復演練）


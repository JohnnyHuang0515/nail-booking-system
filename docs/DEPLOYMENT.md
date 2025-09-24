# 部署指南

美甲預約系統的部署指南，包含開發環境、測試環境和生產環境的部署說明。

## 🏗️ 系統架構

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   客戶端 LIFF   │    │   管理後台      │    │   後端 API      │
│   (React)       │    │   (React)       │    │   (FastAPI)     │
│   Port: 3001    │    │   Port: 3000    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   Port: 5432     │
                    └─────────────────┘
```

## 🚀 快速部署

### 使用 Docker Compose (推薦)

1. **創建 docker-compose.yml**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: nail_booking_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/nail_booking_db
    depends_on:
      - postgres

  admin-panel:
    build: ./admin-panel
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8000/api/v1

  customer-liff:
    build: ./customer-liff
    ports:
      - "3001:3001"
    environment:
      REACT_APP_API_URL: http://localhost:8000/api/v1

volumes:
  postgres_data:
```

2. **啟動服務**
```bash
docker-compose up -d
```

## 🛠️ 手動部署

### 1. 環境準備

#### 系統要求
- Python 3.10+
- Node.js 16+
- PostgreSQL 13+
- Docker (可選)

#### 安裝依賴
```bash
# Python 依賴
pip install -r requirements.txt

# 前端依賴
cd admin-panel && npm install
cd ../customer-liff && npm install
```

### 2. 資料庫設置

#### 使用 Docker (推薦)
```bash
# 啟動 PostgreSQL
docker run -d \
  --name nail-postgres \
  -e POSTGRES_DB=nail_booking_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15

# 創建資料庫表
export DATABASE_URL="postgresql://postgres:password@localhost:5432/nail_booking_db"
python create_tables.py
```

#### 本地 PostgreSQL
```bash
# 安裝 PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# 創建資料庫
sudo -u postgres createdb nail_booking_db
sudo -u postgres createuser nail_user

# 設置密碼
sudo -u postgres psql
ALTER USER nail_user PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE nail_booking_db TO nail_user;

# 創建表
export DATABASE_URL="postgresql://nail_user:your_password@localhost:5432/nail_booking_db"
python create_tables.py
```

### 3. 後端部署

#### 開發環境
```bash
# 設置環境變數
export DATABASE_URL="postgresql://postgres:password@localhost:5432/nail_booking_db"

# 啟動後端服務
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 生產環境
```bash
# 使用 Gunicorn
pip install gunicorn

# 啟動服務
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 使用 systemd (Linux)
```bash
# 創建服務文件
sudo nano /etc/systemd/system/nail-booking.service

[Unit]
Description=Nail Booking System API
After=network.target

[Service]
Type=exec
User=www-data
WorkingDirectory=/path/to/nail-booking-system
Environment=DATABASE_URL=postgresql://postgres:password@localhost:5432/nail_booking_db
ExecStart=/path/to/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target

# 啟動服務
sudo systemctl enable nail-booking
sudo systemctl start nail-booking
```

### 4. 前端部署

#### 開發環境
```bash
# 管理後台
cd admin-panel
npm start

# 客戶端 LIFF
cd customer-liff
npm start
```

#### 生產環境
```bash
# 構建生產版本
cd admin-panel
npm run build

cd ../customer-liff
npm run build

# 使用 Nginx 服務靜態文件
sudo nano /etc/nginx/sites-available/nail-booking

server {
    listen 80;
    server_name your-domain.com;

    # 管理後台
    location /admin {
        root /path/to/admin-panel/build;
        try_files $uri $uri/ /index.html;
    }

    # 客戶端 LIFF
    location / {
        root /path/to/customer-liff/build;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 啟用站點
sudo ln -s /etc/nginx/sites-available/nail-booking /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 安全配置

### 1. 環境變數
```bash
# 創建 .env 文件
DATABASE_URL=postgresql://user:password@localhost:5432/nail_booking_db
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost
```

### 2. HTTPS 配置
```bash
# 使用 Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. 防火牆設置
```bash
# UFW 防火牆
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## 📊 監控與日誌

### 1. 日誌配置
```python
# logging.conf
[loggers]
keys=root,app

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_app]
level=INFO
handlers=fileHandler
qualname=app
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=simpleFormatter
args=('app.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### 2. 健康檢查
```bash
# 創建健康檢查腳本
#!/bin/bash
curl -f http://localhost:8000/ || exit 1
curl -f http://localhost:3000/ || exit 1
curl -f http://localhost:3001/ || exit 1
```

## 🔄 備份與恢復

### 1. 資料庫備份
```bash
# 備份
pg_dump -h localhost -U postgres nail_booking_db > backup_$(date +%Y%m%d).sql

# 恢復
psql -h localhost -U postgres nail_booking_db < backup_20250101.sql
```

### 2. 自動備份腳本
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U postgres nail_booking_db > /backups/backup_$DATE.sql
find /backups -name "backup_*.sql" -mtime +7 -delete
```

## 🚨 故障排除

### 常見問題

#### 1. 資料庫連接失敗
```bash
# 檢查 PostgreSQL 狀態
sudo systemctl status postgresql

# 檢查連接
psql -h localhost -U postgres -d nail_booking_db
```

#### 2. 端口衝突
```bash
# 檢查端口使用
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000
netstat -tulpn | grep :3001
```

#### 3. 權限問題
```bash
# 檢查文件權限
ls -la /path/to/nail-booking-system
chmod +x start.sh stop.sh
```

## 📈 性能優化

### 1. 資料庫優化
```sql
-- 創建索引
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_user ON appointments(user_id);
CREATE INDEX idx_appointments_service ON appointments(service_id);
```

### 2. 緩存配置
```python
# Redis 緩存 (可選)
pip install redis
```

### 3. 負載均衡
```nginx
# Nginx 負載均衡
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

## 🔧 維護任務

### 定期維護
- 資料庫備份
- 日誌清理
- 依賴更新
- 安全補丁

### 監控指標
- API 響應時間
- 資料庫連接數
- 記憶體使用率
- 磁碟空間

---

**部署完成後，請確保所有服務正常運行並進行功能測試！**

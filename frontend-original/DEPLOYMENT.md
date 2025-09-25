# 美甲預約系統 - 部署指南

## 應用架構

系統已拆分為三個獨立部分：

```
frontend/
├── admin-panel/          # 管理後台應用
├── customer-booking/      # 客戶預約應用
└── shared/               # 共用組件庫
```

## 部署建議

### 1. 管理後台 (admin-panel)
- **域名**: `admin.yourdomain.com`
- **用途**: 美甲師和管理員使用
- **安全性**: 建議設置登入驗證

### 2. 客戶預約 (customer-booking)
- **域名**: `yourdomain.com` 或 `booking.yourdomain.com`
- **用途**: 客戶預約美甲服務
- **優化**: 針對手機端優化

### 3. 共用組件庫 (shared)
- **用途**: 兩個應用共用
- **維護**: 更新時需同步到兩個應用

## 部署步驟

### 管理後台
```bash
cd frontend/admin-panel
npm install
npm run build
# 部署 build/ 目錄到 admin.yourdomain.com
```

### 客戶預約
```bash
cd frontend/customer-booking
npm install
npm run build
# 部署 build/ 目錄到 yourdomain.com
```

## 開發環境

### 同時開發兩個應用
```bash
# 終端 1: 管理後台
cd frontend/admin-panel && npm start

# 終端 2: 客戶預約
cd frontend/customer-booking && npm start
```

## 注意事項

1. 兩個應用使用相同的共用組件庫
2. 更新共用組件時需同步到兩個應用
3. 建議使用不同的端口進行開發 (3000, 3001)
4. 生產環境建議使用不同的域名或子域名

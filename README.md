# 美甲預約系統

這是一個完整的美甲預約系統，包含管理後台和客戶預約頁面兩個獨立的前端應用。

## 項目結構

```
美甲預約系統/
├── admin-panel/          # 管理後台 (端口 3000)
├── customer-booking/      # 客戶預約頁面 (端口 3001)
├── frontend/             # 原始統一前端 (已拆分)
└── package.json          # 根目錄配置
```

## 功能說明

### 管理後台 (admin-panel)
- **端口**: 3000
- **功能**: 
  - 儀表板
  - 行事曆管理
  - 預約管理
  - 時段管理
  - 服務管理
  - 顧客管理

### 客戶預約頁面 (customer-booking)
- **端口**: 3001
- **功能**:
  - 日期選擇
  - 時段選擇
  - 服務選擇
  - 預約確認
  - 預約成功頁面

## 安裝和運行

### 1. 安裝所有依賴
```bash
npm run install:all
```

### 2. 運行應用

#### 同時運行兩個應用
```bash
npm start
```

#### 分別運行
```bash
# 運行管理後台 (端口 3000)
npm run start:admin

# 運行客戶預約頁面 (端口 3001)
npm run start:customer
```

### 3. 構建應用
```bash
# 構建所有應用
npm run build

# 分別構建
npm run build:admin
npm run build:customer
```

## 訪問地址

- 管理後台: http://localhost:3000
- 客戶預約: http://localhost:3001

## 技術棧

- React 18
- TypeScript
- Tailwind CSS
- Radix UI
- Lucide React Icons

## 開發說明

每個應用都是獨立的React應用，可以單獨開發和部署。共享的UI組件位於各自的 `src/components/ui/` 目錄中。
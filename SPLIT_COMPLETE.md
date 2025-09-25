# 美甲預約系統拆分完成

## 拆分結果

已成功將前端拆分為兩個獨立的應用：

### 1. 管理後台 (admin-panel)
- **位置**: `/home/johnny/專案/美甲預約系統/admin-panel/`
- **端口**: 3000
- **功能**: 儀表板、行事曆管理、預約管理、時段管理、服務管理、顧客管理

### 2. 客戶預約頁面 (customer-booking)
- **位置**: `/home/johnny/專案/美甲預約系統/customer-booking/`
- **端口**: 3001
- **功能**: 日期選擇、時段選擇、服務選擇、預約確認、預約成功頁面

## 文件結構

```
美甲預約系統/
├── admin-panel/          # 管理後台應用
│   ├── src/
│   │   ├── components/
│   │   │   ├── admin/     # 管理後台組件
│   │   │   ├── ui/        # 共享UI組件
│   │   │   └── Navigation.tsx
│   │   └── App.tsx        # 管理後台主應用
│   ├── public/
│   └── package.json       # 配置端口3000
├── customer-booking/      # 客戶預約應用
│   ├── src/
│   │   ├── components/
│   │   │   ├── customer/  # 客戶預約組件
│   │   │   └── ui/        # 共享UI組件
│   │   └── App.tsx        # 客戶預約主應用
│   ├── public/
│   └── package.json       # 配置端口3001
├── frontend/              # 原始統一前端（保留）
├── package.json           # 根目錄配置
├── start.sh              # 啟動腳本
└── README.md             # 說明文檔
```

## 啟動方式

### 方法1: 使用根目錄腳本
```bash
# 同時啟動兩個應用
npm start

# 分別啟動
npm run start:admin    # 管理後台 (3000)
npm run start:customer # 客戶預約 (3001)
```

### 方法2: 使用啟動腳本
```bash
./start.sh
```

### 方法3: 分別啟動
```bash
# 管理後台
cd admin-panel && npm start

# 客戶預約
cd customer-booking && npm start
```

## 訪問地址

- 管理後台: http://localhost:3000
- 客戶預約: http://localhost:3001

## 注意事項

1. 每個應用都是獨立的React應用，可以單獨開發和部署
2. 共享的UI組件已複製到各自的應用中
3. 原始前端保留在 `frontend/` 目錄中作為備份
4. 兩個應用使用相同的設計系統和樣式

## 技術棧

- React 18
- TypeScript
- Tailwind CSS
- Radix UI
- Lucide React Icons

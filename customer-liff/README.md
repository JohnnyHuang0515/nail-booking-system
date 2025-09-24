# 美甲預約系統 - 顧客端 LIFF 介面

這是美甲預約系統的顧客端介面，基於 LINE LIFF (LINE Front-end Framework) 開發，提供顧客一個簡單直覺的預約體驗。

## 🚀 功能特色

- **📱 響應式設計**: 專為行動裝置優化
- **💅 美甲主題**: 溫柔奶茶色系，營造溫馨氛圍
- **🔄 流暢預約流程**: 4步驟完成預約
- **📅 即時時段查詢**: 動態顯示可用時段
- **✅ 預約確認**: 完整的預約摘要和確認流程
- **🔗 LINE 整合**: 無縫整合 LINE 生態系統

## 📋 預約流程

1. **選擇日期** - 選擇希望的預約日期
2. **選擇時段** - 從可用時段中選擇
3. **選擇服務** - 選擇想要的服務項目
4. **確認預約** - 確認預約資訊並提交

## 🛠️ 技術棧

- **前端框架**: React 18 + TypeScript
- **UI 框架**: React Bootstrap
- **路由**: React Router DOM
- **狀態管理**: React Context + useReducer
- **API 串接**: Axios
- **LIFF SDK**: @line/liff
- **樣式**: CSS3 + Bootstrap

## 📦 安裝與運行

### 1. 安裝依賴

```bash
npm install
```

### 2. 環境變數設置

複製環境變數範例文件：

```bash
cp env.example .env
```

編輯 `.env` 文件，設置正確的 LIFF ID：

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_LIFF_ID=your-actual-liff-id
REACT_APP_NAME=美甲預約系統
REACT_APP_DEBUG=true
```

### 3. 啟動開發服務器

```bash
npm start
```

應用程式將在 `http://localhost:3000` 啟動。

## 🔧 開發說明

### 專案結構

```
src/
├── components/          # 共用組件
│   └── BookingContext.tsx  # 預約流程狀態管理
├── pages/              # 頁面組件
│   ├── DateSelectionPage.tsx    # 日期選擇頁面
│   ├── TimeSelectionPage.tsx    # 時段選擇頁面
│   ├── ServiceSelectionPage.tsx  # 服務選擇頁面
│   ├── ConfirmationPage.tsx      # 預約確認頁面
│   └── SuccessPage.tsx          # 成功頁面
├── services/           # API 服務
│   └── api.ts         # API 接口定義
├── types/             # TypeScript 類型定義
│   └── index.ts       # 共用類型
├── utils/             # 工具函數
│   └── liff.ts        # LIFF 服務封裝
├── styles/            # 樣式文件
│   └── index.css      # 主要樣式
├── App.tsx            # 主應用組件
└── index.tsx          # 應用入口
```

### 狀態管理

使用 React Context + useReducer 管理預約流程狀態：

```typescript
interface BookingState {
  selectedDate: string | null;
  selectedTime: string | null;
  selectedService: Service | null;
  user: User | null;
  isLoading: boolean;
  error: string | null;
}
```

### API 接口

主要 API 接口：

- `userAPI.loginWithLine()` - LINE 用戶登入
- `serviceAPI.getServices()` - 取得服務列表
- `appointmentAPI.getAvailableSlots()` - 取得可用時段
- `appointmentAPI.createAppointment()` - 創建預約

## 🎨 設計風格

### 色彩搭配

- **主色**: `#FFB6C1` (淺粉紅)
- **次色**: `#B0E0E6` (淺藍)
- **強調色**: `#F5E6D3` (溫柔奶茶色)
- **成功色**: `#98FB98` (薄荷綠)
- **文字色**: `#8B6F47` (溫暖棕色)

### 視覺效果

- **玻璃擬態**: 半透明卡片背景
- **漸層背景**: 多層次圓形漸層
- **柔和陰影**: 溫和的陰影效果
- **圓角設計**: 16px 圓角營造親和感
- **動畫效果**: 平滑的過渡動畫

## 📱 LINE LIFF 設置

### 1. 創建 LIFF 應用

1. 登入 [LINE Developers Console](https://developers.line.biz/)
2. 選擇或創建 Provider
3. 創建新的 Channel
4. 在 LIFF 標籤中創建新的 LIFF 應用

### 2. LIFF 設置

- **LIFF URL**: `https://your-domain.com`
- **Size**: Full
- **Endpoint URL**: `https://your-domain.com`
- **Scope**: profile, openid

### 3. 獲取 LIFF ID

在 LIFF 應用設置頁面獲取 LIFF ID，並設置到環境變數中。

## 🚀 部署

### 1. 建構應用

```bash
npm run build
```

### 2. 部署到靜態託管服務

推薦使用：
- Vercel
- Netlify
- GitHub Pages
- Firebase Hosting

### 3. 設置 HTTPS

LIFF 應用需要 HTTPS 環境，確保部署的網站支援 SSL。

## 🔍 測試

### 開發環境測試

1. 使用 LINE 開發者工具測試
2. 在 LINE 應用中開啟 LIFF 視窗
3. 測試完整的預約流程

### 生產環境測試

1. 部署到 HTTPS 環境
2. 更新 LIFF 設置中的 URL
3. 在實際 LINE 應用中測試

## 📞 支援

如有問題或建議，請聯繫開發團隊。

## 📄 授權

本專案採用 MIT 授權條款。
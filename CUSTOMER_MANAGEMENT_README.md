# 顧客消費紀錄管理功能

## 功能概述

店家管理後台現在支援查看和管理會員的消費紀錄，提供完整的顧客管理功能。

## 主要功能

### 1. 顧客管理頁面 (`/customers`)
- **顧客列表**：顯示所有註冊顧客
- **搜尋功能**：可依姓名或電話搜尋顧客
- **消費統計**：顯示每個顧客的消費次數和總金額
- **消費紀錄**：選擇顧客後查看其詳細消費紀錄

### 2. 消費紀錄管理
- **新增消費紀錄**：手動新增顧客的消費記錄
- **編輯消費紀錄**：修改現有的消費紀錄
- **刪除消費紀錄**：移除不需要的消費紀錄
- **關聯預約**：可選擇性關聯到特定預約

### 3. 資料顯示
- **消費日期**：顯示交易建立時間
- **金額**：顯示消費金額
- **關聯預約**：顯示相關的預約日期和時間
- **服務項目**：顯示相關的服務名稱
- **備註**：顯示額外的備註資訊

## 後端 API 端點

### 交易管理
- `GET /api/v1/transactions` - 獲取所有交易
- `GET /api/v1/transactions/{id}` - 獲取特定交易
- `POST /api/v1/transactions` - 創建新交易
- `PUT /api/v1/transactions/{id}` - 更新交易
- `DELETE /api/v1/transactions/{id}` - 刪除交易

### 用戶交易
- `GET /api/v1/users/{user_id}/transactions` - 獲取特定用戶的交易

## 使用方式

### 1. 查看顧客消費紀錄
1. 登入店家管理後台
2. 點擊左側選單的「顧客管理」
3. 在左側顧客列表中選擇要查看的顧客
4. 右側會顯示該顧客的所有消費紀錄

### 2. 新增消費紀錄
1. 在顧客管理頁面選擇顧客
2. 點擊「新增消費紀錄」按鈕
3. 填寫消費金額和備註
4. 可選擇性關聯到特定預約
5. 點擊「新增」完成

### 3. 編輯消費紀錄
1. 在消費紀錄表格中點擊「編輯」圖示
2. 修改金額或備註
3. 點擊「更新」完成

### 4. 刪除消費紀錄
1. 在消費紀錄表格中點擊「刪除」圖示
2. 確認刪除操作

## 技術實作

### 後端架構
- **領域模型**：`Transaction` 領域模型
- **儲存庫**：`SqlTransactionRepository` 實作
- **服務層**：`TransactionService` 業務邏輯
- **API 端點**：RESTful API 設計

### 前端架構
- **頁面元件**：`Customers` 主頁面
- **表格元件**：`TransactionsTable` 顯示交易列表
- **表單元件**：`TransactionFormDialog` 新增/編輯交易
- **API 客戶端**：`transactionsAPI` 處理 API 呼叫

## 資料庫結構

### transactions 表
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    appointment_id UUID REFERENCES appointments(id) ON DELETE SET NULL,
    amount NUMERIC(10, 2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 測試

執行測試腳本驗證 API 功能：
```bash
python test_transactions_api.py
```

## 注意事項

1. **權限控制**：目前所有功能都開放給管理員使用
2. **資料驗證**：前端和後端都有資料驗證
3. **錯誤處理**：提供友善的錯誤訊息
4. **響應式設計**：支援不同螢幕尺寸
5. **資料一致性**：確保交易資料的完整性

## 未來擴展

- 消費統計圖表
- 匯出消費報表
- 消費趨勢分析
- 會員等級管理
- 積分系統整合

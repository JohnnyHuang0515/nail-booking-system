# LIFF 前端整合指南

## 概述

本指南說明如何將現有的 LIFF 前端應用與多商家美甲預約系統的後端 API 整合。

## 前端整合要點

### 1. 身分對應機制

#### 前端實現
```javascript
// 取得 LINE 用戶資料
const profile = await liff.getProfile();
const userId = profile.userId;

// 取得 idToken
const idToken = liff.getIDToken();

// 發送 API 請求時帶上 merchant_id
const response = await fetch('/api/v1/users/liff-login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        id_token: idToken,
        access_token: liff.getAccessToken(), // 可選
        merchant_id: 'merchant_uuid_here'
    })
});
```

#### 後端處理
- 使用 `LIFFAuthManager` 驗證 `idToken`
- 確保 `UNIQUE(merchant_id, line_user_id)` 約束
- 自動創建或更新用戶記錄

### 2. 多商家 LIFF ID 管理

#### 商家設定
```javascript
// 每個商家需要設定獨立的 LIFF ID
const merchantConfig = {
    merchant_id: 'merchant_uuid',
    liff_id: 'liff_app_id_for_this_merchant',
    line_channel_id: 'channel_id_for_this_merchant'
};
```

#### 前端啟動
```javascript
// 根據 URL 參數或配置決定使用哪個 LIFF ID
const urlParams = new URLSearchParams(window.location.search);
const merchantId = urlParams.get('merchant_id');
const liffId = getLiffIdForMerchant(merchantId);

// 初始化 LIFF
liff.init({ liffId: liffId })
    .then(() => {
        if (liff.isLoggedIn()) {
            // 用戶已登入，進行身分驗證
            authenticateUser(merchantId);
        } else {
            // 引導用戶登入
            liff.login();
        }
    });
```

### 3. 安全驗證流程

#### 完整的驗證流程
```javascript
async function authenticateUser(merchantId) {
    try {
        // 1. 取得 LINE 用戶資料和 token
        const profile = await liff.getProfile();
        const idToken = liff.getIDToken();
        const accessToken = liff.getAccessToken();
        
        // 2. 向後端驗證身分
        const response = await fetch(`/api/v1/users/liff-login?merchant_id=${merchantId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id_token: idToken,
                access_token: accessToken
            })
        });
        
        if (response.ok) {
            const userData = await response.json();
            // 3. 設定用戶上下文
            setUserContext(userData);
            // 4. 進入主應用
            initializeApp(userData);
        } else {
            throw new Error('身分驗證失敗');
        }
    } catch (error) {
        console.error('認證錯誤:', error);
        // 處理認證失敗
        handleAuthError(error);
    }
}
```

### 4. UI/UX 建議實現

#### 日期時段選擇器
```javascript
// 建議使用日曆組件 + 時段格子
import { Calendar } from './components/Calendar';
import { TimeSlotGrid } from './components/TimeSlotGrid';

function BookingForm({ merchantId, serviceId }) {
    const [selectedDate, setSelectedDate] = useState(null);
    const [selectedTime, setSelectedTime] = useState(null);
    const [availableSlots, setAvailableSlots] = useState([]);
    
    // 載入可用時段
    useEffect(() => {
        if (selectedDate) {
            loadAvailableSlots(merchantId, serviceId, selectedDate);
        }
    }, [selectedDate]);
    
    return (
        <div className="booking-form">
            <Calendar 
                selectedDate={selectedDate}
                onDateSelect={setSelectedDate}
                minDate={new Date()}
            />
            <TimeSlotGrid 
                slots={availableSlots}
                selectedTime={selectedTime}
                onTimeSelect={setSelectedTime}
            />
        </div>
    );
}
```

#### 成功預約後處理
```javascript
async function confirmBooking(bookingData) {
    try {
        // 1. 提交預約
        const response = await fetch('/api/v1/appointments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${userToken}`
            },
            body: JSON.stringify({
                ...bookingData,
                merchant_id: merchantId
            })
        });
        
        if (response.ok) {
            const appointment = await response.json();
            
            // 2. 跳轉回 LINE 聊天
            liff.closeWindow();
            
            // 3. 後端會自動推送 Flex Message 確認卡片
            // (這個由 LINE Webhook 系統處理)
        }
    } catch (error) {
        console.error('預約失敗:', error);
    }
}
```

### 5. API 整合範例

#### 服務列表
```javascript
async function loadServices(merchantId) {
    const response = await fetch(`/api/v1/services?merchant_id=${merchantId}`);
    const services = await response.json();
    return services;
}
```

#### 可用時段查詢
```javascript
async function loadAvailableSlots(merchantId, serviceId, date) {
    const response = await fetch(
        `/api/v1/booking/available-slots?merchant_id=${merchantId}&service_id=${serviceId}&date=${date}`
    );
    const slots = await response.json();
    return slots;
}
```

#### 預約提交
```javascript
async function createAppointment(merchantId, appointmentData) {
    const response = await fetch('/api/v1/appointments', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            merchant_id: merchantId,
            ...appointmentData
        })
    });
    
    return response.json();
}
```

### 6. 錯誤處理

#### 身分驗證錯誤
```javascript
function handleAuthError(error) {
    if (error.message.includes('LIFF 驗證失敗')) {
        // 重新初始化 LIFF
        liff.init({ liffId: liffId });
    } else if (error.message.includes('找不到商家')) {
        // 顯示錯誤訊息並提供聯絡方式
        showError('找不到指定的商家，請檢查連結是否正確');
    }
}
```

#### 網路錯誤處理
```javascript
async function apiCall(url, options) {
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '請求失敗');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API 調用失敗:', error);
        // 顯示用戶友好的錯誤訊息
        showError('網路連線異常，請稍後再試');
        throw error;
    }
}
```

### 7. 部署配置

#### 環境變數
```javascript
// .env
const config = {
    API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 'https://your-api-domain.com',
    DEFAULT_MERCHANT_ID: process.env.REACT_APP_DEFAULT_MERCHANT_ID,
    ENVIRONMENT: process.env.NODE_ENV
};
```

#### LIFF ID 配置
```javascript
// config/merchants.js
const merchantConfigs = {
    'merchant-uuid-1': {
        liffId: 'liff-app-id-1',
        name: '台北美甲店'
    },
    'merchant-uuid-2': {
        liffId: 'liff-app-id-2',
        name: '高雄美甲店'
    }
};

function getLiffIdForMerchant(merchantId) {
    return merchantConfigs[merchantId]?.liffId;
}
```

### 8. 測試建議

#### 單元測試
```javascript
// 測試身分驗證
describe('LIFF Authentication', () => {
    it('should authenticate user with valid idToken', async () => {
        const mockProfile = { userId: 'test-user-id' };
        const mockIdToken = 'valid-id-token';
        
        // Mock LIFF API
        jest.spyOn(liff, 'getProfile').mockResolvedValue(mockProfile);
        jest.spyOn(liff, 'getIDToken').mockReturnValue(mockIdToken);
        
        // Test authentication
        const result = await authenticateUser('test-merchant-id');
        expect(result).toBeDefined();
    });
});
```

#### 整合測試
```javascript
// 測試完整預約流程
describe('Booking Flow', () => {
    it('should complete booking process', async () => {
        // 1. 模擬用戶登入
        await mockUserLogin();
        
        // 2. 載入服務列表
        const services = await loadServices('test-merchant-id');
        expect(services.length).toBeGreaterThan(0);
        
        // 3. 選擇服務和時段
        const selectedService = services[0];
        const availableSlots = await loadAvailableSlots('test-merchant-id', selectedService.id, '2024-01-15');
        
        // 4. 提交預約
        const appointment = await createAppointment('test-merchant-id', {
            service_id: selectedService.id,
            appointment_date: '2024-01-15',
            appointment_time: '14:00'
        });
        
        expect(appointment.id).toBeDefined();
    });
});
```

## 總結

這個整合指南提供了：

✅ **完整的身分驗證流程**：使用 LIFF idToken 確保安全  
✅ **多商家支援**：每個商家獨立的 LIFF ID 和配置  
✅ **用戶友好的 UI/UX**：日曆和時段選擇器  
✅ **錯誤處理機制**：完善的錯誤處理和用戶提示  
✅ **測試策略**：單元測試和整合測試建議  

前端應用現在可以安全地與後端 API 整合，實現完整的多商家美甲預約系統功能。

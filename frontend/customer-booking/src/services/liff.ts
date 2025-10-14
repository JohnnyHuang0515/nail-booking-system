// LINE LIFF 服務
interface LineProfile {
  userId: string;
  displayName: string;
  pictureUrl?: string;
  statusMessage?: string;
}

interface LiffUser {
  userId: string;
  displayName: string;
  pictureUrl?: string;
  statusMessage?: string;
}

interface MerchantContext {
  merchant_id: string;
  merchant_name: string;
  liff_id: string;
  timezone: string;
  is_active: boolean;
}

class LiffService {
  private isInitialized = false;
  private userProfile: LineProfile | null = null;
  private merchantContext: MerchantContext | null = null;

  async initialize(): Promise<boolean> {
    try {
      // 檢查是否在 LIFF 環境中
      if (typeof window !== 'undefined' && (window as any).liff) {
        const liff = (window as any).liff;
        
        // 先嘗試從 URL 參數獲取 merchant_id，如果沒有則使用正確的商家 ID
        const urlParams = new URLSearchParams(window.location.search);
        const merchantId = urlParams.get('merchant_id') || '00000000-0000-0000-0000-000000000001';
        
        // 獲取商家上下文
        await this.loadMerchantContext(merchantId);
        
        // 使用商家的 LIFF ID 初始化，如果沒有則使用測試 ID
        const liffId = this.merchantContext?.liff_id || 'test-liff-id';
        await liff.init({ liffId });
        this.isInitialized = true;

        // 檢查是否已登入
        if (liff.isLoggedIn()) {
          // 取得用戶資料
          const profile = await liff.getProfile();
          this.userProfile = {
            userId: profile.userId,
            displayName: profile.displayName,
            pictureUrl: profile.pictureUrl,
            statusMessage: profile.statusMessage
          };
          return true;
        } else {
          // 如果未登入，嘗試登入
          liff.login();
          return false;
        }
      } else {
        // 非 LIFF 環境，仍然嘗試獲取商家上下文
        const urlParams = new URLSearchParams(window.location.search);
        const merchantId = urlParams.get('merchant_id') || '00000000-0000-0000-0000-000000000001';
        await this.loadMerchantContext(merchantId);
        
        console.log('非 LIFF 環境');
        this.isInitialized = true;
        return false;
      }
    } catch (error) {
      console.error('LIFF 初始化失敗:', error);
      this.isInitialized = true;
      return false;
    }
  }

  getUserProfile(): LineProfile | null {
    return this.userProfile;
  }

  getMerchantContext(): MerchantContext | null {
    return this.merchantContext;
  }

  isLiffReady(): boolean {
    return this.isInitialized;
  }

  private async loadMerchantContext(merchantId: string): Promise<void> {
    try {
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/v1/merchant-context/${merchantId}`);
      
      if (response.ok) {
        this.merchantContext = await response.json();
        console.log('商家上下文已載入:', this.merchantContext);
      } else {
        console.error('載入商家上下文失敗:', response.status);
        // 使用預設的商家上下文
        this.merchantContext = {
          merchant_id: merchantId,
          merchant_name: '測試商家',
          liff_id: 'test-liff-id',
          timezone: 'Asia/Taipei',
          is_active: true
        };
      }
    } catch (error) {
      console.error('載入商家上下文異常:', error);
      // 使用預設的商家上下文
      this.merchantContext = {
        merchant_id: merchantId,
        merchant_name: '測試商家',
        liff_id: 'test-liff-id',
        timezone: 'Asia/Taipei',
        is_active: true
      };
    }
  }

  async getAccessToken(): Promise<string | null> {
    try {
      if (typeof window !== 'undefined' && (window as any).liff && this.isInitialized) {
        const liff = (window as any).liff;
        return await liff.getAccessToken();
      }
      return null;
    } catch (error) {
      console.error('取得 Access Token 失敗:', error);
      return null;
    }
  }

  async getIdToken(): Promise<string | null> {
    try {
      if (typeof window !== 'undefined' && (window as any).liff && this.isInitialized) {
        const liff = (window as any).liff;
        return await liff.getIDToken();
      }
      return null;
    } catch (error) {
      console.error('取得 ID Token 失敗:', error);
      return null;
    }
  }

  async closeWindow(): Promise<void> {
    try {
      if (typeof window !== 'undefined' && (window as any).liff && this.isInitialized) {
        const liff = (window as any).liff;
        liff.closeWindow();
      }
    } catch (error) {
      console.error('關閉視窗失敗:', error);
    }
  }

  // 取得用戶的聯絡資訊（基於 LINE 資料推測）
  getUserContactInfo(): {
    name: string;
    phone: string;
    email: string;
  } {
    if (this.userProfile) {
      return {
        name: this.userProfile.displayName,
        phone: '', // LINE 不提供電話號碼
        email: ''  // LINE 不提供電子郵件
      };
    }
    
    return {
      name: '',
      phone: '',
      email: ''
    };
  }
}

export const liffService = new LiffService();
export default liffService;

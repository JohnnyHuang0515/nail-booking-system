import liff from '@line/liff';
import { LiffProfile } from '../types';

class LiffService {
  private isInitialized = false;

  // 初始化 LIFF
  async init(): Promise<void> {
    if (this.isInitialized) return;

    try {
      const liffId = process.env.REACT_APP_LIFF_ID;
      
      // 如果沒有設置 LIFF ID 或使用預設值，跳過 LIFF 初始化
      if (!liffId || liffId === 'your-liff-id-here') {
        console.log('LIFF ID not configured, running in development mode');
        this.isInitialized = true;
        return;
      }

      await liff.init({ liffId });
      this.isInitialized = true;
      console.log('LIFF initialized successfully');
    } catch (error) {
      console.error('LIFF initialization failed:', error);
      // 在開發環境中，即使 LIFF 初始化失敗也繼續運行
      console.log('Continuing in development mode without LIFF');
      this.isInitialized = true;
    }
  }

  // 檢查是否在 LINE 環境中
  isInLineClient(): boolean {
    return liff.isInClient();
  }

  // 取得用戶資料
  async getProfile(): Promise<LiffProfile> {
    if (!this.isInitialized) {
      await this.init();
    }

    // 如果沒有配置 LIFF ID，返回模擬資料
    const liffId = process.env.REACT_APP_LIFF_ID;
    if (!liffId || liffId === 'your-liff-id-here') {
      return {
        userId: 'dev-user-123',
        displayName: '開發測試用戶',
        pictureUrl: undefined,
        statusMessage: '開發模式',
      };
    }

    try {
      const profile = await liff.getProfile();
      return {
        userId: profile.userId,
        displayName: profile.displayName,
        pictureUrl: profile.pictureUrl,
        statusMessage: profile.statusMessage,
      };
    } catch (error) {
      console.error('Failed to get profile:', error);
      // 返回模擬資料作為後備
      return {
        userId: 'fallback-user-456',
        displayName: '測試用戶',
        pictureUrl: undefined,
        statusMessage: '後備模式',
      };
    }
  }

  // 關閉 LIFF 視窗
  closeWindow(): void {
    const liffId = process.env.REACT_APP_LIFF_ID;
    if (!liffId || liffId === 'your-liff-id-here') {
      console.log('Development mode: Cannot close LIFF window');
      return;
    }

    if (liff.isInClient()) {
      liff.closeWindow();
    }
  }

  // 開啟外部瀏覽器
  openWindow(url: string): void {
    liff.openWindow({
      url: url,
      external: true,
    });
  }

  // 分享訊息
  async shareTargetPicker(messages: any[]): Promise<void> {
    if (liff.isApiAvailable('shareTargetPicker')) {
      await liff.shareTargetPicker(messages);
    } else {
      console.log('shareTargetPicker is not available');
    }
  }
}

export const liffService = new LiffService();
export default liffService;

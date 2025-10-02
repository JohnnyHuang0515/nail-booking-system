// 本地儲存服務
interface UserProfile {
  name: string;
  phone: string;
  email: string;
  lastUsed: string; // ISO date string
}

class StorageService {
  private readonly STORAGE_KEY = 'nail_booking_user_profile';

  // 儲存用戶資料
  saveUserProfile(profile: Omit<UserProfile, 'lastUsed'>): void {
    try {
      const userProfile: UserProfile = {
        ...profile,
        lastUsed: new Date().toISOString()
      };
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(userProfile));
      console.log('用戶資料已儲存:', userProfile);
    } catch (error) {
      console.error('儲存用戶資料失敗:', error);
    }
  }

  // 取得用戶資料
  getUserProfile(): UserProfile | null {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        const profile = JSON.parse(stored) as UserProfile;
        console.log('取得用戶資料:', profile);
        return profile;
      }
    } catch (error) {
      console.error('取得用戶資料失敗:', error);
    }
    return null;
  }

  // 清除用戶資料
  clearUserProfile(): void {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
      console.log('用戶資料已清除');
    } catch (error) {
      console.error('清除用戶資料失敗:', error);
    }
  }

  // 檢查是否有儲存的資料
  hasStoredProfile(): boolean {
    return this.getUserProfile() !== null;
  }

  // 取得資料年齡（天數）
  getProfileAge(): number {
    const profile = this.getUserProfile();
    if (!profile) return -1;
    
    const lastUsed = new Date(profile.lastUsed);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - lastUsed.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays;
  }

  // 檢查資料是否過期（超過30天）
  isProfileExpired(): boolean {
    return this.getProfileAge() > 30;
  }
}

export const storageService = new StorageService();
export default storageService;

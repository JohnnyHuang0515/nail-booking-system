/**
 * 認證服務 - 處理 LINE Login 與 JWT Token
 */
import customerApiService from './api';

interface LineProfile {
  userId: string;
  displayName: string;
  pictureUrl?: string;
  statusMessage?: string;
}

interface AuthResult {
  success: boolean;
  token?: string;
  error?: string;
}

class AuthService {
  private isAuthenticated: boolean = false;

  async authenticateLineUser(lineProfile: LineProfile): Promise<AuthResult> {
    try {
      // 使用 LINE userId 作為唯一標識（改用有效的 email 域名）
      const email = `${lineProfile.userId}@lineuser.app`;
      
      // 1. 嘗試登入
      try {
        const loginResult = await customerApiService.loginLineUser(
          email,
          lineProfile.userId
        );
        
        customerApiService.setToken(loginResult.access_token);
        this.isAuthenticated = true;
        
        console.log('✅ LINE 用戶登入成功');
        return {
          success: true,
          token: loginResult.access_token,
        };
      } catch (loginError) {
        // 2. 登入失敗，嘗試註冊
        console.log('📝 LINE 用戶首次使用，進行註冊...');
        
        const registerResult = await customerApiService.registerLineUser(
          email,
          lineProfile.userId,
          lineProfile.displayName
        );
        
        console.log('✅ 註冊成功，用戶 ID:', registerResult.id);
        
        // 3. 註冊後自動登入
        const loginResult = await customerApiService.loginLineUser(
          email,
          lineProfile.userId
        );
        
        customerApiService.setToken(loginResult.access_token);
        this.isAuthenticated = true;
        
        console.log('✅ 自動登入成功');
        return {
          success: true,
          token: loginResult.access_token,
        };
      }
    } catch (error) {
      console.error('❌ 認證失敗:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : '認證失敗',
      };
    }
  }

  isUserAuthenticated(): boolean {
    return this.isAuthenticated && customerApiService.getToken() !== null;
  }

  logout(): void {
    customerApiService.clearToken();
    this.isAuthenticated = false;
  }
}

export const authService = new AuthService();
export default authService;


/**
 * 系統管理員認證 Hook
 */

import { useState, useEffect, useCallback } from 'react';
import systemAdminApiService from '../services/api-system-admin';

interface UserData {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
}

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);

  const login = async (email: string, password: string) => {
    try {
      console.log('🔐 開始登入...', { email });
      const response = await systemAdminApiService.login(email, password);
      console.log('📡 後端響應:', response);
      
      if (response.token) {
        console.log('✅ 登入成功，設置認證狀態...');
        localStorage.setItem('system_admin_token', response.token);
        localStorage.setItem('system_admin_user', JSON.stringify(response.user));
        
        systemAdminApiService.setAuthToken(response.token);
        
        setUserData(response.user);
        setIsAuthenticated(true);
        
        console.log('🎉 認證狀態已更新:', { isAuthenticated: true, user: response.user });
        
        return { success: true, user: response.user };
      } else {
        console.log('❌ 登入失敗：沒有 token');
        return { success: false, error: '登入失敗' };
      }
    } catch (error: any) {
      console.error('❌ 登入失敗:', error);
      return { success: false, error: error.message || '登入失敗' };
    }
  };

  const logout = useCallback(() => {
    localStorage.removeItem('system_admin_token');
    localStorage.removeItem('system_admin_user');
    systemAdminApiService.setAuthToken('');
    setUserData(null);
    setIsAuthenticated(false);
  }, []);

  const checkAuthStatus = useCallback(() => {
    const token = localStorage.getItem('system_admin_token');
    const storedUserData = localStorage.getItem('system_admin_user');
    
    if (token && storedUserData) {
      try {
        systemAdminApiService.setAuthToken(token);
        
        const user = JSON.parse(storedUserData);
        setUserData(user);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('解析用戶資料失敗:', error);
        logout();
      }
    }
    setLoading(false);
  }, [logout]);

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  return {
    isAuthenticated,
    userData,
    loading,
    login,
    logout,
  };
}

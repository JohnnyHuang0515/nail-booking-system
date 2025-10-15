/**
 * 系統管理員認證 Hook
 */

import { useState, useEffect, useCallback } from 'react';
import systemAdminApiService from '../services/api';

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
      const response = await systemAdminApiService.login(email, password);
      if (response.access_token) {
        localStorage.setItem('system_admin_token', response.access_token);
        localStorage.setItem('system_admin_user', JSON.stringify(response.user));
        
        systemAdminApiService.setAuthToken(response.access_token);
        
        setUserData(response.user);
        setIsAuthenticated(true);
        
        return { success: true, user: response.user };
      } else {
        return { success: false, error: '登入失敗' };
      }
    } catch (error: any) {
      console.error('Login failed:', error);
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

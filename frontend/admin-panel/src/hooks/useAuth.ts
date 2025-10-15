import { useState, useEffect, useCallback } from 'react';
import adminApiService from '../services/api';

interface MerchantData {
  id: string;
  name: string;
  email: string;
  line_channel_id: string;
  liff_id: string;
  timezone: string;
  is_active: boolean;
}

interface UserData {
  id: string;
  email: string;
  name: string;
  merchant_id: string;
  role: string;
  is_active: boolean;
}

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [merchantData, setMerchantData] = useState<MerchantData | null>(null);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);

  const logout = () => {
    localStorage.removeItem('merchant_token');
    localStorage.removeItem('merchant_data');
    localStorage.removeItem('user_data');
    setIsAuthenticated(false);
    setMerchantData(null);
    setUserData(null);
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await adminApiService.login(email, password);
      
      if (response.access_token) {
        localStorage.setItem('merchant_token', response.access_token);
        localStorage.setItem('merchant_data', JSON.stringify(response.user));
        localStorage.setItem('user_data', JSON.stringify(response.user));
        
        // 設定 API 服務的認證 token
        adminApiService.setAuthToken(response.access_token);
        adminApiService.setMerchantId(response.user.merchant_id);
        
        setUserData(response.user);
        setIsAuthenticated(true);
        
        return { success: true };
      }
    } catch (error: any) {
      console.error('Login failed:', error);
      return { 
        success: false, 
        error: error.message || '登入失敗' 
      };
    }
  };

  const register = async (userData: {
    email: string;
    password: string;
    name: string;
  }) => {
    try {
      const response = await adminApiService.register(userData);
      return { success: true, data: response };
    } catch (error: any) {
      console.error('Registration failed:', error);
      return { 
        success: false, 
        error: error.message || '註冊失敗' 
      };
    }
  };

  const getCurrentUser = async () => {
    try {
      const user = await adminApiService.getCurrentUser();
      setUserData(user);
      return user;
    } catch (error) {
      console.error('Failed to get current user:', error);
      logout();
      throw error;
    }
  };

  const getAuthHeaders = () => {
    const token = localStorage.getItem('merchant_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  // 初始化認證狀態
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('merchant_token');
      const storedMerchantData = localStorage.getItem('merchant_data');
      const storedUserData = localStorage.getItem('user_data');

      if (token && storedMerchantData && storedUserData) {
        try {
          adminApiService.setAuthToken(token);
          
          const merchantData = JSON.parse(storedMerchantData);
          const userData = JSON.parse(storedUserData);
          
          adminApiService.setMerchantId(userData.merchant_id);
          
          setMerchantData(merchantData);
          setUserData(userData);
          setIsAuthenticated(true);
          
          // 驗證 token 是否仍然有效
          await getCurrentUser();
        } catch (error) {
          console.error('Token validation failed:', error);
          logout();
        }
      }
      
      setLoading(false);
    };

    initAuth();
  }, []);

  return {
    isAuthenticated,
    merchantData,
    userData,
    loading,
    login,
    register,
    logout,
    getCurrentUser,
    getAuthHeaders
  };
}
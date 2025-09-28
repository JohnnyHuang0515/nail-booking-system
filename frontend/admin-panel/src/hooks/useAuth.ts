import { useState, useEffect } from 'react';

interface MerchantData {
  id: string;
  name: string;
  email: string;
  line_channel_id: string;
  liff_id: string;
  timezone: string;
  is_active: boolean;
}

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [merchantData, setMerchantData] = useState<MerchantData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = () => {
    const token = localStorage.getItem('merchant_token');
    const storedMerchantData = localStorage.getItem('merchant_data');

    if (token && storedMerchantData) {
      try {
        const merchant = JSON.parse(storedMerchantData);
        setMerchantData(merchant);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('解析商家資料失敗:', error);
        logout();
      }
    }
    setLoading(false);
  };

  const login = (merchant: MerchantData, token: string) => {
    localStorage.setItem('merchant_token', token);
    localStorage.setItem('merchant_data', JSON.stringify(merchant));
    setMerchantData(merchant);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('merchant_token');
    localStorage.removeItem('merchant_data');
    setMerchantData(null);
    setIsAuthenticated(false);
  };

  const getAuthHeaders = () => {
    const token = localStorage.getItem('merchant_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  return {
    isAuthenticated,
    merchantData,
    loading,
    login,
    logout,
    getAuthHeaders,
  };
}

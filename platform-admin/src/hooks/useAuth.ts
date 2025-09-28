import { useState, useEffect } from 'react';

interface AdminData {
  id: string;
  username: string;
  email: string;
  role: string;
  permissions: string[];
}

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [adminData, setAdminData] = useState<AdminData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = () => {
    const token = localStorage.getItem('admin_token');
    const storedAdminData = localStorage.getItem('admin_data');

    if (token && storedAdminData) {
      try {
        const admin = JSON.parse(storedAdminData);
        setAdminData(admin);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('解析管理員資料失敗:', error);
        logout();
      }
    }
    setLoading(false);
  };

  const login = (admin: AdminData, token: string) => {
    localStorage.setItem('admin_token', token);
    localStorage.setItem('admin_data', JSON.stringify(admin));
    setAdminData(admin);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_data');
    setAdminData(null);
    setIsAuthenticated(false);
  };

  const getAuthHeaders = () => {
    const token = localStorage.getItem('admin_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const hasPermission = (permission: string) => {
    return adminData?.permissions?.includes(permission) || false;
  };

  return {
    isAuthenticated,
    adminData,
    loading,
    login,
    logout,
    getAuthHeaders,
    hasPermission,
  };
}

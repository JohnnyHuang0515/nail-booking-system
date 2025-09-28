import React, { useState } from 'react';
import { 
  LayoutDashboard, 
  Store, 
  Activity, 
  FileText, 
  Ticket, 
  CreditCard, 
  Settings,
  ArrowLeft,
  UserCircle,
  LogOut,
  ChevronDown,
  Shield
} from 'lucide-react';

interface AdminData {
  id: string;
  username: string;
  email: string;
  role: string;
  permissions: string[];
}

interface NavigationProps {
  currentPage: string;
  onPageChange: (page: string) => void;
  selectedMerchantId: string | null;
  onBackToMerchants: () => void;
  adminData?: AdminData | null;
  onLogout?: () => void;
}

const Navigation: React.FC<NavigationProps> = ({ 
  currentPage, 
  onPageChange, 
  selectedMerchantId,
  onBackToMerchants,
  adminData,
  onLogout
}) => {
  const [showUserMenu, setShowUserMenu] = useState(false);

  const menuItems = [
    { id: 'dashboard', label: '儀表板', icon: LayoutDashboard },
    { id: 'merchants', label: '商家管理', icon: Store },
    { id: 'monitoring', label: '監控總覽', icon: Activity },
    { id: 'audit', label: '審計軌跡', icon: FileText },
    { id: 'tickets', label: '工單中心', icon: Ticket },
    { id: 'billing', label: '帳務管理', icon: CreditCard },
    { id: 'settings', label: '系統設定', icon: Settings },
  ];

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-indigo-600 mr-2" />
              <h1 className="text-xl font-semibold text-gray-900">
                平台管理員
              </h1>
            </div>
            
            <div className="hidden md:flex space-x-1">
              {menuItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => onPageChange(item.id)}
                    className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      currentPage === item.id
                        ? 'bg-indigo-100 text-indigo-700'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {item.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {selectedMerchantId && (
              <button
                onClick={onBackToMerchants}
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                返回商家列表
              </button>
            )}

            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 text-sm text-gray-700 hover:text-gray-900"
              >
                <UserCircle className="h-8 w-8 text-gray-400" />
                <div className="hidden md:block text-left">
                  <div className="font-medium">{adminData?.username || '管理員'}</div>
                  <div className="text-xs text-gray-500">{adminData?.role}</div>
                </div>
                <ChevronDown className="h-4 w-4" />
              </button>

              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border">
                  <div className="px-4 py-2 text-sm text-gray-700 border-b">
                    <div className="font-medium">{adminData?.username}</div>
                    <div className="text-xs text-gray-500">{adminData?.email}</div>
                    <div className="text-xs text-gray-500">{adminData?.role}</div>
                  </div>
                  <button
                    onClick={() => {
                      onLogout?.();
                      setShowUserMenu(false);
                    }}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    登出
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            {menuItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => onPageChange(item.id)}
                  className={`flex items-center w-full px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentPage === item.id
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {item.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
import React, { useState } from 'react';
import { Calendar, Home, Clock, Users, Sparkles, UserCircle, LogOut, ChevronDown, UserCog, Menu, X, CreditCard, Bell } from 'lucide-react';

interface MerchantData {
  id: string;
  name: string;
  email: string;
  line_channel_id: string;
  liff_id: string;
  timezone: string;
  is_active: boolean;
}

interface NavigationProps {
  currentPage: string;
  onPageChange: (page: string) => void;
  isAdmin?: boolean;
  merchantData?: MerchantData | null;
  onLogout?: () => void;
}

export default function Navigation({ 
  currentPage, 
  onPageChange, 
  isAdmin = true, 
  merchantData, 
  onLogout 
}: NavigationProps) {
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  const adminMenuItems = [
    { id: 'dashboard', name: '儀表板', icon: Home, path: '/' },
    { id: 'calendar', name: '行事曆管理', icon: Calendar, path: '/calendar' },
    { id: 'appointments', name: '預約管理', icon: Clock, path: '/appointments' },
    { id: 'schedule', name: '時段管理', icon: Calendar, path: '/schedule' },
    { id: 'services', name: '服務管理', icon: Sparkles, path: '/services' },
    { id: 'staff', name: '美甲師管理', icon: UserCog, path: '/staff' },
    { id: 'customers', name: '顧客管理', icon: Users, path: '/customers' },
    { id: 'billing', name: '計費管理', icon: CreditCard, path: '/billing' },
    { id: 'notifications', name: '通知管理', icon: Bell, path: '/notifications' },
  ];

  if (!isAdmin) return null;

  return (
    <nav className="bg-white shadow-sm border-b border-border">
      <div className="max-w-full mx-auto px-3 sm:px-4 lg:px-6">
        <div className="flex justify-between items-center h-16">
          {/* 左側 Logo */}
          <div className="flex-shrink-0 flex items-center">
            <Sparkles className="h-7 w-7 lg:h-8 lg:w-8 text-primary" />
            <span className="ml-2 font-medium text-base lg:text-lg text-foreground whitespace-nowrap">美甲管理</span>
          </div>
          
          {/* 中央菜單 */}
          <div className="hidden md:flex md:flex-1 md:justify-center">
            <div className="flex space-x-3 lg:space-x-6">
              {adminMenuItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => onPageChange(item.id)}
                    className={`${
                      currentPage === item.id
                        ? 'border-primary text-primary'
                        : 'border-transparent text-muted-foreground hover:text-foreground hover:border-muted'
                    } whitespace-nowrap py-2 px-1 border-b-2 inline-flex items-center transition-colors text-sm lg:text-base`}
                  >
                    <Icon className="h-4 w-4 mr-1.5" />
                    {item.name}
                  </button>
                );
              })}
            </div>
          </div>
          
          {/* 右側用戶區域 */}
          <div className="flex items-center relative flex-shrink-0 space-x-2">
            {/* 移動端菜單按鈕 */}
            <button
              onClick={() => setShowMobileMenu(!showMobileMenu)}
              className="md:hidden p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
            >
              {showMobileMenu ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>

            {/* 用戶菜單按鈕 */}
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-1 sm:space-x-2 text-sm text-gray-700 hover:text-gray-900 py-2 px-2 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <UserCircle className="h-7 w-7 sm:h-8 sm:w-8 text-muted-foreground flex-shrink-0" />
              <div className="hidden lg:block text-left max-w-[150px]">
                <div className="font-medium text-sm truncate">{merchantData?.name || '商家'}</div>
                <div className="text-xs text-gray-500 truncate">{merchantData?.email}</div>
              </div>
              <ChevronDown className="h-4 w-4 flex-shrink-0" />
            </button>

            {showUserMenu && (
              <div className="absolute right-0 top-full mt-2 w-56 bg-white rounded-lg shadow-lg py-1 z-50 border border-gray-200">
                <div className="px-4 py-3 text-sm text-gray-700 border-b border-gray-100">
                  <div className="font-medium truncate">{merchantData?.name || '商家'}</div>
                  <div className="text-xs text-gray-500 truncate mt-0.5">{merchantData?.email}</div>
                </div>
                <button
                  onClick={() => {
                    onLogout?.();
                    setShowUserMenu(false);
                  }}
                  className="flex items-center w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  登出
                </button>
              </div>
            )}
          </div>
        </div>

        {/* 移動端菜單 */}
        {showMobileMenu && (
          <div className="md:hidden border-t border-gray-200 bg-white">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {adminMenuItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      onPageChange(item.id);
                      setShowMobileMenu(false);
                    }}
                    className={`${
                      currentPage === item.id
                        ? 'bg-primary/10 text-primary border-l-4 border-primary'
                        : 'text-gray-600 hover:bg-gray-50 border-l-4 border-transparent'
                    } w-full flex items-center px-3 py-3 text-base font-medium transition-colors`}
                  >
                    <Icon className="h-5 w-5 mr-3" />
                    {item.name}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
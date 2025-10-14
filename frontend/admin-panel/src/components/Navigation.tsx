import React, { useState } from 'react';
import { Calendar, Home, Clock, Users, Sparkles, UserCircle, LogOut, ChevronDown } from 'lucide-react';

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

  const adminMenuItems = [
    { id: 'dashboard', name: '儀表板', icon: Home, path: '/' },
    { id: 'calendar', name: '行事曆管理', icon: Calendar, path: '/calendar' },
    { id: 'appointments', name: '預約管理', icon: Clock, path: '/appointments' },
    { id: 'schedule', name: '時段管理', icon: Calendar, path: '/schedule' },
    { id: 'services', name: '服務管理', icon: Sparkles, path: '/services' },
    { id: 'customers', name: '顧客管理', icon: Users, path: '/customers' },
  ];

  if (!isAdmin) return null;

  return (
    <nav className="bg-white shadow-sm border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Sparkles className="h-8 w-8 text-primary" />
              <span className="ml-2 font-medium text-lg text-foreground">美甲管理系統</span>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
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
                    } whitespace-nowrap py-2 px-1 border-b-2 inline-flex items-center transition-colors`}
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    {item.name}
                  </button>
                );
              })}
            </div>
          </div>
          <div className="flex items-center relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2 text-sm text-gray-700 hover:text-gray-900"
            >
              <UserCircle className="h-8 w-8 text-muted-foreground" />
              <div className="hidden md:block text-left">
                <div className="font-medium">{merchantData?.name || '商家'}</div>
                <div className="text-xs text-gray-500">{merchantData?.email}</div>
              </div>
              <ChevronDown className="h-4 w-4" />
            </button>

            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border">
                <div className="px-4 py-2 text-sm text-gray-700 border-b">
                  <div className="font-medium">{merchantData?.name}</div>
                  <div className="text-xs text-gray-500">{merchantData?.email}</div>
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
    </nav>
  );
}
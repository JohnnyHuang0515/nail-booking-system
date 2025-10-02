import React from 'react';
import { Calendar, Home, Clock, Users, Scissors, UserCircle } from 'lucide-react';

interface NavigationProps {
  currentPage: string;
  onPageChange: (page: string) => void;
  isAdmin?: boolean;
}

export default function Navigation({ currentPage, onPageChange, isAdmin = true }: NavigationProps) {
  const adminMenuItems = [
    { id: 'dashboard', name: '儀表板', icon: Home, path: '/' },
    { id: 'calendar', name: '行事曆管理', icon: Calendar, path: '/calendar' },
    { id: 'appointments', name: '預約管理', icon: Clock, path: '/appointments' },
    { id: 'schedule', name: '時段管理', icon: Calendar, path: '/schedule' },
    { id: 'services', name: '服務管理', icon: Scissors, path: '/services' },
    { id: 'customers', name: '顧客管理', icon: Users, path: '/customers' },
  ];

  if (!isAdmin) return null;

  return (
    <nav className="bg-white shadow-sm border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Scissors className="h-8 w-8 text-primary" />
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
          <div className="flex items-center">
            <UserCircle className="h-8 w-8 text-muted-foreground" />
          </div>
        </div>
      </div>
    </nav>
  );
}
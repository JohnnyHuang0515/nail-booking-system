import React, { useState } from 'react';
import { useAuth } from './hooks/useAuth';
import LoginPage from './components/auth/LoginPage';
import Navigation from './components/Navigation';
import Dashboard from './components/admin/Dashboard';
import Appointments from './components/admin/Appointments';
import Calendar from './components/admin/Calendar';
import Schedule from './components/admin/Schedule';
import Services from './components/admin/Services';
import Staff from './components/admin/Staff';
import Customers from './components/admin/Customers';
import Billing from './components/admin/Billing';
import Notifications from './components/admin/Notifications';

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const { isAuthenticated, merchantData, loading, login, logout } = useAuth();

  const handleLoginSuccess = (result: any) => {
    // useAuth hook 已經處理了登入狀態，這裡不需要額外處理
    console.log('Login successful:', result);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard onPageChange={setCurrentPage} />;
      case 'appointments':
        return <Appointments />;
      case 'calendar':
        return <Calendar />;
      case 'schedule':
        return <Schedule />;
      case 'services':
        return <Services />;
      case 'staff':
        return <Staff />;
      case 'customers':
        return <Customers />;
      case 'billing':
        return <Billing />;
      case 'notifications':
        return <Notifications />;
      default:
        return <Dashboard onPageChange={setCurrentPage} />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation 
        currentPage={currentPage} 
        onPageChange={setCurrentPage} 
        isAdmin={true}
        merchantData={merchantData}
        onLogout={logout}
      />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderPage()}
      </main>
    </div>
  );
}


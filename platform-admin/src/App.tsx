import React, { useState } from 'react';
import { useAuth } from './hooks/useAuth';
import LoginPage from './components/auth/LoginPage';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import MerchantList from './pages/MerchantList';
import MerchantDetail from './pages/MerchantDetail';
import MonitoringOverview from './pages/MonitoringOverview';
import AuditTrail from './pages/AuditTrail';
import TicketCenter from './pages/TicketCenter';
import Billing from './pages/Billing';
import SystemSettings from './pages/SystemSettings';

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [selectedMerchantId, setSelectedMerchantId] = useState<string | null>(null);
  const { isAuthenticated, adminData, loading, login, logout } = useAuth();

  const handleLoginSuccess = (admin: any) => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      login(admin, token);
    }
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard onPageChange={setCurrentPage} />;
      case 'merchants':
        if (selectedMerchantId) {
          return <MerchantDetail merchantId={selectedMerchantId} onBack={() => setSelectedMerchantId(null)} />;
        }
        return <MerchantList onMerchantSelect={setSelectedMerchantId} />;
      case 'monitoring':
        return <MonitoringOverview />;
      case 'audit':
        return <AuditTrail />;
      case 'tickets':
        return <TicketCenter />;
      case 'billing':
        return <Billing />;
      case 'settings':
        return <SystemSettings />;
      default:
        return <Dashboard onPageChange={setCurrentPage} />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
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
        selectedMerchantId={selectedMerchantId}
        onBackToMerchants={() => setSelectedMerchantId(null)}
        adminData={adminData}
        onLogout={logout}
      />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderPage()}
      </main>
    </div>
  );
}


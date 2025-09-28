import React, { useState } from 'react';
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

  return (
    <div className="min-h-screen bg-background">
      <Navigation 
        currentPage={currentPage} 
        onPageChange={setCurrentPage} 
        selectedMerchantId={selectedMerchantId}
        onBackToMerchants={() => setSelectedMerchantId(null)}
      />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderPage()}
      </main>
    </div>
  );
}


import React from 'react';
import { useAuth } from './hooks/useAuth-system-admin';
import LoginPage from './components/LoginPage';
import SystemAdminDashboard from './components/SystemAdminDashboard';
import './App.css';

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingContainer: {
    textAlign: 'center' as const,
  },
  spinner: {
    width: '48px',
    height: '48px',
    border: '2px solid #e5e7eb',
    borderTop: '2px solid #4f46e5',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    margin: '0 auto',
  },
  loadingText: {
    marginTop: '16px',
    color: '#6b7280',
  },
};

function App() {
  const { isAuthenticated, loading } = useAuth();

  console.log('🔄 App 渲染狀態:', { isAuthenticated, loading });

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingContainer}>
          <div style={styles.spinner} />
          <p style={styles.loadingText}>載入中...</p>
        </div>
      </div>
    );
  }

  console.log('🎯 渲染組件:', isAuthenticated ? 'SystemAdminDashboard' : 'LoginPage');

  return (
    <div>
      {isAuthenticated ? <SystemAdminDashboard /> : <LoginPage />}
    </div>
  );
}

export default App;
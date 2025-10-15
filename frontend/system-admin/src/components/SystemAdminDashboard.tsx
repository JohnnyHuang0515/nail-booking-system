/**
 * 系統管理員主頁面
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import systemAdminApiService from '../services/api';

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f9fafb',
  },
  header: {
    backgroundColor: 'white',
    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
    padding: '24px 0',
  },
  headerContent: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 16px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#111827',
    margin: 0,
  },
  subtitle: {
    fontSize: '16px',
    color: '#6b7280',
    margin: '4px 0 0 0',
  },
  userInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  userName: {
    fontSize: '14px',
    color: '#6b7280',
  },
  logoutButton: {
    backgroundColor: '#dc2626',
    color: 'white',
    padding: '8px 16px',
    borderRadius: '6px',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
  },
  main: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '24px 16px',
  },
  error: {
    backgroundColor: '#fef2f2',
    border: '1px solid #fecaca',
    color: '#dc2626',
    padding: '16px',
    borderRadius: '6px',
    marginBottom: '24px',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '24px',
    marginBottom: '32px',
  },
  statCard: {
    backgroundColor: 'white',
    padding: '24px',
    borderRadius: '8px',
    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
  },
  statTitle: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#6b7280',
    marginBottom: '8px',
  },
  statValue: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#111827',
  },
  merchantsCard: {
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
    padding: '24px',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
  },
  cardTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#111827',
    margin: 0,
  },
  addButton: {
    backgroundColor: '#4f46e5',
    color: 'white',
    padding: '8px 16px',
    borderRadius: '6px',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  searchInput: {
    width: '100%',
    padding: '12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    marginBottom: '16px',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse' as const,
  },
  tableHeader: {
    backgroundColor: '#f9fafb',
    padding: '12px',
    textAlign: 'left' as const,
    fontSize: '12px',
    fontWeight: '500',
    color: '#6b7280',
    textTransform: 'uppercase' as const,
    borderBottom: '1px solid #e5e7eb',
  },
  tableCell: {
    padding: '12px',
    fontSize: '14px',
    color: '#111827',
    borderBottom: '1px solid #e5e7eb',
  },
  statusBadge: {
    padding: '4px 8px',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: '500',
  },
  statusActive: {
    backgroundColor: '#dcfce7',
    color: '#166534',
  },
  statusInactive: {
    backgroundColor: '#fef2f2',
    color: '#dc2626',
  },
  actionButton: {
    backgroundColor: 'transparent',
    border: 'none',
    cursor: 'pointer',
    padding: '4px',
    margin: '0 4px',
  },
  loadingContainer: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  emptyState: {
    textAlign: 'center' as const,
    padding: '32px',
    color: '#6b7280',
  },
};

interface SystemStats {
  total_merchants: number;
  active_merchants: number;
  total_bookings: number;
  total_revenue: number;
  subscription_stats: {
    active: number;
    past_due: number;
    canceled: number;
  };
}

interface MerchantSummary {
  id: string;
  name: string;
  email: string;
  slug: string;
  is_active: boolean;
  created_at: string;
  subscription_status?: string;
  total_bookings: number;
  total_revenue: number;
}

export default function SystemAdminDashboard() {
  const { userData, logout } = useAuth();
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [merchants, setMerchants] = useState<MerchantSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      
      const [statsData, merchantsData] = await Promise.all([
        systemAdminApiService.getSystemStats(),
        systemAdminApiService.getMerchants()
      ]);
      
      setStats(statsData);
      setMerchants(merchantsData);
    } catch (err: any) {
      console.error('載入資料錯誤:', err);
      setError('載入資料失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  const filteredMerchants = merchants.filter(merchant =>
    merchant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    merchant.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.loadingText}>
          <div style={{
            width: '20px',
            height: '20px',
            border: '2px solid #e5e7eb',
            borderTop: '2px solid #4f46e5',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
          }} />
          <span>載入中...</span>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <div>
            <h1 style={styles.title}>系統管理後台</h1>
            <p style={styles.subtitle}>美甲預約系統管理</p>
          </div>
          <div style={styles.userInfo}>
            <span style={styles.userName}>
              歡迎，{userData?.name}
            </span>
            <button
              onClick={logout}
              style={styles.logoutButton}
            >
              登出
            </button>
          </div>
        </div>
      </header>

      <main style={styles.main}>
        {error && (
          <div style={styles.error}>
            {error}
          </div>
        )}

        {/* 系統統計 */}
        {stats && (
          <div style={styles.statsGrid}>
            <div style={styles.statCard}>
              <div style={styles.statTitle}>總商家數</div>
              <div style={styles.statValue}>{stats.total_merchants}</div>
            </div>
            <div style={styles.statCard}>
              <div style={styles.statTitle}>活躍商家</div>
              <div style={styles.statValue}>{stats.active_merchants}</div>
            </div>
            <div style={styles.statCard}>
              <div style={styles.statTitle}>總預約數</div>
              <div style={styles.statValue}>{stats.total_bookings}</div>
            </div>
            <div style={styles.statCard}>
              <div style={styles.statTitle}>總收入</div>
              <div style={styles.statValue}>${stats.total_revenue.toFixed(2)}</div>
            </div>
          </div>
        )}

        {/* 商家管理 */}
        <div style={styles.merchantsCard}>
          <div style={styles.cardHeader}>
            <h3 style={styles.cardTitle}>商家管理</h3>
            <button style={styles.addButton}>
              + 新增商家
            </button>
          </div>

          {/* 搜尋 */}
          <input
            type="text"
            placeholder="搜尋商家..."
            style={styles.searchInput}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />

          {/* 商家列表 */}
          <div style={{ overflowX: 'auto' }}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.tableHeader}>商家名稱</th>
                  <th style={styles.tableHeader}>聯絡信箱</th>
                  <th style={styles.tableHeader}>狀態</th>
                  <th style={styles.tableHeader}>預約數</th>
                  <th style={styles.tableHeader}>收入</th>
                  <th style={styles.tableHeader}>操作</th>
                </tr>
              </thead>
              <tbody>
                {filteredMerchants.map((merchant) => (
                  <tr key={merchant.id}>
                    <td style={styles.tableCell}>
                      <div style={{ fontWeight: '500' }}>
                        {merchant.name}
                      </div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>
                        {merchant.slug}
                      </div>
                    </td>
                    <td style={styles.tableCell}>{merchant.email}</td>
                    <td style={styles.tableCell}>
                      <span style={{
                        ...styles.statusBadge,
                        ...(merchant.is_active ? styles.statusActive : styles.statusInactive),
                      }}>
                        {merchant.is_active ? '啟用' : '停用'}
                      </span>
                    </td>
                    <td style={styles.tableCell}>{merchant.total_bookings}</td>
                    <td style={styles.tableCell}>${merchant.total_revenue.toFixed(2)}</td>
                    <td style={styles.tableCell}>
                      <button style={styles.actionButton}>編輯</button>
                      <button style={styles.actionButton}>刪除</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredMerchants.length === 0 && (
            <div style={styles.emptyState}>
              沒有找到商家
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

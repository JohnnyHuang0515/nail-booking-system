/**
 * 系統管理員登入頁面
 */

import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth-system-admin';

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f9fafb',
    padding: '48px 16px',
  },
  formContainer: {
    maxWidth: '400px',
    width: '100%',
    padding: '32px',
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    textAlign: 'center' as const,
    color: '#111827',
    marginBottom: '8px',
  },
  subtitle: {
    fontSize: '14px',
    textAlign: 'center' as const,
    color: '#6b7280',
    marginBottom: '32px',
  },
  input: {
    width: '100%',
    padding: '12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    marginBottom: '16px',
    boxSizing: 'border-box' as const,
  },
  button: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#4f46e5',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    marginBottom: '16px',
  },
  buttonDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
  },
  error: {
    color: '#dc2626',
    fontSize: '14px',
    textAlign: 'center' as const,
    marginBottom: '16px',
  },
  testInfo: {
    padding: '16px',
    backgroundColor: '#eff6ff',
    border: '1px solid #bfdbfe',
    borderRadius: '6px',
    fontSize: '12px',
  },
  testTitle: {
    fontWeight: '500',
    color: '#1e40af',
    marginBottom: '8px',
  },
  testText: {
    color: '#1e40af',
    margin: '4px 0',
  },
};

export default function LoginPage() {
  const [account, setAccount] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await login(account, password);
      if (result && result.success) {
        console.log('Login successful:', result);
        // 登入成功，useAuth hook 會處理狀態更新
      } else {
        setError(result?.error || '登入失敗');
      }
    } catch (err: any) {
      setError(err.message || '登入失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.formContainer}>
        <h2 style={styles.title}>
          系統管理員登入
        </h2>
        <p style={styles.subtitle}>
          美甲預約系統管理後台
        </p>
        
        <form onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="管理員帳號"
            value={account}
            onChange={(e) => setAccount(e.target.value)}
            style={styles.input}
            required
          />
          <input
            type="password"
            placeholder="密碼"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
            required
          />

          {error && (
            <div style={styles.error}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              ...styles.button,
              ...(loading ? styles.buttonDisabled : {}),
            }}
          >
            {loading ? '登入中...' : '登入'}
          </button>

          {/* 測試帳號資訊 */}
          <div style={styles.testInfo}>
            <h3 style={styles.testTitle}>測試帳號</h3>
            <p style={styles.testText}>帳號：system@nailbooking.com</p>
            <p style={styles.testText}>密碼：system123</p>
          </div>
        </form>
      </div>
    </div>
  );
}

import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { BookingProvider, useBooking } from './components/BookingContext';
import { liffService } from './utils/liff';
import { userAPI } from './services/api';

// 頁面組件
import DateSelectionPage from './pages/DateSelectionPage';
import TimeSelectionPage from './pages/TimeSelectionPage';
import ServiceSelectionPage from './pages/ServiceSelectionPage';
import ConfirmationPage from './pages/ConfirmationPage';
import SuccessPage from './pages/SuccessPage';

// 載入頁面
const LoadingPage: React.FC = () => (
  <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
    <div className="text-center">
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">載入中...</span>
      </div>
      <p className="mt-3 text-muted">正在初始化...</p>
    </div>
  </div>
);

// 錯誤頁面
const ErrorPage: React.FC<{ error: string }> = ({ error }) => (
  <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
    <div className="text-center">
      <div className="alert alert-danger" role="alert">
        <h4 className="alert-heading">發生錯誤</h4>
        <p>{error}</p>
        <hr />
        <p className="mb-0">請重新整理頁面或聯繫客服</p>
      </div>
    </div>
  </div>
);

// 主要的應用組件
const AppContent: React.FC = () => {
  const { dispatch } = useBooking();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // 初始化 LIFF
      await liffService.init();

      // 取得用戶資料
      const profile = await liffService.getProfile();
      
      // 登入或註冊用戶
      const user = await userAPI.loginWithLine(profile.userId, profile);
      
      // 設定用戶資料到 Context
      dispatch({ type: 'SET_USER', payload: user });

    } catch (err) {
      console.error('App initialization failed:', err);
      // 在開發環境中，即使初始化失敗也繼續運行
      const isDevMode = !process.env.REACT_APP_LIFF_ID || process.env.REACT_APP_LIFF_ID === 'your-liff-id-here';
      if (!isDevMode) {
        setError('初始化失敗，請稍後再試');
      } else {
        console.log('Development mode: Continuing despite initialization error');
        // 設定一個預設用戶 (使用資料庫中存在的 UUID)
        dispatch({ type: 'SET_USER', payload: {
          id: '1df2ea15-fb93-4e2c-a13a-4c616728c40a',
          line_user_id: 'dev-user-123',
          name: '開發測試用戶',
          phone: null
        }});
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingPage />;
  }

  if (error) {
    return <ErrorPage error={error} />;
  }

  return (
    <Router>
      <div className="app-container">
        <Routes>
          <Route path="/" element={<DateSelectionPage />} />
          <Route path="/time-selection" element={<TimeSelectionPage />} />
          <Route path="/service-selection" element={<ServiceSelectionPage />} />
          <Route path="/confirmation" element={<ConfirmationPage />} />
          <Route path="/success" element={<SuccessPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
};

// 根組件
const App: React.FC = () => {
  return (
    <BookingProvider>
      <AppContent />
    </BookingProvider>
  );
};

export default App;
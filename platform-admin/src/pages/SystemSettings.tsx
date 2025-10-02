import React, { useState, useEffect } from 'react';
import { Save, RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react';

interface SystemConfig {
  platform_name: string;
  default_timezone: string;
  max_merchants: number;
  webhook_timeout: number;
  rate_limit_per_minute: number;
  backup_frequency: string;
  maintenance_mode: boolean;
  email_notifications: boolean;
  sms_notifications: boolean;
}

const SystemSettings: React.FC = () => {
  const [config, setConfig] = useState<SystemConfig>({
    platform_name: '美甲預約平台',
    default_timezone: 'Asia/Taipei',
    max_merchants: 1000,
    webhook_timeout: 30,
    rate_limit_per_minute: 100,
    backup_frequency: 'daily',
    maintenance_mode: false,
    email_notifications: true,
    sms_notifications: false
  });
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetchSystemConfig();
  }, []);

  const fetchSystemConfig = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/admin/system-config`);
      const data = await response.json();
      
      // 確保所有字段都有值，避免受控/非受控組件警告
      setConfig({
        platform_name: data.platform_name || '美甲預約平台',
        default_timezone: data.default_timezone || 'Asia/Taipei',
        max_merchants: data.max_merchants || 1000,
        webhook_timeout: data.webhook_timeout || 30,
        rate_limit_per_minute: data.rate_limit_per_minute || 100,
        backup_frequency: data.backup_frequency || 'daily',
        maintenance_mode: data.maintenance_mode || false,
        email_notifications: data.email_notifications || true,
        sms_notifications: data.sms_notifications || false
      });
    } catch (error) {
      console.error('取得系統設定失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveSystemConfig = async () => {
    try {
      setLoading(true);
      await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/admin/system-config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('儲存系統設定失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof SystemConfig, value: any) => {
    setConfig(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">系統設定</h1>
        <button
          onClick={saveSystemConfig}
          disabled={loading}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? (
            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Save className="w-4 h-4 mr-2" />
          )}
          {saved ? '已儲存' : '儲存設定'}
        </button>
      </div>

      {saved && (
        <div className="bg-green-50 border border-green-200 rounded-md p-4">
          <div className="flex">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800">
                系統設定已成功儲存
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 基本設定 */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">基本設定</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                平台名稱
              </label>
              <input
                type="text"
                value={config.platform_name}
                onChange={(e) => handleInputChange('platform_name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                預設時區
              </label>
              <select
                value={config.default_timezone}
                onChange={(e) => handleInputChange('default_timezone', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="Asia/Taipei">台北 (UTC+8)</option>
                <option value="Asia/Tokyo">東京 (UTC+9)</option>
                <option value="Asia/Shanghai">上海 (UTC+8)</option>
                <option value="UTC">UTC (UTC+0)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                最大商家數量
              </label>
              <input
                type="number"
                value={config.max_merchants}
                onChange={(e) => handleInputChange('max_merchants', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* 技術設定 */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">技術設定</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Webhook 超時時間 (秒)
              </label>
              <input
                type="number"
                value={config.webhook_timeout}
                onChange={(e) => handleInputChange('webhook_timeout', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                每分鐘請求限制
              </label>
              <input
                type="number"
                value={config.rate_limit_per_minute}
                onChange={(e) => handleInputChange('rate_limit_per_minute', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                備份頻率
              </label>
              <select
                value={config.backup_frequency}
                onChange={(e) => handleInputChange('backup_frequency', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="hourly">每小時</option>
                <option value="daily">每日</option>
                <option value="weekly">每週</option>
                <option value="monthly">每月</option>
              </select>
            </div>
          </div>
        </div>

        {/* 通知設定 */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">通知設定</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-gray-900">電子郵件通知</h3>
                <p className="text-sm text-gray-500">啟用系統事件電子郵件通知</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.email_notifications}
                  onChange={(e) => handleInputChange('email_notifications', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-gray-900">簡訊通知</h3>
                <p className="text-sm text-gray-500">啟用緊急事件簡訊通知</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.sms_notifications}
                  onChange={(e) => handleInputChange('sms_notifications', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* 系統狀態 */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">系統狀態</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-gray-900">維護模式</h3>
                <p className="text-sm text-gray-500">啟用後系統將進入維護模式</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.maintenance_mode}
                  onChange={(e) => handleInputChange('maintenance_mode', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-red-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
              </label>
            </div>

            {config.maintenance_mode && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                <div className="flex">
                  <AlertTriangle className="w-5 h-5 text-yellow-400" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-yellow-800">
                      維護模式已啟用
                    </p>
                    <p className="text-sm text-yellow-700">
                      系統將暫時停止服務，請謹慎使用此功能。
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemSettings;
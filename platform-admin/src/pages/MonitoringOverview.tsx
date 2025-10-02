import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { 
  Monitor, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  TrendingUp,
  Users,
  Calendar,
  DollarSign
} from 'lucide-react';

interface MonitoringData {
  platform_health: {
    healthy_merchants: number;
    warning_merchants: number;
    critical_merchants: number;
    overall_health_score: number;
  };
  system_statistics: {
    total_users: number;
    total_appointments: number;
    total_revenue: number;
    system_uptime: string;
  };
  error_leaderboard: Array<{
    merchant_id: string;
    error_count: number;
    error_rate: number;
  }>;
}

interface Alert {
  id: string;
  merchant_id: string;
  severity: 'warning' | 'critical';
  type: string;
  message: string;
  created_at: string;
  status: string;
}

const MonitoringOverview: React.FC = () => {
  const [monitoringData, setMonitoringData] = useState<MonitoringData>({
    platform_health: {
      healthy_merchants: 0,
      warning_merchants: 0,
      critical_merchants: 0,
      overall_health_score: 0
    },
    system_statistics: {
      total_users: 0,
      total_appointments: 0,
      total_revenue: 0,
      system_uptime: '0%'
    },
    error_leaderboard: []
  });
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);

  // 取得監控總覽
  const fetchMonitoringOverview = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/monitoring/overview');
      if (response.ok) {
        const data = await response.json();
        // 安全地合併 API 資料與預設值
        setMonitoringData({
          platform_health: {
            healthy_merchants: data?.platform_health?.healthy_merchants ?? 0,
            warning_merchants: data?.platform_health?.warning_merchants ?? 0,
            critical_merchants: data?.platform_health?.critical_merchants ?? 0,
            overall_health_score: data?.platform_health?.overall_health_score ?? 0
          },
          system_statistics: {
            total_users: data?.system_statistics?.total_users ?? 0,
            total_appointments: data?.system_statistics?.total_appointments ?? 0,
            total_revenue: data?.system_statistics?.total_revenue ?? 0,
            system_uptime: data?.system_statistics?.system_uptime ?? '0%'
          },
          error_leaderboard: data?.error_leaderboard ?? []
        });
      } else {
        console.error('取得監控總覽失敗');
        // 保持當前狀態，不重置為預設值
      }
    } catch (error) {
      console.error('網路錯誤');
      // 保持當前狀態，不重置為預設值
    } finally {
      setLoading(false);
    }
  };

  // 取得告警列表
  const fetchAlerts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/monitoring/alerts');
      if (response.ok) {
        const data = await response.json();
        setAlerts(data.alerts);
      }
    } catch (error) {
      console.error('取得告警失敗:', error);
    }
  };

  // 確認告警
  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      const response = await fetch(`/api/v1/monitoring/alerts/${alertId}/acknowledge`, {
        method: 'POST',
      });

      if (response.ok) {
        console.log('告警已確認');
        fetchAlerts();
      } else {
        console.error('確認告警失敗');
      }
    } catch (error) {
      console.error('網路錯誤');
    }
  };

  useEffect(() => {
    fetchMonitoringOverview();
    fetchAlerts();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">監控總覽</h2>
        <Button variant="outline" onClick={fetchMonitoringOverview}>
          <Monitor className="h-4 w-4 mr-2" />
          重新整理
        </Button>
      </div>

      {/* 平台健康狀態 */}
      {loading ? (
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">載入中...</span>
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">健康商家</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{monitoringData.platform_health.healthy_merchants}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">警告商家</CardTitle>
                <AlertTriangle className="h-4 w-4 text-yellow-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">{monitoringData.platform_health.warning_merchants}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">嚴重商家</CardTitle>
                <XCircle className="h-4 w-4 text-red-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{monitoringData.platform_health.critical_merchants}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">整體健康分數</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${
                  monitoringData.platform_health.overall_health_score >= 90 ? 'text-green-600' : 
                  monitoringData.platform_health.overall_health_score >= 70 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {monitoringData.platform_health.overall_health_score}%
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 系統統計 */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">總用戶數</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{monitoringData.system_statistics.total_users}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">總預約數</CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{monitoringData.system_statistics.total_appointments}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">總營收</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">NT$ {monitoringData.system_statistics.total_revenue.toLocaleString()}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">系統可用性</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{monitoringData.system_statistics.system_uptime}</div>
              </CardContent>
            </Card>
          </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* 錯誤榜 */}
        <Card>
          <CardHeader>
            <CardTitle>錯誤榜</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {monitoringData.error_leaderboard.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="space-y-1">
                    <p className="text-sm font-medium leading-none">{item.merchant_id}</p>
                    <p className="text-sm text-muted-foreground">{item.error_count} 次錯誤</p>
                  </div>
                  <div className="text-sm font-medium text-red-600">
                    {(item.error_rate * 100).toFixed(2)}%
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 告警列表 */}
        <Card>
          <CardHeader>
            <CardTitle>告警列表</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {alerts.map((alert) => (
                <div key={alert.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      {alert.severity === 'critical' ? (
                        <XCircle className="h-4 w-4 text-red-600" />
                      ) : (
                        <AlertTriangle className="h-4 w-4 text-yellow-600" />
                      )}
                      <span className="text-sm font-medium">{alert.type}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">{alert.message}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(alert.created_at).toLocaleString('zh-TW')}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    {alert.status === 'active' && (
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleAcknowledgeAlert(alert.id)}
                      >
                        確認
                      </Button>
                    )}
                    <Button variant="outline" size="sm">
                      查看商家
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
          </div>
        </>
      )}
    </div>
  );
};

export default MonitoringOverview;
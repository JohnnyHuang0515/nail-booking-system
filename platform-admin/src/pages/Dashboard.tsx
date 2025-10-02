import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { 
  BarChart3, 
  Download, 
  RefreshCw,
  TrendingUp,
  Users,
  Store,
  Calendar,
  DollarSign,
  Settings
} from 'lucide-react';
// import { useMonitoringOverview, useReportsDashboard } from '../hooks/useApi';

interface DashboardData {
  merchant_statistics: {
    statistics: {
      total_merchants: number;
      active_merchants: number;
      inactive_merchants: number;
      new_merchants_this_month: number;
      growth_rate: number;
    };
  };
  platform_overview: {
    total_revenue: number;
    total_appointments: number;
    total_customers: number;
    system_uptime: string;
  };
  trends: {
    revenue_growth: number;
    customer_growth: number;
    appointment_growth: number;
  };
  top_services: Array<{
    name: string;
    count: number;
    revenue: number;
  }>;
}

interface Merchant {
  id: string;
  name: string;
  line_channel_id: string;
  is_active: boolean;
  created_at: string;
}

interface DashboardProps {
  onPageChange: (page: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onPageChange }) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [loading, setLoading] = useState(false);

  // 取得儀表板資料
  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/reports/dashboard`);
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data.dashboard_data);
      } else {
        console.error('取得儀表板資料失敗');
      }
    } catch (error) {
      console.error('網路錯誤');
    } finally {
      setLoading(false);
    }
  };

  // 取得商家列表
  const fetchMerchants = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/merchants`);
      if (response.ok) {
        const data = await response.json();
        setMerchants(data.slice(0, 5)); // 只顯示前5個
      } else {
        console.error('取得商家列表失敗:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('取得商家列表失敗:', error);
    }
  };

  // 匯出報表
  const handleExport = async (type: string) => {
    try {
      let url = '';
      let filename = '';
      
      switch (type) {
        case 'merchant-list':
          url = '/api/v1/reports/export/merchant-list';
          filename = 'merchant_list.csv';
          break;
        case 'credentials-list':
          url = '/api/v1/reports/export/credentials-list';
          filename = 'credentials_list.csv';
          break;
        case 'operational-report':
          url = '/api/v1/reports/export/operational-report';
          filename = 'operational_report.csv';
          break;
        default:
          return;
      }

      const response = await fetch(url);
      if (response.ok) {
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);
        console.log('匯出成功');
      } else {
        console.error('匯出失敗');
      }
    } catch (error) {
      console.error('匯出失敗');
    }
  };

  useEffect(() => {
    fetchDashboardData();
    fetchMerchants();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">平台管理儀表板</h2>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={fetchDashboardData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            重新整理
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExport('operational-report')}>
            <Download className="h-4 w-4 mr-2" />
            匯出營運報表
          </Button>
        </div>
      </div>

      {/* 商家統計 */}
      {dashboardData && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">總商家數</CardTitle>
              <Store className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.merchant_statistics.statistics.total_merchants}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">活躍商家</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{dashboardData.merchant_statistics.statistics.active_merchants}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">本月新增</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{dashboardData.merchant_statistics.statistics.new_merchants_this_month}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">成長率</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{dashboardData.merchant_statistics.statistics.growth_rate}%</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 平台總覽 */}
      {dashboardData && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">總營收</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">NT$ {dashboardData.platform_overview.total_revenue.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">總預約數</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.platform_overview.total_appointments}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">總用戶數</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.platform_overview.total_customers}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">系統可用性</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{dashboardData.platform_overview.system_uptime}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 成長趨勢 */}
      {dashboardData && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>營收成長</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{dashboardData.trends.revenue_growth}%</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>用戶成長</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{dashboardData.trends.customer_growth}%</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>預約成長</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">{dashboardData.trends.appointment_growth}%</div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {/* 熱門服務 */}
        <Card>
          <CardHeader>
            <CardTitle>熱門服務</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dashboardData?.top_services?.map((service, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="space-y-1">
                    <p className="text-sm font-medium leading-none">{service.name}</p>
                    <p className="text-sm text-muted-foreground">{service.count} 次預約</p>
                  </div>
                  <div className="text-sm font-medium">NT$ {service.revenue.toLocaleString()}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 最近商家 */}
        <Card>
          <CardHeader>
            <CardTitle>最近商家</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {merchants.map((merchant) => (
                <div key={merchant.id} className="flex items-center justify-between">
                  <div className="space-y-1">
                    <p className="text-sm font-medium leading-none">{merchant.name}</p>
                    <p className="text-sm text-muted-foreground">{merchant.line_channel_id}</p>
                  </div>
                  <div className={`text-sm font-medium ${merchant.is_active ? 'text-green-600' : 'text-red-600'}`}>
                    {merchant.is_active ? '活躍' : '停用'}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 快速操作 */}
      <Card>
        <CardHeader>
          <CardTitle>快速操作</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <Button 
              variant="outline" 
              className="h-20 flex-col"
              onClick={() => onPageChange('merchants')}
            >
              <Store className="h-6 w-6 mb-2" />
              商家管理
            </Button>
            <Button 
              variant="outline" 
              className="h-20 flex-col"
              onClick={() => onPageChange('monitoring')}
            >
              <Users className="h-6 w-6 mb-2" />
              監控總覽
            </Button>
            <Button 
              variant="outline" 
              className="h-20 flex-col"
              onClick={() => onPageChange('reports')}
            >
              <BarChart3 className="h-6 w-6 mb-2" />
              報表分析
            </Button>
            <Button 
              variant="outline" 
              className="h-20 flex-col"
              onClick={() => onPageChange('settings')}
            >
              <Settings className="h-6 w-6 mb-2" />
              系統設定
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
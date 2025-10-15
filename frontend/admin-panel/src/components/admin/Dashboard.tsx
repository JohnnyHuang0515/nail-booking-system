import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Calendar, Clock, Users, Sparkles, TrendingUp, Plus, Loader2, UserCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import adminApiService from '../../services/api';

interface DashboardProps {
  onPageChange: (page: string) => void;
}

interface DashboardStats {
  todayAppointments: number;
  monthlyRevenue: number;
  activeCustomers: number;
  totalServices: number;
}

interface Appointment {
  id: string;
  time: string;
  service: string;
  customer: string;
  status: string;
}

export default function Dashboard({ onPageChange }: DashboardProps) {
  const [stats, setStats] = useState<DashboardStats>({
    todayAppointments: 0,
    monthlyRevenue: 0,
    activeCustomers: 0,
    totalServices: 0
  });
  const [todayAppointments, setTodayAppointments] = useState<Appointment[]>([]);
  const [staffCount, setStaffCount] = useState<number>(2); // 美甲師數量，預設為2
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 並行載入儀表板資料
      // 獲取過去30天到未來30天的預約資料，以便計算活躍客戶和收入
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      const thirtyDaysAgoStr = thirtyDaysAgo.toISOString().split('T')[0];
      
      const thirtyDaysLater = new Date();
      thirtyDaysLater.setDate(thirtyDaysLater.getDate() + 30);
      const thirtyDaysLaterStr = thirtyDaysLater.toISOString().split('T')[0];
      
      const [appointmentsData, servicesData, staffData] = await Promise.all([
        adminApiService.getAppointments(thirtyDaysAgoStr, thirtyDaysLaterStr),
        adminApiService.getServices(),
        adminApiService.getStaff()
      ]) as [any[], any[], any[]];

      // 處理統計資料
      const today = new Date().toISOString().split('T')[0];
      const currentMonth = new Date().toISOString().slice(0, 7); // YYYY-MM
      
      const todayAppts = appointmentsData.filter((apt: any) => 
        apt.appointment_date === today
      );

      // 計算本月收入（只計算已完成的預約）
      const monthlyRevenue = appointmentsData
        .filter((apt: any) => 
          apt.status === 'completed' && 
          apt.appointment_date?.startsWith(currentMonth)
        )
        .reduce((sum: number, apt: any) => {
          return sum + (apt.service?.price || 0);
        }, 0);

      // 計算活躍客戶（本月已完成預約的客戶，更符合業務需求）
      const activeCustomersSet = new Set();
      appointmentsData
        .filter((apt: any) => 
          apt.appointment_date?.startsWith(currentMonth) && 
          apt.status === 'completed' &&
          apt.customer_name &&
          apt.customer_phone
        )
        .forEach((apt: any) => {
          activeCustomersSet.add(`${apt.customer_name}-${apt.customer_phone}`);
        });

      setStats({
        todayAppointments: todayAppts.length,
        monthlyRevenue: monthlyRevenue,
        activeCustomers: activeCustomersSet.size,
        totalServices: servicesData.length || 0
      });

      // 處理今日預約
      const formattedAppointments = todayAppts.map((apt: any) => ({
        id: apt.id,
        time: apt.appointment_time,
        service: apt.service?.name || '未知服務',
        customer: apt.customer_name || '未知客戶',
        status: getStatusText(apt.status)
      }));

      setTodayAppointments(formattedAppointments);
      
      // 設置美甲師數量（用於計算時段容量）
      const activeStaffCount = staffData.filter((s: any) => s.is_active).length;
      setStaffCount(activeStaffCount > 0 ? activeStaffCount : 2); // 至少為2

    } catch (err) {
      console.error('載入儀表板資料失敗:', err);
      setError('載入資料失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  const getTodayTimeSlotStats = () => {
    const fixedSlots = ['12:00', '15:00', '18:00'];
    return fixedSlots.map(time => {
      const appointments = todayAppointments.filter(apt => apt.time === time);
      return {
        time,
        count: appointments.length,
        appointments
      };
    });
  };

  const getStatusText = (status: string) => {
    const statusMap: { [key: string]: string } = {
      'confirmed': '已確認',
      'in-progress': '進行中',
      'pending': '待確認',
      'completed': '已完成',
      'cancelled': '已取消'
    };
    return statusMap[status] || status;
  };

  const statsConfig = [
    { title: '今日預約', value: stats.todayAppointments.toString(), icon: Calendar, color: 'text-primary' },
    { title: '本月收入', value: `NT$${stats.monthlyRevenue.toLocaleString()}`, icon: TrendingUp, color: 'text-green-600' },
    { title: '活躍顧客', value: stats.activeCustomers.toString(), icon: Users, color: 'text-blue-500' },
    { title: '服務項目', value: stats.totalServices.toString(), icon: Sparkles, color: 'text-purple-500' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">載入中...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="text-red-500 mb-4">{error}</div>
        <Button onClick={loadDashboardData} variant="outline">
          重新載入
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-foreground">儀表板</h1>
        <Button onClick={() => onPageChange('appointments')} className="bg-primary hover:bg-primary/90">
          <Plus className="h-4 w-4 mr-2" />
          新增預約
        </Button>
      </div>

      {/* 統計卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {statsConfig.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* 今日時段預約概覽 */}
      <Card className="border-2">
        <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b">
          <CardTitle className="flex items-center text-xl">
            <Clock className="h-6 w-6 mr-2 text-primary" />
            今日時段預約概覽
            <Badge variant="secondary" className="ml-auto text-sm px-3 py-1">
              {new Date().toLocaleDateString('zh-TW', { month: 'long', day: 'numeric', weekday: 'short' })}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {getTodayTimeSlotStats().map((slot, idx) => {
              // 每個時段的最大容量 = 啟用的美甲師數量（每位美甲師同時只能服務一位客戶）
              const maxCapacity = staffCount;
              const percentage = (slot.count / maxCapacity) * 100;
              const isEmpty = slot.count === 0;
              const isFull = slot.count >= maxCapacity;
              
              return (
                <div 
                  key={slot.time}
                  className={`relative overflow-hidden rounded-xl border-2 transition-all hover:shadow-lg ${
                    isFull 
                      ? 'bg-gradient-to-br from-red-50 to-orange-50 border-red-300' 
                      : isEmpty 
                        ? 'bg-gradient-to-br from-gray-50 to-slate-50 border-gray-200' 
                        : 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-300'
                  }`}
                >
                  {/* 時段標題 */}
                  <div className={`px-5 py-3 border-b-2 ${
                    isFull 
                      ? 'bg-gradient-to-r from-red-100 to-orange-100 border-red-200' 
                      : isEmpty 
                        ? 'bg-gray-100 border-gray-200' 
                        : 'bg-gradient-to-r from-green-100 to-emerald-100 border-green-200'
                  }`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Clock className={`h-5 w-5 ${
                          isFull ? 'text-red-600' : isEmpty ? 'text-gray-500' : 'text-green-600'
                        }`} />
                        <span className="font-bold text-lg">{slot.time}</span>
                      </div>
                      <Badge 
                        variant={isFull ? "destructive" : isEmpty ? "secondary" : "default"}
                        className={`text-xs px-2 py-1 ${
                          isFull 
                            ? 'bg-red-500' 
                            : isEmpty 
                              ? 'bg-gray-400' 
                              : 'bg-green-500'
                        }`}
                      >
                        {isFull ? '已滿' : isEmpty ? '空閒' : '有預約'}
                      </Badge>
                    </div>
                  </div>

                  {/* 預約數量 */}
                  <div className="p-5">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm text-gray-600 font-medium">預約數量</span>
                      <span className={`text-2xl font-bold ${
                        isFull ? 'text-red-600' : isEmpty ? 'text-gray-400' : 'text-green-600'
                      }`}>
                        {slot.count} / {maxCapacity}
                      </span>
                    </div>

                    {/* 進度條 */}
                    <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                      <div 
                        className={`h-full transition-all duration-500 rounded-full ${
                          isFull 
                            ? 'bg-gradient-to-r from-red-500 to-orange-500' 
                            : isEmpty 
                              ? 'bg-gray-300' 
                              : 'bg-gradient-to-r from-green-500 to-emerald-500'
                        }`}
                        style={{ width: `${Math.min(percentage, 100)}%` }}
                      />
                    </div>

                    {/* 預約客戶列表 */}
                    {slot.count > 0 && (
                      <div className="mt-4 space-y-2">
                        {slot.appointments.map((apt, aptIdx) => (
                          <div 
                            key={aptIdx}
                            className="flex items-center space-x-2 text-sm bg-white rounded-lg p-2 border"
                          >
                            <UserCircle className="h-4 w-4 text-gray-500 flex-shrink-0" />
                            <span className="flex-1 truncate font-medium text-gray-700">{apt.customer}</span>
                            <span className="text-xs text-gray-500">{apt.service}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* 空閒提示 */}
                    {isEmpty && (
                      <div className="mt-4 text-center py-3">
                        <p className="text-sm text-gray-400">暫無預約</p>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* 今日預約詳細列表與快速操作 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calendar className="h-5 w-5 mr-2 text-primary" />
              今日預約詳細列表
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {todayAppointments.length > 0 ? (
                todayAppointments.map((appointment) => (
                  <div key={appointment.id} className="flex items-center justify-between p-4 bg-muted rounded-lg hover:bg-muted/80 transition-colors">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-medium text-lg">{appointment.customer}</div>
                        <div className={`text-xs px-3 py-1 rounded-full font-medium ${
                          appointment.status === '已確認' ? 'bg-green-100 text-green-700 border border-green-200' :
                          appointment.status === '進行中' ? 'bg-blue-100 text-blue-700 border border-blue-200' :
                          appointment.status === '已完成' ? 'bg-purple-100 text-purple-700 border border-purple-200' :
                          appointment.status === '已取消' ? 'bg-red-100 text-red-700 border border-red-200' :
                          'bg-yellow-100 text-yellow-700 border border-yellow-200'
                        }`}>
                          {appointment.status}
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-sm text-muted-foreground">
                        <div className="flex items-center space-x-4">
                          <div className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {appointment.time}
                          </div>
                          <div className="flex items-center">
                            <Sparkles className="h-4 w-4 mr-1" />
                            {appointment.service}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  今日暫無預約
                </div>
              )}
            </div>
          </CardContent>
        </Card>

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
                onClick={() => onPageChange('appointments')}
              >
                <Calendar className="h-6 w-6 mb-2" />
                新增預約
              </Button>
              <Button 
                variant="outline" 
                className="h-20 flex-col"
                onClick={() => onPageChange('customers')}
              >
                <Users className="h-6 w-6 mb-2" />
                顧客管理
              </Button>
              <Button 
                variant="outline" 
                className="h-20 flex-col"
                onClick={() => onPageChange('services')}
              >
                <Sparkles className="h-6 w-6 mb-2" />
                服務管理
              </Button>
              <Button 
                variant="outline" 
                className="h-20 flex-col"
                onClick={() => onPageChange('schedule')}
              >
                <Clock className="h-6 w-6 mb-2" />
                時段設定
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
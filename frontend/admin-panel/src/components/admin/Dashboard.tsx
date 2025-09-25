import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Calendar, Clock, Users, Sparkles, TrendingUp, Plus } from 'lucide-react';
import { Button } from '../ui/button';

interface DashboardProps {
  onPageChange: (page: string) => void;
}

export default function Dashboard({ onPageChange }: DashboardProps) {
  const stats = [
    { title: '今日預約', value: '12', icon: Calendar, color: 'text-primary' },
    { title: '本月收入', value: '¥24,500', icon: TrendingUp, color: 'text-green-600' },
    { title: '活躍顧客', value: '156', icon: Users, color: 'text-blue-500' },
    { title: '服務項目', value: '8', icon: Sparkles, color: 'text-purple-500' },
  ];

  const todayAppointments = [
    { time: '09:00', service: '基礎保養', customer: '張小姐', status: '已確認' },
    { time: '10:30', service: '法式指甲', customer: '李小姐', status: '進行中' },
    { time: '14:00', service: '光療指甲', customer: '王小姐', status: '待確認' },
    { time: '15:30', service: '手部護理', customer: '陳小姐', status: '已確認' },
  ];

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
        {stats.map((stat) => {
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

      {/* 今日預約 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Clock className="h-5 w-5 mr-2 text-primary" />
              今日預約
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {todayAppointments.map((appointment, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <div>
                    <div className="font-medium">{appointment.time}</div>
                    <div className="text-sm text-muted-foreground">{appointment.service}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">{appointment.customer}</div>
                    <div className={`text-xs px-2 py-1 rounded-full inline-block ${
                      appointment.status === '已確認' ? 'bg-green-100 text-green-700' :
                      appointment.status === '進行中' ? 'bg-blue-100 text-blue-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                      {appointment.status}
                    </div>
                  </div>
                </div>
              ))}
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
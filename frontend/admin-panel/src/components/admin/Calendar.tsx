import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { ChevronLeft, ChevronRight, Plus, Loader2 } from 'lucide-react';
import adminApiService from '../../services/api';

interface CalendarAppointment {
  id: string;
  time: string;
  service: string;
  customer: string;
  status: string;
  customer_phone?: string;
  notes?: string;
}

export default function Calendar() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [appointments, setAppointments] = useState<Record<string, CalendarAppointment[]>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 載入預約數據
  const loadAppointments = async (date: Date) => {
    try {
      setLoading(true);
      setError(null);
      
      const year = date.getFullYear();
      const month = date.getMonth();
      
      // 計算月份的第一天和最後一天
      const startDate = new Date(year, month, 1);
      const endDate = new Date(year, month + 1, 0);
      
      const startDateStr = startDate.toISOString().split('T')[0];
      const endDateStr = endDate.toISOString().split('T')[0];
      
      const appointmentsData = await adminApiService.getCalendarAppointments(startDateStr, endDateStr);
      
      // 將預約按日期分組
      const groupedAppointments: Record<string, CalendarAppointment[]> = {};
      appointmentsData.forEach(apt => {
        const dateKey = apt.appointment_date || new Date().toISOString().split('T')[0];
        if (!groupedAppointments[dateKey]) {
          groupedAppointments[dateKey] = [];
        }
        groupedAppointments[dateKey].push(apt);
      });
      
      console.log('載入的預約數據:', appointmentsData);
      console.log('分組後的預約:', groupedAppointments);
      
      setAppointments(groupedAppointments);
    } catch (err) {
      console.error('載入預約數據失敗:', err);
      setError('載入預約數據失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  // 當月份改變時重新載入數據
  useEffect(() => {
    loadAppointments(currentDate);
  }, [currentDate]);

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(day);
    }
    
    return days;
  };

  const formatDateKey = (day: number) => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      if (direction === 'prev') {
        newDate.setMonth(prev.getMonth() - 1);
      } else {
        newDate.setMonth(prev.getMonth() + 1);
      }
      return newDate;
    });
  };

  const refreshAppointments = () => {
    loadAppointments(currentDate);
  };

  const monthNames = [
    '一月', '二月', '三月', '四月', '五月', '六月',
    '七月', '八月', '九月', '十月', '十一月', '十二月'
  ];

  const weekDays = ['日', '一', '二', '三', '四', '五', '六'];

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-semibold text-foreground">行事曆管理</h1>
          <Button className="bg-primary hover:bg-primary/90" disabled>
            <Plus className="h-4 w-4 mr-2" />
            新增預約
          </Button>
        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin" />
              <span className="ml-2">載入預約數據中...</span>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-semibold text-foreground">行事曆管理</h1>
          <Button className="bg-primary hover:bg-primary/90" onClick={refreshAppointments}>
            <Plus className="h-4 w-4 mr-2" />
            新增預約
          </Button>
        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-red-500 mb-4">{error}</div>
              <Button onClick={refreshAppointments} variant="outline">
                重新載入
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-foreground">行事曆管理</h1>
        <Button className="bg-primary hover:bg-primary/90">
          <Plus className="h-4 w-4 mr-2" />
          新增預約
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>
              {currentDate.getFullYear()}年 {monthNames[currentDate.getMonth()]}
            </CardTitle>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm" onClick={() => navigateMonth('prev')}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={() => navigateMonth('next')}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-7 gap-1 mb-4">
            {weekDays.map((day, index) => (
              <div key={`weekday-${index}`} className="p-2 text-center font-medium text-muted-foreground bg-muted rounded">
                {day}
              </div>
            ))}
          </div>
          
          <div className="grid grid-cols-7 gap-1">
            {getDaysInMonth(currentDate).map((day, index) => {
              if (!day) {
                return <div key={`empty-${index}`} className="p-2 h-24"></div>;
              }
              
              const dateKey = formatDateKey(day);
              const dayAppointments = appointments[dateKey] || [];
              const today = new Date();
              const isToday = 
                day === today.getDate() && 
                currentDate.getMonth() === today.getMonth() && 
                currentDate.getFullYear() === today.getFullYear();
              
              return (
                <div 
                  key={`day-${day}-${currentDate.getMonth()}-${currentDate.getFullYear()}`} 
                  className={`p-2 h-24 border rounded-lg hover:bg-muted/50 cursor-pointer ${
                    isToday ? 'bg-primary/10 border-primary' : 'border-border'
                  }`}
                >
                  <div className={`font-medium mb-1 ${isToday ? 'text-primary' : ''}`}>
                    {day}
                  </div>
                  <div className="space-y-1">
                    {dayAppointments.slice(0, 2).map((appointment: CalendarAppointment, idx: number) => (
                      <div 
                        key={`appointment-${day}-${idx}-${appointment.time}-${appointment.customer}`} 
                        className="text-xs p-1 bg-primary/20 text-primary rounded truncate cursor-pointer hover:bg-primary/30"
                        title={`${appointment.time} ${appointment.customer} - ${appointment.service} (${appointment.status})`}
                        onClick={() => {
                          // TODO: 顯示預約詳情
                          console.log('預約詳情:', appointment);
                        }}
                      >
                        {appointment.time} {appointment.customer}
                      </div>
                    ))}
                    {dayAppointments.length > 2 && (
                      <div className="text-xs text-muted-foreground">
                        +{dayAppointments.length - 2} 更多
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
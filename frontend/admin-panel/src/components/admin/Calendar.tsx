import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { ChevronLeft, ChevronRight, Plus, Loader2, Clock, User, Phone } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Badge } from '../ui/badge';
import adminApiService from '../../services/api';

interface CalendarAppointment {
  id: string;
  time: string;
  service: string;
  customer: string;
  status: string;
  customer_phone?: string;
  notes?: string;
  appointment_date?: string;
  staff_id?: number;
}

interface TimeSlotDetail {
  date: string;
  time: string;
  appointments: CalendarAppointment[];
}

// 固定時段
const FIXED_TIME_SLOTS = ['12:00', '15:00', '18:00'];

export default function Calendar() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [appointments, setAppointments] = useState<Record<string, CalendarAppointment[]>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeSlot, setSelectedTimeSlot] = useState<TimeSlotDetail | null>(null);
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false);
  const [staffList, setStaffList] = useState<any[]>([]);

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

  // 載入員工列表
  useEffect(() => {
    const loadStaff = async () => {
      try {
        const staff = await adminApiService.getStaff() as any[];
        setStaffList(staff);
      } catch (err) {
        console.error('載入員工列表失敗:', err);
      }
    };
    loadStaff();
  }, []);

  // 當月份改變時重新載入數據
  useEffect(() => {
    loadAppointments(currentDate);
  }, [currentDate]);

  // 根據staff_id獲取員工名稱
  const getStaffName = (staffId?: number) => {
    if (!staffId) return '未指定';
    const staff = staffList.find(s => s.id === staffId);
    return staff?.name || `員工 ${staffId}`;
  };

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
          
          <div className="grid grid-cols-7 gap-3">
            {getDaysInMonth(currentDate).map((day, index) => {
              if (!day) {
                return <div key={`empty-${index}`} className="h-48"></div>;
              }
              
              const dateKey = formatDateKey(day);
              const dayAppointments = appointments[dateKey] || [];
              const today = new Date();
              const isToday = 
                day === today.getDate() && 
                currentDate.getMonth() === today.getMonth() && 
                currentDate.getFullYear() === today.getFullYear();
              
              const checkDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
              const isPast = checkDate < new Date(new Date().setHours(0,0,0,0));
              const isWeekend = checkDate.getDay() === 0 || checkDate.getDay() === 6;
              
              // 將預約按時段分組
              const appointmentsByTime: Record<string, CalendarAppointment[]> = {};
              dayAppointments.forEach(apt => {
                if (!appointmentsByTime[apt.time]) {
                  appointmentsByTime[apt.time] = [];
                }
                appointmentsByTime[apt.time].push(apt);
              });
              
              return (
                <div 
                  key={`day-${day}-${currentDate.getMonth()}-${currentDate.getFullYear()}`} 
                  className={`rounded-xl shadow-sm border-2 overflow-hidden transition-all hover:shadow-md ${
                    isToday 
                      ? 'bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-300 ring-2 ring-blue-200' 
                      : isPast
                        ? 'bg-gray-50 border-gray-200 opacity-60'
                        : isWeekend
                          ? 'bg-amber-50 border-amber-200'
                          : 'bg-white border-gray-200'
                  }`}
                >
                  {/* 日期標題區域 */}
                  <div className={`px-3 py-2 border-b ${
                    isToday 
                      ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white' 
                      : isPast
                        ? 'bg-gray-100 text-gray-500'
                        : isWeekend
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-gray-50 text-gray-700'
                  }`}>
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-base">{day}</span>
                      {isToday && (
                        <span className="text-xs font-medium bg-white/20 px-2 py-0.5 rounded-full">
                          今天
                        </span>
                      )}
                      {dayAppointments.length > 0 && !isToday && (
                        <span className={`text-xs font-medium px-1.5 py-0.5 rounded-full ${
                          isPast ? 'bg-gray-200 text-gray-600' : 'bg-blue-100 text-blue-700'
                        }`}>
                          {dayAppointments.length}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {/* 三個固定時段 */}
                  <div className="p-2 space-y-1.5">
                    {FIXED_TIME_SLOTS.map(timeSlot => {
                      const slotAppointments = appointmentsByTime[timeSlot] || [];
                      const hasAppointments = slotAppointments.length > 0;
                      
                      return (
                        <button
                          key={`${dateKey}-${timeSlot}`}
                          onClick={() => {
                            setSelectedTimeSlot({
                              date: dateKey,
                              time: timeSlot,
                              appointments: slotAppointments
                            });
                            setIsDetailDialogOpen(true);
                          }}
                          className={`w-full group relative rounded-lg px-3 py-2 text-xs font-medium transition-all duration-200 ${
                            hasAppointments 
                              ? 'bg-gradient-to-r from-emerald-100 to-green-100 hover:from-emerald-200 hover:to-green-200 text-emerald-800 border-2 border-emerald-300 hover:border-emerald-400 shadow-sm hover:shadow' 
                              : 'bg-gradient-to-r from-gray-50 to-slate-50 hover:from-gray-100 hover:to-slate-100 text-gray-500 hover:text-gray-700 border border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-1.5">
                              <Clock className="h-3 w-3" />
                              <span>{timeSlot}</span>
                            </div>
                            {hasAppointments ? (
                              <div className="flex items-center space-x-1">
                                <User className="h-3 w-3" />
                                <span className="font-bold">{slotAppointments.length}</span>
                              </div>
                            ) : (
                              <span className="text-[10px] opacity-0 group-hover:opacity-100 transition-opacity">
                                點擊
                              </span>
                            )}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* 時段詳情對話框 */}
      <Dialog open={isDetailDialogOpen} onOpenChange={setIsDetailDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[85vh] overflow-hidden flex flex-col">
          <DialogHeader className="border-b pb-4">
            <DialogTitle className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Clock className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <div className="text-xl font-bold">{selectedTimeSlot?.time}</div>
                <div className="text-sm font-normal text-gray-500">
                  {selectedTimeSlot?.date && new Date(selectedTimeSlot.date).toLocaleDateString('zh-TW', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    weekday: 'long'
                  })}
                </div>
              </div>
              {selectedTimeSlot && selectedTimeSlot.appointments.length > 0 && (
                <Badge variant="secondary" className="ml-auto">
                  {selectedTimeSlot.appointments.length} 個預約
                </Badge>
              )}
            </DialogTitle>
          </DialogHeader>
          
          <div className="flex-1 overflow-y-auto py-4 space-y-3">
            {selectedTimeSlot?.appointments.length === 0 ? (
              <div className="text-center py-12">
                <div className="inline-flex p-4 bg-gray-100 rounded-full mb-4">
                  <Clock className="h-12 w-12 text-gray-400" />
                </div>
                <p className="text-gray-500 font-medium">此時段無預約</p>
                <p className="text-sm text-gray-400 mt-2">點擊「新增預約」來安排預約</p>
              </div>
            ) : (
              <>
                {selectedTimeSlot?.appointments.map((apt, idx) => (
                  <div 
                    key={apt.id || idx} 
                    className="bg-gradient-to-br from-white to-gray-50 border-2 border-gray-200 rounded-xl p-5 hover:border-gray-300 hover:shadow-md transition-all"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center text-white font-bold">
                          {apt.customer?.charAt(0) || '?'}
                        </div>
                        <div>
                          <div className="font-bold text-lg text-gray-800">{apt.customer}</div>
                          {apt.customer_phone && (
                            <div className="text-sm text-gray-500 flex items-center space-x-1">
                              <Phone className="h-3 w-3" />
                              <span>{apt.customer_phone}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {/* 狀態標籤 */}
                      <Badge 
                        className="text-xs px-3 py-1"
                        variant={
                          apt.status === 'confirmed' ? 'default' : 
                          apt.status === 'completed' ? 'secondary' : 
                          apt.status === 'cancelled' ? 'destructive' : 
                          'outline'
                        }
                      >
                        {apt.status === 'confirmed' ? '✓ 已確認' :
                         apt.status === 'completed' ? '✓ 已完成' :
                         apt.status === 'cancelled' ? '✗ 已取消' :
                         apt.status}
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3">
                      {/* 服務項目 */}
                      <div className="bg-white rounded-lg p-3 border border-gray-200">
                        <div className="text-xs text-gray-500 mb-1">服務項目</div>
                        <div className="font-medium text-gray-800">{apt.service}</div>
                      </div>
                      
                      {/* 美甲師 */}
                      <div className="bg-white rounded-lg p-3 border border-gray-200">
                        <div className="text-xs text-gray-500 mb-1">美甲師</div>
                        <div className="font-medium text-gray-800 flex items-center space-x-1">
                          <User className="h-3.5 w-3.5 text-blue-500" />
                          <span>{getStaffName(apt.staff_id)}</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* 備註 */}
                    {apt.notes && (
                      <div className="mt-3 bg-amber-50 border border-amber-200 rounded-lg p-3">
                        <div className="text-xs text-amber-700 font-medium mb-1">📝 備註</div>
                        <div className="text-sm text-amber-900">{apt.notes}</div>
                      </div>
                    )}
                  </div>
                ))}
              </>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
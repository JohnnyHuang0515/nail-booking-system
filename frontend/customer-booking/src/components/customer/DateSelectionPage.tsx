import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Calendar, ChevronLeft, ChevronRight, Clock, UserCog } from 'lucide-react';
import customerApiService from '../../services/api';

interface DateSelectionPageProps {
  onNext: (selectedDate: string, staffId: number) => void;
  selectedStaffId?: number;
}

interface Staff {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  is_active: boolean;
  skills: number[];
}

export default function DateSelectionPage({ onNext, selectedStaffId = 1 }: DateSelectionPageProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [holidays, setHolidays] = useState<string[]>([]);
  const [fullyBookedDates, setFullyBookedDates] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [staffList, setStaffList] = useState<Staff[]>([]);
  const [currentStaffId, setCurrentStaffId] = useState<number>(selectedStaffId);

  // 載入美甲師列表
  useEffect(() => {
    const loadStaff = async () => {
      try {
        const staff = await customerApiService.getStaff();
        setStaffList(staff);
        console.log('✅ 載入美甲師列表:', staff);
      } catch (error) {
        console.error('❌ 載入美甲師列表失敗:', error);
      }
    };
    loadStaff();
  }, []);

  // 載入美甲師休假日資料
  useEffect(() => {
    const loadStaffHolidays = async () => {
      try {
        const holidaysData = await customerApiService.getHolidays();
        // 過濾出當前美甲師的休假
        const staffHolidays = holidaysData.filter((h: any) => h.staff_id === currentStaffId);
        const holidayDates = staffHolidays.map((h: any) => h.holiday_date);
        setHolidays(holidayDates);
        console.log(`✅ 載入美甲師 ${currentStaffId} 的休假日:`, holidayDates);
      } catch (error) {
        console.error('❌ 載入美甲師休假日失敗:', error);
        setHolidays([]);
      } finally {
        setLoading(false);
      }
    };
    
    loadStaffHolidays();
  }, [currentStaffId]);

  // 載入已完全預約的日期
  useEffect(() => {
    const checkFullyBookedDates = async () => {
      // 檢查當月所有日期是否已預約滿
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth();
      const daysInMonth = new Date(year, month + 1, 0).getDate();
      
      const bookedDates: string[] = [];
      
      // 檢查每一天（簡化：只檢查本月）
      for (let day = 1; day <= daysInMonth; day++) {
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const checkDate = new Date(year, month, day);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        // 只檢查今天及未來的日期，且排除休假日
        if (checkDate >= today && !holidays.includes(dateStr)) {
          try {
            // 查詢該日期的可用時段
            const response = await fetch(
              `http://localhost:8000/public/merchants/nail-abc/slots?target_date=${dateStr}&staff_id=${currentStaffId}`
            );
            
            if (response.ok) {
              const slots = await response.json();
              // 檢查固定的三個時段是否都不可用
              const fixedTimes = ['12:00', '15:00', '18:00'];
              const availableSlots = slots.filter((s: any) => 
                fixedTimes.includes(s.start_time) && s.available
              );
              
              // 只有在有時段但都不可用時才標記為"額滿"
              // 如果完全沒有時段(休假日)，不標記為額滿
              if (slots.length > 0 && availableSlots.length === 0) {
                bookedDates.push(dateStr);
              }
            }
          } catch (error) {
            console.error(`檢查日期 ${dateStr} 失敗:`, error);
          }
        }
      }
      
      setFullyBookedDates(bookedDates);
      console.log('已預約滿的日期:', bookedDates);
      console.log('休假日:', holidays);
    };
    
    checkFullyBookedDates();
  }, [currentDate, currentStaffId, holidays]);

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

  const isDateAvailable = (day: number) => {
    if (!day) return false;
    
    const today = new Date();
    const checkDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
    
    // 設置今日開始時間為 00:00:00，避免時區問題
    today.setHours(0, 0, 0, 0);
    checkDate.setHours(0, 0, 0, 0);
    
    // Disable past dates
    if (checkDate < today) return false;
    
    // 限制最多只能往後約30天
    const maxDate = new Date(today);
    maxDate.setDate(today.getDate() + 30);
    if (checkDate > maxDate) return false;
    
    // 檢查是否為休假日
    const dateKey = formatDateKey(day);
    if (holidays.includes(dateKey)) return false;
    
    // 檢查是否為完全預約的日期
    if (fullyBookedDates.includes(dateKey)) return false;
    
    return true;
  };

  const isDateFullyBooked = (day: number) => {
    if (!day) return false;
    const dateKey = formatDateKey(day);
    return fullyBookedDates.includes(dateKey);
  };

  const formatDateKey = (day: number) => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      const today = new Date();
      const maxDate = new Date(today);
      maxDate.setDate(today.getDate() + 30);
      
      if (direction === 'prev') {
        newDate.setMonth(prev.getMonth() - 1);
      } else {
        // 檢查下一個月是否超過30天限制
        const nextMonth = new Date(prev);
        nextMonth.setMonth(prev.getMonth() + 1);
        const firstDayOfNextMonth = new Date(nextMonth.getFullYear(), nextMonth.getMonth(), 1);
        
        if (firstDayOfNextMonth <= maxDate) {
          newDate.setMonth(prev.getMonth() + 1);
        } else {
          return prev; // 不允許導航到下一個月
        }
      }
      return newDate;
    });
    setSelectedDate(''); // Clear selection when changing month
  };

  const handleDateSelect = (day: number) => {
    if (!isDateAvailable(day)) return;
    
    const dateKey = formatDateKey(day);
    setSelectedDate(dateKey);
  };

  const handleNext = () => {
    if (selectedDate) {
      onNext(selectedDate, currentStaffId);
    }
  };

  const handleStaffChange = (staffId: number) => {
    setCurrentStaffId(staffId);
    setSelectedDate(''); // 清除選擇的日期，因為美甲師變了
    setFullyBookedDates([]); // 清除已預約滿的日期，將重新載入
  };

  const monthNames = [
    '一月', '二月', '三月', '四月', '五月', '六月',
    '七月', '八月', '九月', '十月', '十一月', '十二月'
  ];

  const weekDays = ['日', '一', '二', '三', '四', '五', '六'];

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-md mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-foreground mb-2">選擇預約日期</h1>
          <p className="text-muted-foreground">請選擇您希望預約的日期</p>
          
          {/* 美甲師選擇 */}
          {staffList.length > 0 && (
            <Card className="mt-4 mb-2">
              <CardContent className="pt-4 pb-4">
                <div className="flex items-center justify-center space-x-3">
                  <UserCog className="h-5 w-5 text-primary" />
                  <label className="text-sm font-medium text-foreground">選擇美甲師：</label>
                  <select
                    value={currentStaffId}
                    onChange={(e) => handleStaffChange(Number(e.target.value))}
                    className="px-3 py-2 border border-border rounded-lg bg-background text-foreground font-medium focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    {staffList.map(staff => (
                      <option key={staff.id} value={staff.id}>
                        {staff.name}
                      </option>
                    ))}
                  </select>
                </div>
              </CardContent>
            </Card>
          )}
          
          <p className="text-sm text-muted-foreground mt-1">可預約日期：今日起30天內</p>
          {loading && (
            <p className="text-sm text-muted-foreground mt-1">載入休假日資料中...</p>
          )}
          
          {/* 圖例 */}
          <div className="flex justify-center space-x-3 text-xs text-muted-foreground mt-2 flex-wrap gap-2">
            <div className="flex items-center space-x-1.5">
              <div className="w-3 h-3 bg-primary rounded"></div>
              <span>已選擇</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-3 h-3 border-2 border-primary rounded"></div>
              <span>今日</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-3 h-3 bg-orange-50 border-2 border-orange-400 rounded relative">
                <div className="absolute -bottom-0.5 left-0 right-0 text-[6px] text-center text-orange-600 font-bold">滿</div>
              </div>
              <span>已預約滿</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-3 h-3 bg-card border border-border rounded"></div>
              <span>可預約</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-3 h-3 bg-muted/50 rounded"></div>
              <span>不可預約</span>
            </div>
          </div>
        </div>

        {/* Calendar */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle className="text-lg">
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
            {/* Week days header */}
            <div className="grid grid-cols-7 gap-1 mb-2">
              {weekDays.map(day => (
                <div key={day} className="p-2 text-center text-sm font-medium text-muted-foreground">
                  {day}
                </div>
              ))}
            </div>
            
            {/* Calendar days */}
            <div className="grid grid-cols-7 gap-1">
              {getDaysInMonth(currentDate).map((day, index) => {
                if (!day) {
                  return <div key={`empty-${index}`} className="p-2 h-12"></div>;
                }
                
                const dateKey = formatDateKey(day);
                const isHoliday = holidays.includes(dateKey);
                const isFullyBooked = isDateFullyBooked(day);
                const isAvailable = isDateAvailable(day);
                const isSelected = selectedDate === dateKey;
                const today = new Date();
                const isToday = 
                  day === today.getDate() && 
                  currentDate.getMonth() === today.getMonth() && 
                  currentDate.getFullYear() === today.getFullYear();
                
                const checkDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
                checkDate.setHours(0, 0, 0, 0);
                today.setHours(0, 0, 0, 0);
                const isPast = checkDate < today;
                
                return (
                  <button
                    key={`day-${day}-${currentDate.getMonth()}-${currentDate.getFullYear()}`}
                    onClick={() => handleDateSelect(day)}
                    disabled={!isAvailable}
                    className={`
                      p-2 h-12 rounded-lg text-sm font-medium transition-colors relative
                      ${isSelected 
                        ? 'bg-primary text-primary-foreground' 
                        : isHoliday
                          ? 'bg-red-50 border-2 border-red-300 text-red-600 cursor-not-allowed'
                          : isFullyBooked
                            ? 'bg-orange-50 border-2 border-orange-400 text-orange-700 cursor-not-allowed'
                            : isAvailable 
                              ? 'hover:bg-muted text-foreground border border-border' 
                              : isPast
                                ? 'text-muted-foreground/30 cursor-not-allowed bg-muted/30'
                                : 'text-disabled-foreground cursor-not-allowed bg-disabled'
                      }
                      ${isToday && !isSelected ? 'ring-2 ring-primary ring-opacity-50' : ''}
                    `}
                  >
                    <div>{day}</div>
                    {isHoliday && (
                      <div className="absolute -bottom-0.5 left-0 right-0 text-[9px] font-bold text-red-600">
                        休
                      </div>
                    )}
                    {!isHoliday && isFullyBooked && (
                      <div className="absolute -bottom-0.5 left-0 right-0 text-[9px] font-bold text-orange-600">
                        滿
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Selected date info */}
        {selectedDate && (
          <Card className="bg-secondary">
            <CardContent className="pt-6">
              <div className="flex items-center justify-center space-x-2 text-secondary-foreground">
                <Calendar className="h-5 w-5" />
                <span className="font-medium">
                  已選擇：{new Date(selectedDate).toLocaleDateString('zh-TW', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    weekday: 'long'
                  })}
                </span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Legend */}
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm space-y-2">
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 rounded bg-primary"></div>
                <span>已選擇</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 rounded border-2 border-primary"></div>
                <span>今日</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 rounded bg-orange-50 border-2 border-orange-400"></div>
                <span>已預約滿</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 rounded bg-disabled"></div>
                <span>不可預約</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Next button */}
        <Button 
          onClick={handleNext}
          disabled={!selectedDate}
          className="w-full h-12"
        >
          <Clock className="h-4 w-4 mr-2" />
          選擇時段
        </Button>
      </div>
    </div>
  );
}
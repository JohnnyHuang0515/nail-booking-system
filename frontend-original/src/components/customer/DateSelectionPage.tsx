import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Calendar, ChevronLeft, ChevronRight, Clock } from 'lucide-react';

interface DateSelectionPageProps {
  onNext: (selectedDate: string) => void;
}

export default function DateSelectionPage({ onNext }: DateSelectionPageProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<string>('');

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
    
    // Disable past dates
    if (checkDate < today) return false;
    
    // Disable Sundays (0 = Sunday)
    if (checkDate.getDay() === 0) return false;
    
    return true;
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
    setSelectedDate(''); // Clear selection when changing month
  };

  const handleDateSelect = (day: number) => {
    if (!isDateAvailable(day)) return;
    
    const dateKey = formatDateKey(day);
    setSelectedDate(dateKey);
  };

  const handleNext = () => {
    if (selectedDate) {
      onNext(selectedDate);
    }
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
                const isAvailable = isDateAvailable(day);
                const isSelected = selectedDate === dateKey;
                const today = new Date();
                const isToday = 
                  day === today.getDate() && 
                  currentDate.getMonth() === today.getMonth() && 
                  currentDate.getFullYear() === today.getFullYear();
                
                return (
                  <button
                    key={`day-${day}-${currentDate.getMonth()}-${currentDate.getFullYear()}`}
                    onClick={() => handleDateSelect(day)}
                    disabled={!isAvailable}
                    className={`
                      p-2 h-12 rounded-lg text-sm font-medium transition-colors
                      ${isSelected 
                        ? 'bg-primary text-primary-foreground' 
                        : isAvailable 
                          ? 'hover:bg-muted text-foreground' 
                          : 'text-muted-foreground cursor-not-allowed'
                      }
                      ${isToday && !isSelected ? 'ring-2 ring-primary ring-opacity-50' : ''}
                    `}
                  >
                    {day}
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
                <div className="w-4 h-4 rounded bg-muted-foreground opacity-50"></div>
                <span>不可預約（過去日期或休息日）</span>
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
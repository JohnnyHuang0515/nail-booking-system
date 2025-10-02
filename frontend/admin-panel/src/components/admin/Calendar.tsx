import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react';

export default function Calendar() {
  const [currentDate, setCurrentDate] = useState(new Date());
  
  const appointments: Record<string, Array<{ time: string; service: string; customer: string }>> = {
    '2024-01-15': [
      { time: '09:00', service: '基礎保養', customer: '張小姐' },
      { time: '14:00', service: '光療指甲', customer: '李小姐' },
    ],
    '2024-01-16': [
      { time: '10:30', service: '法式指甲', customer: '王小姐' },
    ],
    '2024-01-18': [
      { time: '09:00', service: '手部護理', customer: '陳小姐' },
      { time: '11:00', service: '光療指甲', customer: '林小姐' },
      { time: '15:30', service: '基礎保養', customer: '黃小姐' },
    ],
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

  const monthNames = [
    '一月', '二月', '三月', '四月', '五月', '六月',
    '七月', '八月', '九月', '十月', '十一月', '十二月'
  ];

  const weekDays = ['日', '一', '二', '三', '四', '五', '六'];

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
                    {dayAppointments.slice(0, 2).map((appointment: { time: string; service: string; customer: string }, idx: number) => (
                      <div 
                        key={`appointment-${day}-${idx}-${appointment.time}-${appointment.customer}`} 
                        className="text-xs p-1 bg-primary/20 text-primary rounded truncate"
                        title={`${appointment.time} ${appointment.customer} - ${appointment.service}`}
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
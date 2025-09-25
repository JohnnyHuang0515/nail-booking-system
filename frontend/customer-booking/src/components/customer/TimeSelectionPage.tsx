import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Clock, ChevronLeft, Sparkles } from 'lucide-react';

interface TimeSelectionPageProps {
  selectedDate: string;
  onNext: (selectedTime: string, selectedDate: string) => void;
  onBack: () => void;
}

export default function TimeSelectionPage({ selectedDate, onNext, onBack }: TimeSelectionPageProps) {
  const [selectedTime, setSelectedTime] = useState<string>('');

  // Mock available time slots - in real app this would come from API
  const timeSlots = [
    { time: '09:00', available: true, bookedBy: null },
    { time: '09:30', available: true, bookedBy: null },
    { time: '10:00', available: false, bookedBy: '張小姐' },
    { time: '10:30', available: true, bookedBy: null },
    { time: '11:00', available: true, bookedBy: null },
    { time: '11:30', available: false, bookedBy: '李小姐' },
    { time: '12:00', available: false, bookedBy: '休息時間' },
    { time: '12:30', available: false, bookedBy: '休息時間' },
    { time: '13:00', available: true, bookedBy: null },
    { time: '13:30', available: true, bookedBy: null },
    { time: '14:00', available: true, bookedBy: null },
    { time: '14:30', available: false, bookedBy: '王小姐' },
    { time: '15:00', available: true, bookedBy: null },
    { time: '15:30', available: true, bookedBy: null },
    { time: '16:00', available: true, bookedBy: null },
    { time: '16:30', available: true, bookedBy: null },
    { time: '17:00', available: true, bookedBy: null },
    { time: '17:30', available: true, bookedBy: null },
  ];

  const handleTimeSelect = (time: string) => {
    const slot = timeSlots.find(s => s.time === time);
    if (slot && slot.available) {
      setSelectedTime(time);
    }
  };

  const handleNext = () => {
    if (selectedTime) {
      onNext(selectedTime, selectedDate);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    });
  };

  const morningSlots = timeSlots.filter(slot => {
    const hour = parseInt(slot.time.split(':')[0]);
    return hour >= 9 && hour < 12;
  });

  const afternoonSlots = timeSlots.filter(slot => {
    const hour = parseInt(slot.time.split(':')[0]);
    return hour >= 13 && hour <= 18;
  });

  const TimeSlotGrid = ({ slots, title }: { slots: typeof timeSlots, title: string }) => (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3">
          {slots.map((slot) => {
            const isSelected = selectedTime === slot.time;
            const isLunchBreak = slot.bookedBy === '休息時間';
            
            return (
              <button
                key={slot.time}
                onClick={() => handleTimeSelect(slot.time)}
                disabled={!slot.available}
                className={`
                  p-3 rounded-lg border text-sm font-medium transition-colors relative
                  ${isSelected 
                    ? 'bg-primary text-primary-foreground border-primary' 
                    : slot.available 
                      ? 'border-border hover:bg-muted text-foreground' 
                      : 'border-muted text-muted-foreground cursor-not-allowed bg-muted/50'
                  }
                `}
              >
                <div className="flex items-center justify-center space-x-1">
                  <Clock className="h-3 w-3" />
                  <span>{slot.time}</span>
                </div>
                {!slot.available && (
                  <div className="text-xs mt-1 opacity-75">
                    {isLunchBreak ? '休息' : '已預約'}
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-md mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-foreground mb-2">選擇預約時段</h1>
          <p className="text-muted-foreground">請選擇您希望的預約時段</p>
        </div>

        {/* Selected date */}
        <Card className="bg-secondary">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-sm text-secondary-foreground mb-1">預約日期</div>
              <div className="font-medium text-secondary-foreground">
                {formatDate(selectedDate)}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Morning time slots */}
        <TimeSlotGrid slots={morningSlots} title="上午時段" />

        {/* Afternoon time slots */}
        <TimeSlotGrid slots={afternoonSlots} title="下午時段" />

        {/* Selected time info */}
        {selectedTime && (
          <Card className="bg-primary/10 border-primary/20">
            <CardContent className="pt-6">
              <div className="flex items-center justify-center space-x-2 text-primary">
                <Clock className="h-5 w-5" />
                <span className="font-medium">
                  已選擇時段：{selectedTime}
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
                <div className="w-4 h-4 rounded border border-border bg-background"></div>
                <span>可預約</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 rounded bg-muted"></div>
                <span>已預約或休息時間</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Navigation buttons */}
        <div className="flex space-x-3">
          <Button variant="outline" onClick={onBack} className="flex-1">
            <ChevronLeft className="h-4 w-4 mr-2" />
            返回日期
          </Button>
          <Button 
            onClick={handleNext}
            disabled={!selectedTime}
            className="flex-1"
          >
            <Sparkles className="h-4 w-4 mr-2" />
            選擇服務
          </Button>
        </div>
      </div>
    </div>
  );
}
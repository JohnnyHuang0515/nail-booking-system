import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Clock, ChevronLeft, Sparkles, Loader2 } from 'lucide-react';
import customerApiService from '../../services/api';

interface TimeSelectionPageProps {
  selectedDate: string;
  onNext: (selectedTime: string, selectedDate: string) => void;
  onBack: () => void;
}

interface TimeSlot {
  time: string;
  available: boolean;
  bookedBy?: string;
}

export default function TimeSelectionPage({ selectedDate, onNext, onBack }: TimeSelectionPageProps) {
  const [selectedTime, setSelectedTime] = useState<string>('');
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTimeSlots();
  }, [selectedDate]);

  const loadTimeSlots = async () => {
    try {
      setLoading(true);
      setError(null);
      const slots = await customerApiService.getAvailableTimeSlots(selectedDate);
      setTimeSlots(slots);
    } catch (err) {
      console.error('載入時間段失敗:', err);
      setError('載入時間段失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

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

  // 所有時段都是 12、15、18 點，不需要分組
  const allSlots = timeSlots;

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
                      : 'border-disabled text-disabled-foreground cursor-not-allowed bg-disabled'
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

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-4">
        <div className="max-w-md mx-auto space-y-6">
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin" />
            <span className="ml-2">載入中...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background p-4">
        <div className="max-w-md mx-auto space-y-6">
          <div className="text-center">
            <h1 className="text-2xl font-semibold text-foreground mb-2">選擇預約時段</h1>
            <p className="text-muted-foreground">請選擇您希望的預約時段</p>
          </div>
          <Card className="bg-red-50 border-red-200">
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="text-red-500 mb-4">{error}</div>
                <Button onClick={loadTimeSlots} variant="outline">
                  重新載入
                </Button>
              </div>
            </CardContent>
          </Card>
          <Button variant="outline" onClick={onBack} className="w-full">
            <ChevronLeft className="h-4 w-4 mr-2" />
            返回日期
          </Button>
        </div>
      </div>
    );
  }

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

        {/* Available time slots */}
        {allSlots.length > 0 ? (
          <TimeSlotGrid slots={allSlots} title="可預約時段" />
        ) : (
          <Card className="bg-orange-50 border-orange-200">
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="text-orange-600 mb-2">當日無可預約時段</div>
                <p className="text-sm text-orange-500">
                  可能原因：<br />
                  • 所有時段已被預約<br />
                  • 當日為休假時間<br />
                  • 當日不在營業時間內
                </p>
              </div>
            </CardContent>
          </Card>
        )}

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
                <div className="w-4 h-4 rounded bg-disabled"></div>
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
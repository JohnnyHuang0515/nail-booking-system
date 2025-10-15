import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Clock, ChevronLeft, Sparkles, Loader2 } from 'lucide-react';
import customerApiService from '../../services/api';

interface TimeSelectionPageProps {
  selectedDate: string;
  selectedStaffId?: number;
  onNext: (time: string, date: string) => void;
  onBack: () => void;
}

export default function TimeSelectionPage({ 
  selectedDate,
  selectedStaffId = 1,
  onNext, 
  onBack 
}: TimeSelectionPageProps) {
  const [selectedTime, setSelectedTime] = useState<string>('');
  const [timeSlots, setTimeSlots] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  // 載入時段資料
  useEffect(() => {
    const loadTimeSlots = async () => {
      try {
        setLoading(true);
        setError('');
        
        // 查詢可用時段（使用選擇的美甲師）
        const slots = await customerApiService.getAvailableTimeSlots(
          selectedDate,
          selectedStaffId,  // 使用選擇的美甲師 ID
          []  // 先不指定服務，顯示所有可能時段
        );
        
        // 固定三個時段：12:00, 15:00, 18:00
        const fixedTimes = ['12:00', '15:00', '18:00'];
        const fixedSlots = fixedTimes.map(time => {
          // 檢查後端是否有此時段
          const backendSlot = slots.find(s => s.start_time === time);
          
          const slot = {
            start_time: time,
            end_time: backendSlot?.end_time || calculateEndTime(time, 60),
            available: backendSlot?.available !== undefined ? backendSlot.available : false,
            duration_minutes: 60
          };
          
          console.log(`時段 ${time}:`, {
            找到後端數據: !!backendSlot,
            後端available: backendSlot?.available,
            最終available: slot.available
          });
          
          return slot;
        });
        
        setTimeSlots(fixedSlots);
        console.log('✅ 固定時段:', fixedSlots.map(s => `${s.start_time}(${s.available ? '可用' : '不可用'})`).join(', '));
      } catch (err) {
        console.error('❌ 載入時段失敗:', err);
        setError('無法載入可用時段，請稍後再試');
      } finally {
        setLoading(false);
      }
    };

    if (selectedDate) {
      loadTimeSlots();
    }
  }, [selectedDate, selectedStaffId]);
  
  // 計算結束時間
  const calculateEndTime = (startTime: string, duration: number) => {
    const [hour, minute] = startTime.split(':').map(Number);
    const totalMinutes = hour * 60 + minute + duration;
    const endHour = Math.floor(totalMinutes / 60);
    const endMinute = totalMinutes % 60;
    return `${String(endHour).padStart(2, '0')}:${String(endMinute).padStart(2, '0')}`;
  };

  const handleTimeSelect = (slot: any) => {
    if (!slot.available) return;
    
    // 後端返回的是純時間字串（如 "10:00"），直接使用
    setSelectedTime(slot.start_time);
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

  const formatTimeSlot = (slot: any) => {
    const time = slot.start_time;
    const endTime = slot.end_time;
    
    // 固定三個時段標籤
    let period = '';
    if (time === '12:00') period = '中午';
    else if (time === '15:00') period = '下午';
    else if (time === '18:00') period = '晚上';
    
    return { time, endTime, period };
  };

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-md mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-foreground mb-2">選擇預約時段</h1>
          <p className="text-muted-foreground">{formatDate(selectedDate)}</p>
        </div>

        {/* Loading State */}
        {loading && (
          <Card>
            <CardContent className="pt-12 pb-12">
              <div className="flex flex-col items-center space-y-4">
                <Loader2 className="h-8 w-8 text-primary animate-spin" />
                <p className="text-muted-foreground">載入可用時段中...</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error State */}
        {error && (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center text-red-600">
                <p>{error}</p>
                <Button 
                  variant="outline" 
                  onClick={() => window.location.reload()} 
                  className="mt-4"
                >
                  重新載入
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Time Slots - 三個整點 */}
        {!loading && !error && (
          <>
            {timeSlots.filter((s: any) => s.available).length === 0 && (
              <Card className="border-yellow-300 bg-yellow-50">
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-center space-x-3 text-yellow-700">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">此日期已預約滿</p>
                      <p className="text-sm mt-1">請選擇其他日期或聯繫客服</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <Clock className="h-5 w-5 mr-2 text-primary" />
                  選擇預約時段
                  <Badge variant={timeSlots.filter((s: any) => s.available).length === 0 ? "destructive" : "outline"} className="ml-2">
                    {timeSlots.filter((s: any) => s.available).length} 個可用
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {timeSlots.map((slot: any) => {
                    const { time, period } = formatTimeSlot(slot);
                    const isSelected = selectedTime === time;
                    
                    return (
                      <button
                        key={time}
                        onClick={() => handleTimeSelect(slot)}
                        disabled={!slot.available}
                        className={`
                          w-full p-4 rounded-lg text-left transition-all border-2
                          ${isSelected 
                            ? 'bg-primary text-primary-foreground border-primary' 
                            : slot.available 
                              ? 'bg-card hover:bg-accent text-foreground border-border hover:border-primary/50' 
                              : 'bg-disabled text-disabled-foreground border-disabled cursor-not-allowed opacity-50'
                          }
                        `}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <Clock className="h-5 w-5" />
                            <div>
                              <div className="font-medium text-lg">{time}</div>
                              <div className="text-sm opacity-75">{period}</div>
                            </div>
                          </div>
                          <div>
                            {isSelected ? (
                              <Badge className="bg-primary">已選擇</Badge>
                            ) : (
                              <Badge variant={slot.available ? "default" : "destructive"} className={slot.available ? "bg-green-600" : ""}>
                                {slot.available ? '✓ 可預約' : '✗ 已被預約'}
                              </Badge>
                            )}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {timeSlots.length === 0 && (
              <Card>
                <CardContent className="pt-12 pb-12 text-center">
                  <div className="text-muted-foreground">
                    <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>此日期暫無可用時段</p>
                    <p className="text-sm mt-2">請選擇其他日期</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {/* Selected time info */}
        {selectedTime && (
          <Card className="bg-secondary">
            <CardContent className="pt-6">
              <div className="flex items-center justify-center space-x-2 text-secondary-foreground">
                <Clock className="h-5 w-5" />
                <span className="font-medium">已選擇：{selectedTime}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Navigation buttons */}
        <div className="flex space-x-3">
          <Button variant="outline" onClick={onBack} className="flex-1">
            <ChevronLeft className="h-4 w-4 mr-2" />
            返回日期
          </Button>
          <Button 
            onClick={handleNext}
            disabled={!selectedTime || timeSlots.filter((s: any) => s.available).length === 0}
            className="flex-1"
          >
            <Sparkles className="h-4 w-4 mr-2" />
            {timeSlots.filter((s: any) => s.available).length === 0 ? '無可用時段' : '選擇服務'}
          </Button>
        </div>
      </div>
    </div>
  );
}


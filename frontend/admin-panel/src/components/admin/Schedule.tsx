import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Switch } from '../ui/switch';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { Plus, Clock, Calendar, Trash2, AlertCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from '../ui/dialog';

interface Holiday {
  id: number;
  date: string;
  name: string;
}

export default function Schedule() {
  const [isAddHolidayOpen, setIsAddHolidayOpen] = useState(false);
  const [newHolidayDate, setNewHolidayDate] = useState('');
  const [newHolidayName, setNewHolidayName] = useState('');
  const [error, setError] = useState('');
  const [holidays, setHolidays] = useState<Holiday[]>([]);
  const [loading, setLoading] = useState(true);

  const [weekdays, setWeekdays] = useState([
    { id: 'monday', name: '星期一', enabled: true },
    { id: 'tuesday', name: '星期二', enabled: true },
    { id: 'wednesday', name: '星期三', enabled: true },
    { id: 'thursday', name: '星期四', enabled: true },
    { id: 'friday', name: '星期五', enabled: true },
    { id: 'saturday', name: '星期六', enabled: true },
    { id: 'sunday', name: '星期日', enabled: false },
  ]);

  // 固定時段：12:00, 15:00, 18:00
  const fixedTimeSlots = ['12:00', '15:00', '18:00'];

  // 載入休假資料
  useEffect(() => {
    const loadHolidays = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/schedule/time_off/all');
        if (response.ok) {
          const data = await response.json();
          // 轉換 API 資料格式為前端需要的格式
          const formattedHolidays: Holiday[] = data.map((item: any) => ({
            id: item.id,
            date: item.start_datetime.split('T')[0], // 只取日期部分
            name: item.reason || '休假日'
          }));
          setHolidays(formattedHolidays);
        }
      } catch (err) {
        console.error('載入休假資料錯誤:', err);
        // 如果 API 失敗，使用預設資料
        setHolidays([
          { id: 1, date: '2024-01-01', name: '元旦' },
          { id: 2, date: '2024-02-10', name: '農曆新年' },
          { id: 3, date: '2024-02-11', name: '農曆新年' },
          { id: 4, date: '2024-02-12', name: '農曆新年' },
          { id: 5, date: '2024-04-04', name: '兒童節' },
          { id: 6, date: '2024-04-05', name: '清明節' },
        ]);
      } finally {
        setLoading(false);
      }
    };

    loadHolidays();
  }, []);

  const handleAddHoliday = async () => {
    // 清除之前的錯誤
    setError('');
    
    // 驗證輸入
    if (!newHolidayDate) {
      setError('請選擇日期');
      return;
    }
    
    if (!newHolidayName.trim()) {
      setError('請輸入休假名稱');
      return;
    }
    
    // 檢查日期是否已存在
    const dateExists = holidays.some(h => h.date === newHolidayDate);
    if (dateExists) {
      setError('該日期已設定為休假日');
      return;
    }
    
    try {
      // 調用 API 新增休假
      const response = await fetch('http://localhost:8000/api/v1/schedule/time_off', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_datetime: `${newHolidayDate}T00:00:00`,
          end_datetime: `${newHolidayDate}T23:59:59`,
          reason: newHolidayName.trim()
        }),
      });
      
      if (!response.ok) {
        throw new Error('新增休假失敗');
      }
      
      const result = await response.json();
      
      // 新增休假到狀態中
      const newHoliday: Holiday = {
        id: result.id || Math.max(...holidays.map(h => h.id), 0) + 1,
        date: newHolidayDate,
        name: newHolidayName.trim()
      };
      
      setHolidays(prevHolidays => [...prevHolidays, newHoliday]);
      
      // 重置表單並關閉對話框
      setIsAddHolidayOpen(false);
      setNewHolidayDate('');
      setNewHolidayName('');
      
    } catch (err) {
      console.error('新增休假錯誤:', err);
      setError('新增休假失敗，請稍後再試');
    }
  };

  const handleDeleteHoliday = async (holidayId: number) => {
    try {
      // 調用 API 刪除休假
      const response = await fetch(`http://localhost:8000/api/v1/schedule/time_off/${holidayId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error('刪除休假失敗');
      }
      
      // 從狀態中移除休假
      setHolidays(prevHolidays => prevHolidays.filter(h => h.id !== holidayId));
      
    } catch (err) {
      console.error('刪除休假錯誤:', err);
      setError('刪除休假失敗，請稍後再試');
    }
  };

  const handleWeekdayToggle = (dayId: string) => {
    setWeekdays(prev => prev.map(day => 
      day.id === dayId ? { ...day, enabled: !day.enabled } : day
    ));
  };

  const handleSaveBusinessHours = async () => {
    try {
      // TODO: 調用 API 儲存營業時間設定
      console.log('儲存營業時間:', weekdays);
      // 這裡可以添加 API 調用來儲存設定
    } catch (err) {
      console.error('儲存營業時間錯誤:', err);
      setError('儲存營業時間失敗，請稍後再試');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-foreground">時段管理</h1>
      </div>

      {/* 營業時間設定 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Clock className="h-5 w-5 mr-2 text-primary" />
            營業時間設定
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {weekdays.map((day) => (
              <div key={day.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <Switch 
                    checked={day.enabled} 
                    onCheckedChange={() => handleWeekdayToggle(day.id)}
                  />
                  <Label className="font-medium w-16">{day.name}</Label>
                </div>
                {day.enabled ? (
                  <Badge variant="default" className="bg-green-100 text-green-800">
                    營業中
                  </Badge>
                ) : (
                  <Badge variant="secondary">休息日</Badge>
                )}
              </div>
            ))}
          </div>
          <div className="mt-6">
            <Button 
              className="bg-primary hover:bg-primary/90"
              onClick={handleSaveBusinessHours}
            >
              儲存營業時間
            </Button>
          </div>
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">固定時段</h4>
            <div className="flex space-x-2">
              {fixedTimeSlots.map(time => (
                <Badge key={time} variant="outline" className="bg-white">
                  {time}
                </Badge>
              ))}
            </div>
            <p className="text-sm text-blue-700 mt-2">
              所有營業日都提供 12:00、15:00、18:00 三個固定時段
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 休假管理 */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center">
              <Calendar className="h-5 w-5 mr-2 text-primary" />
              休假管理
            </CardTitle>
            <Dialog open={isAddHolidayOpen} onOpenChange={setIsAddHolidayOpen}>
              <DialogTrigger asChild>
                <Button variant="outline">
                  <Plus className="h-4 w-4 mr-2" />
                  新增休假
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>新增休假日</DialogTitle>
                  <DialogDescription>
                    設定店家的特殊休假日，這些日期將不會開放預約。
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  {error && (
                    <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-md">
                      <AlertCircle className="h-4 w-4 text-red-500" />
                      <span className="text-sm text-red-700">{error}</span>
                    </div>
                  )}
                  <div>
                    <Label htmlFor="holiday-date">日期</Label>
                    <Input 
                      id="holiday-date" 
                      type="date" 
                      value={newHolidayDate}
                      onChange={(e) => {
                        setNewHolidayDate(e.target.value);
                        setError(''); // 清除錯誤當用戶開始輸入
                      }}
                    />
                  </div>
                  <div>
                    <Label htmlFor="holiday-name">休假名稱</Label>
                    <Input 
                      id="holiday-name" 
                      placeholder="請輸入休假名稱"
                      value={newHolidayName}
                      onChange={(e) => {
                        setNewHolidayName(e.target.value);
                        setError(''); // 清除錯誤當用戶開始輸入
                      }}
                    />
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => {
                      setIsAddHolidayOpen(false);
                      setNewHolidayDate('');
                      setNewHolidayName('');
                      setError('');
                    }}>
                      取消
                    </Button>
                    <Button onClick={handleAddHoliday}>
                      確認新增
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="text-sm text-muted-foreground">載入中...</div>
            </div>
          ) : (
            <div className="space-y-3">
              {holidays.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  目前沒有設定休假日
                </div>
              ) : (
                holidays.map((holiday) => (
                  <div key={holiday.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <div className="font-medium">{holiday.name}</div>
                      <div className="text-sm text-muted-foreground">{holiday.date}</div>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleDeleteHoliday(holiday.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 時段間隔設定 */}
      <Card>
        <CardHeader>
          <CardTitle>時段間隔設定</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="slot-interval">預約時段間隔</Label>
              <select id="slot-interval" className="px-3 py-1 border rounded" defaultValue="30">
                <option value="15">15分鐘</option>
                <option value="30">30分鐘</option>
                <option value="60">60分鐘</option>
              </select>
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="advance-booking">提前預約天數</Label>
              <Input id="advance-booking" type="number" defaultValue="30" className="w-24" />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="same-day">允許當日預約</Label>
              <Switch defaultChecked />
            </div>
          </div>
          <div className="mt-6">
            <Button className="bg-primary hover:bg-primary/90">
              儲存設定
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
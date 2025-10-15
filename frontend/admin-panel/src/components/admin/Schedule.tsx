import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Switch } from '../ui/switch';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Plus, Clock, Calendar, Trash2, AlertCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from '../ui/dialog';
import adminApiService from '../../services/api';

interface StaffHoliday {
  id: number;
  staff_id: number;
  staff_name: string;
  holiday_date: string;
  name: string;
  is_recurring: boolean;
}

export default function Schedule() {
  const [isAddHolidayOpen, setIsAddHolidayOpen] = useState(false);
  const [newHolidayDate, setNewHolidayDate] = useState('');
  const [newHolidayName, setNewHolidayName] = useState('');
  const [newHolidayStaffId, setNewHolidayStaffId] = useState<number | null>(null);
  const [error, setError] = useState('');
  const [holidays, setHolidays] = useState<StaffHoliday[]>([]);
  const [staffList, setStaffList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

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

  // 載入營業時間、休假資料和美甲師列表
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError('');
        
        const [holidaysData, businessHours, staffData] = await Promise.all([
          adminApiService.getStaffHolidays(),
          adminApiService.getBusinessHours(),
          adminApiService.getStaff()
        ]);
        
        // 設定美甲師休假日
        setHolidays(holidaysData.map((h: any) => ({
          id: h.id,
          staff_id: h.staff_id,
          staff_name: h.staff_name,
          holiday_date: h.holiday_date,
          name: h.name,
          is_recurring: h.is_recurring
        })));
        
        // 設定美甲師列表
        setStaffList(staffData);
        console.log('✅ 載入美甲師列表:', staffData);
        
        // 設定營業時間
        setWeekdays(prev => prev.map(day => ({
          ...day,
          enabled: businessHours[day.id] || false
        })));
        
      } catch (err) {
        console.error('載入資料錯誤:', err);
        setError('載入資料失敗，請稍後再試');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const handleAddHoliday = async () => {
    // 清除之前的錯誤
    setError('');
    
    // 驗證輸入
    if (!newHolidayDate) {
      setError('請選擇日期');
      return;
    }
    
    if (newHolidayStaffId === null || newHolidayStaffId === undefined) {
      setError('請選擇美甲師');
      return;
    }
    
    if (!newHolidayName.trim()) {
      setError('請輸入休假名稱');
      return;
    }
    
    // 檢查該美甲師該日期是否已設定休假
    const dateExists = holidays.some(h => 
      h.staff_id === newHolidayStaffId && h.holiday_date === newHolidayDate
    );
    if (dateExists) {
      setError('該美甲師該日期已設定休假');
      return;
    }
    
    try {
      const newHoliday = await adminApiService.createStaffHoliday({
        staff_id: newHolidayStaffId,
        holiday_date: newHolidayDate,
        name: newHolidayName.trim(),
        is_recurring: false
      });
      
      const staffName = staffList.find(s => s.id === newHolidayStaffId)?.name || '未知';
      setHolidays(prevHolidays => [...prevHolidays, {
        id: newHoliday.id,
        staff_id: newHoliday.staff_id,
        staff_name: staffName,
        holiday_date: newHoliday.holiday_date,
        name: newHoliday.name,
        is_recurring: newHoliday.is_recurring
      }]);
      
      // 重置表單並關閉對話框
      setIsAddHolidayOpen(false);
      setNewHolidayDate('');
      setNewHolidayName('');
      setNewHolidayStaffId(null);
      
    } catch (err: any) {
      console.error('新增休假錯誤:', err);
      setError(err.message || '新增休假失敗，請稍後再試');
    }
  };

  const handleDeleteHoliday = async (holidayId: number) => {
    try {
      await adminApiService.deleteStaffHoliday(holidayId);
      setHolidays(prevHolidays => prevHolidays.filter(h => h.id !== holidayId));
    } catch (err: any) {
      console.error('刪除休假錯誤:', err);
      setError(err.message || '刪除休假失敗，請稍後再試');
    }
  };

  const handleWeekdayToggle = (dayId: string) => {
    setWeekdays(prev => prev.map(day => 
      day.id === dayId ? { ...day, enabled: !day.enabled } : day
    ));
  };

  const handleSaveBusinessHours = async () => {
    try {
      setSaving(true);
      setError('');
      
      // 轉換為 API 格式
      const businessHours = {
        monday: weekdays.find(d => d.id === 'monday')?.enabled || false,
        tuesday: weekdays.find(d => d.id === 'tuesday')?.enabled || false,
        wednesday: weekdays.find(d => d.id === 'wednesday')?.enabled || false,
        thursday: weekdays.find(d => d.id === 'thursday')?.enabled || false,
        friday: weekdays.find(d => d.id === 'friday')?.enabled || false,
        saturday: weekdays.find(d => d.id === 'saturday')?.enabled || false,
        sunday: weekdays.find(d => d.id === 'sunday')?.enabled || false,
      };
      
      await adminApiService.updateBusinessHours(businessHours);
      
      // 顯示成功訊息
      setError('');
      alert('營業時間設定已儲存！');
      
    } catch (err: any) {
      console.error('儲存營業時間錯誤:', err);
      setError(err.message || '儲存營業時間失敗，請稍後再試');
    } finally {
      setSaving(false);
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
              disabled={saving}
            >
              {saving ? '儲存中...' : '儲存營業時間'}
            </Button>
          </div>
          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-4 w-4 text-red-500" />
                <span className="text-sm text-red-700">{error}</span>
              </div>
            </div>
          )}
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
                    設定美甲師的個人休假日，該美甲師在這些日期將不會開放預約。
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
                    <Label htmlFor="holiday-staff">美甲師</Label>
                    <Select
                      value={newHolidayStaffId !== null ? newHolidayStaffId.toString() : ""}
                      onValueChange={(value) => {
                        setNewHolidayStaffId(value === "" ? null : Number(value));
                        setError('');
                      }}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="請選擇美甲師" />
                      </SelectTrigger>
                      <SelectContent>
                        {staffList.length > 0 ? (
                          staffList.map(staff => (
                            <SelectItem key={staff.id} value={staff.id.toString()}>
                              {staff.name}
                            </SelectItem>
                          ))
                        ) : (
                          <SelectItem value="" disabled>載入中...</SelectItem>
                        )}
                      </SelectContent>
                    </Select>
                  </div>
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
                      setNewHolidayStaffId(null);
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
                      <div className="text-sm text-muted-foreground">
                        {holiday.staff_name} - {holiday.holiday_date}
                      </div>
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
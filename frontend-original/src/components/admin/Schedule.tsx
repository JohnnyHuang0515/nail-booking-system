import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Switch } from '../ui/switch';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { Plus, Clock, Calendar, Trash2 } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';

export default function Schedule() {
  const [isAddHolidayOpen, setIsAddHolidayOpen] = useState(false);

  const weekdays = [
    { id: 'monday', name: '星期一', enabled: true, start: '09:00', end: '18:00' },
    { id: 'tuesday', name: '星期二', enabled: true, start: '09:00', end: '18:00' },
    { id: 'wednesday', name: '星期三', enabled: true, start: '09:00', end: '18:00' },
    { id: 'thursday', name: '星期四', enabled: true, start: '09:00', end: '18:00' },
    { id: 'friday', name: '星期五', enabled: true, start: '09:00', end: '18:00' },
    { id: 'saturday', name: '星期六', enabled: true, start: '10:00', end: '17:00' },
    { id: 'sunday', name: '星期日', enabled: false, start: '10:00', end: '17:00' },
  ];

  const holidays = [
    { id: 1, date: '2024-01-01', name: '元旦' },
    { id: 2, date: '2024-02-10', name: '農曆新年' },
    { id: 3, date: '2024-02-11', name: '農曆新年' },
    { id: 4, date: '2024-02-12', name: '農曆新年' },
    { id: 5, date: '2024-04-04', name: '兒童節' },
    { id: 6, date: '2024-04-05', name: '清明節' },
  ];

  const timeSlots = [
    '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
    '12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
    '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00'
  ];

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
                  <Switch checked={day.enabled} />
                  <Label className="font-medium w-16">{day.name}</Label>
                </div>
                {day.enabled && (
                  <div className="flex items-center space-x-2">
                    <select className="px-3 py-1 border rounded" defaultValue={day.start}>
                      {timeSlots.map(time => (
                        <option key={time} value={time}>{time}</option>
                      ))}
                    </select>
                    <span>至</span>
                    <select className="px-3 py-1 border rounded" defaultValue={day.end}>
                      {timeSlots.map(time => (
                        <option key={time} value={time}>{time}</option>
                      ))}
                    </select>
                  </div>
                )}
                {!day.enabled && (
                  <Badge variant="secondary">休息日</Badge>
                )}
              </div>
            ))}
          </div>
          <div className="mt-6">
            <Button className="bg-primary hover:bg-primary/90">
              儲存營業時間
            </Button>
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
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="holiday-date">日期</Label>
                    <Input id="holiday-date" type="date" />
                  </div>
                  <div>
                    <Label htmlFor="holiday-name">休假名稱</Label>
                    <Input id="holiday-name" placeholder="請輸入休假名稱" />
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => setIsAddHolidayOpen(false)}>
                      取消
                    </Button>
                    <Button onClick={() => setIsAddHolidayOpen(false)}>
                      確認新增
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {holidays.map((holiday) => (
              <div key={holiday.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <div className="font-medium">{holiday.name}</div>
                  <div className="text-sm text-muted-foreground">{holiday.date}</div>
                </div>
                <Button variant="outline" size="sm">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
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
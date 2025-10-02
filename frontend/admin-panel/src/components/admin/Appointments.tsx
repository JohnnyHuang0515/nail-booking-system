import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Plus, Search, Filter, Edit, Trash2, Phone, Loader2 } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from '../ui/dialog';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Textarea } from '../ui/textarea';
import apiService from '../../services/api';

interface Appointment {
  id: string;
  date: string;
  time: string;
  customer: string;
  phone: string;
  service: string;
  duration: number;
  price: number;
  status: string;
}

export default function Appointments() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);

  useEffect(() => {
    loadAppointments();
  }, []);

  const loadAppointments = async () => {
    try {
      setLoading(true);
      setError(null);

      const appointmentsData = await apiService.getAppointments() as Appointment[];
      setAppointments(appointmentsData);
    } catch (err) {
      console.error('載入預約資料失敗:', err);
      setError('載入預約資料失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      'confirmed': { label: '已確認', variant: 'default' as const, color: 'bg-green-100 text-green-700' },
      'pending': { label: '待確認', variant: 'secondary' as const, color: 'bg-yellow-100 text-yellow-700' },
      'in-progress': { label: '進行中', variant: 'default' as const, color: 'bg-blue-100 text-blue-700' },
      'completed': { label: '已完成', variant: 'outline' as const, color: 'bg-gray-100 text-gray-700' },
      'cancelled': { label: '已取消', variant: 'destructive' as const, color: 'bg-red-100 text-red-700' },
    };

    const config = statusConfig[status as keyof typeof statusConfig];
    return (
      <span className={`px-2 py-1 rounded-full text-xs ${config.color}`}>
        {config.label}
      </span>
    );
  };

  const filteredAppointments = appointments.filter(appointment => {
    const matchesSearch = appointment.customer.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         appointment.service.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === 'all' || appointment.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">載入中...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="text-red-500 mb-4">{error}</div>
        <Button onClick={loadAppointments} variant="outline">
          重新載入
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-foreground">預約管理</h1>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-primary hover:bg-primary/90">
              <Plus className="h-4 w-4 mr-2" />
              新增預約
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>新增預約</DialogTitle>
              <DialogDescription>
                請填寫預約的詳細資訊，包括日期、時間、顧客和服務項目。
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="date">日期</Label>
                  <Input id="date" type="date" />
                </div>
                <div>
                  <Label htmlFor="time">時間</Label>
                  <Input id="time" type="time" />
                </div>
              </div>
              <div>
                <Label htmlFor="customer">顧客姓名</Label>
                <Input id="customer" placeholder="請輸入顧客姓名" />
              </div>
              <div>
                <Label htmlFor="phone">聯絡電話</Label>
                <Input id="phone" placeholder="請輸入聯絡電話" />
              </div>
              <div>
                <Label htmlFor="service">服務項目</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="選擇服務項目" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="basic">基礎保養 - $800</SelectItem>
                    <SelectItem value="french">法式指甲 - $1200</SelectItem>
                    <SelectItem value="gel">光療指甲 - $1500</SelectItem>
                    <SelectItem value="care">手部護理 - $1000</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="notes">備註</Label>
                <Textarea id="notes" placeholder="請輸入備註事項" />
              </div>
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                  取消
                </Button>
                <Button onClick={() => setIsAddDialogOpen(false)}>
                  確認新增
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* 搜尋和篩選 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="搜尋顧客姓名或服務項目..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="w-full sm:w-48">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部狀態</SelectItem>
                <SelectItem value="confirmed">已確認</SelectItem>
                <SelectItem value="pending">待確認</SelectItem>
                <SelectItem value="in-progress">進行中</SelectItem>
                <SelectItem value="completed">已完成</SelectItem>
                <SelectItem value="cancelled">已取消</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* 預約列表 */}
      <div className="grid gap-4">
        {filteredAppointments.map((appointment) => (
          <Card key={appointment.id}>
            <CardContent className="pt-6">
              <div className="flex justify-between items-start">
                <div className="space-y-2">
                  <div className="flex items-center space-x-4">
                    <div className="text-lg font-medium">{appointment.customer}</div>
                    {getStatusBadge(appointment.status)}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    <div className="flex items-center space-x-4">
                      <span>{appointment.date} {appointment.time}</span>
                      <span>•</span>
                      <span>{appointment.service}</span>
                      <span>•</span>
                      <span>{appointment.duration}分鐘</span>
                      <span>•</span>
                      <span className="font-medium text-primary">NT${appointment.price}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <div className="flex items-center">
                      <Phone className="h-3 w-3 mr-1" />
                      {appointment.phone}
                    </div>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm">
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredAppointments.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <p className="text-muted-foreground">沒有找到符合條件的預約</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
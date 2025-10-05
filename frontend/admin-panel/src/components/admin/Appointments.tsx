import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Plus, Search, Filter, Edit, Trash2, Phone, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from '../ui/dialog';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Textarea } from '../ui/textarea';
import adminApiService from '../../services/api';

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
  service_id?: string;
  notes?: string;
}

export default function Appointments() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingAppointment, setEditingAppointment] = useState<Appointment | null>(null);
  const [services, setServices] = useState<any[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  useEffect(() => {
    loadAppointments();
    loadServices();
  }, []);

  // 自動隱藏通知
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => {
        setNotification(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const loadAppointments = async () => {
    try {
      setLoading(true);
      setError(null);

      const appointmentsData = await adminApiService.getAppointments() as any[];
      
      // 轉換資料格式以匹配前端介面
      const formattedAppointments = appointmentsData.map(apt => ({
        id: apt.id,
        date: apt.appointment_date,
        time: apt.appointment_time,
        customer: apt.customer_name || '未知客戶',
        phone: apt.customer_phone || '',
        service: apt.service?.name || '未知服務',
        duration: apt.service?.duration_minutes || 0,
        price: apt.service?.price || 0,
        status: apt.status,
        service_id: apt.service_id || apt.service?.id || '',
        notes: apt.notes || ''
      }));
      
      setAppointments(formattedAppointments);
    } catch (err) {
      console.error('載入預約資料失敗:', err);
      setError('載入預約資料失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  const loadServices = async () => {
    try {
      const servicesData = await adminApiService.getServices() as any[];
      setServices(servicesData || []);
    } catch (err) {
      console.error('載入服務資料失敗:', err);
    }
  };

  // 新增預約
  const handleCreateAppointment = async (formData: any) => {
    try {
      setSubmitting(true);
      const appointmentData = {
        customer_name: formData.customer,
        customer_phone: formData.phone,
        customer_email: formData.email || '',
        service_id: formData.service_id,
        appointment_date: formData.date,
        appointment_time: formData.time,
        notes: formData.notes || ''
      };

      await adminApiService.createAppointment(appointmentData);
      await loadAppointments(); // 重新載入列表
      setIsAddDialogOpen(false);
      setNotification({ type: 'success', message: '預約新增成功！' });
    } catch (err) {
      console.error('新增預約失敗:', err);
      setNotification({ type: 'error', message: '新增預約失敗，請稍後再試' });
    } finally {
      setSubmitting(false);
    }
  };

  // 編輯預約
  const handleEditAppointment = (appointment: Appointment) => {
    setEditingAppointment(appointment);
    setIsEditDialogOpen(true);
  };

  const handleUpdateAppointment = async (formData: any) => {
    if (!editingAppointment) return;

    try {
      setSubmitting(true);
      const appointmentData = {
        service_id: formData.service_id,
        appointment_date: formData.date,
        appointment_time: formData.time,
        status: formData.status
      };

      await adminApiService.updateAppointment(editingAppointment.id, appointmentData);
      await loadAppointments(); // 重新載入列表
      setIsEditDialogOpen(false);
      setEditingAppointment(null);
      setNotification({ type: 'success', message: '預約更新成功！' });
    } catch (err) {
      console.error('更新預約失敗:', err);
      setNotification({ type: 'error', message: '更新預約失敗，請稍後再試' });
    } finally {
      setSubmitting(false);
    }
  };

  // 刪除預約
  const handleDeleteAppointment = async (appointmentId: string) => {
    if (!window.confirm('確定要刪除這個預約嗎？此操作無法復原。')) {
      return;
    }

    try {
      setSubmitting(true);
      await adminApiService.deleteAppointment(appointmentId);
      await loadAppointments(); // 重新載入列表
      setNotification({ type: 'success', message: '預約刪除成功！' });
    } catch (err) {
      console.error('刪除預約失敗:', err);
      setNotification({ type: 'error', message: '刪除預約失敗，請稍後再試' });
    } finally {
      setSubmitting(false);
    }
  };

  // 更新預約狀態
  const handleUpdateStatus = async (appointmentId: string, newStatus: string) => {
    try {
      setSubmitting(true);
      const appointmentData = { status: newStatus };
      await adminApiService.updateAppointment(appointmentId, appointmentData);
      await loadAppointments(); // 重新載入列表
      setNotification({ type: 'success', message: '狀態更新成功！' });
    } catch (err) {
      console.error('更新狀態失敗:', err);
      setNotification({ type: 'error', message: '更新狀態失敗，請稍後再試' });
    } finally {
      setSubmitting(false);
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
    const customer = appointment.customer || '';
    const service = appointment.service || '';
    const matchesSearch = customer.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         service.toLowerCase().includes(searchTerm.toLowerCase());
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
      {/* 通知訊息 */}
      {notification && (
        <div className={`p-4 rounded-md ${
          notification.type === 'success' ? 'bg-green-50 border border-green-200 text-green-700' :
          notification.type === 'error' ? 'bg-red-50 border border-red-200 text-red-700' :
          'bg-blue-50 border border-blue-200 text-blue-700'
        }`}>
          <div className="flex justify-between items-center">
            <span>{notification.message}</span>
            <button 
              onClick={() => setNotification(null)}
              className="text-current hover:opacity-70"
            >
              ×
            </button>
          </div>
        </div>
      )}

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
            <CreateAppointmentForm 
              services={services}
              onSubmit={handleCreateAppointment}
              onCancel={() => setIsAddDialogOpen(false)}
              submitting={submitting}
            />
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
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleEditAppointment(appointment)}
                    disabled={submitting}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleDeleteAppointment(appointment.id)}
                    disabled={submitting}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                  {appointment.status === 'pending' && (
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleUpdateStatus(appointment.id, 'confirmed')}
                      disabled={submitting}
                      className="text-green-600 hover:text-green-700"
                    >
                      <CheckCircle className="h-4 w-4" />
                    </Button>
                  )}
                  {appointment.status === 'confirmed' && (
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleUpdateStatus(appointment.id, 'completed')}
                      disabled={submitting}
                      className="text-blue-600 hover:text-blue-700"
                    >
                      <CheckCircle className="h-4 w-4" />
                    </Button>
                  )}
                  {(appointment.status === 'pending' || appointment.status === 'confirmed') && (
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleUpdateStatus(appointment.id, 'cancelled')}
                      disabled={submitting}
                      className="text-red-600 hover:text-red-700"
                    >
                      <XCircle className="h-4 w-4" />
                    </Button>
                  )}
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

      {/* 編輯預約對話框 */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>編輯預約</DialogTitle>
            <DialogDescription>
              修改預約的詳細資訊。
            </DialogDescription>
          </DialogHeader>
          {editingAppointment && (
            <EditAppointmentForm 
              appointment={editingAppointment}
              services={services}
              onSubmit={handleUpdateAppointment}
              onCancel={() => {
                setIsEditDialogOpen(false);
                setEditingAppointment(null);
              }}
              submitting={submitting}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

// 新增預約表單元件
interface CreateAppointmentFormProps {
  services: any[];
  onSubmit: (data: any) => void;
  onCancel: () => void;
  submitting: boolean;
}

function CreateAppointmentForm({ services, onSubmit, onCancel, submitting }: CreateAppointmentFormProps) {
  const [formData, setFormData] = useState({
    date: '',
    time: '',
    customer: '',
    phone: '',
    email: '',
    service_id: '',
    notes: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.date || !formData.time || !formData.customer || !formData.phone || !formData.service_id) {
      // 表單驗證失敗，不提交
      return;
    }
    onSubmit(formData);
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="date">日期 *</Label>
          <Input 
            id="date" 
            type="date" 
            value={formData.date}
            onChange={(e) => handleInputChange('date', e.target.value)}
            required
          />
        </div>
        <div>
          <Label htmlFor="time">時間 *</Label>
          <Input 
            id="time" 
            type="time" 
            value={formData.time}
            onChange={(e) => handleInputChange('time', e.target.value)}
            required
          />
        </div>
      </div>
      <div>
        <Label htmlFor="customer">顧客姓名 *</Label>
        <Input 
          id="customer" 
          placeholder="請輸入顧客姓名" 
          value={formData.customer}
          onChange={(e) => handleInputChange('customer', e.target.value)}
          required
        />
      </div>
      <div>
        <Label htmlFor="phone">聯絡電話 *</Label>
        <Input 
          id="phone" 
          placeholder="請輸入聯絡電話" 
          value={formData.phone}
          onChange={(e) => handleInputChange('phone', e.target.value)}
          required
        />
      </div>
      <div>
        <Label htmlFor="email">電子信箱</Label>
        <Input 
          id="email" 
          type="email"
          placeholder="請輸入電子信箱" 
          value={formData.email}
          onChange={(e) => handleInputChange('email', e.target.value)}
        />
      </div>
      <div>
        <Label htmlFor="service">服務項目 *</Label>
        <Select value={formData.service_id} onValueChange={(value) => handleInputChange('service_id', value)}>
          <SelectTrigger>
            <SelectValue placeholder="選擇服務項目" />
          </SelectTrigger>
          <SelectContent>
            {services.map((service) => (
              <SelectItem key={service.id} value={service.id}>
                {service.name} - ${service.price} ({service.duration_minutes}分鐘)
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label htmlFor="notes">備註</Label>
        <Textarea 
          id="notes" 
          placeholder="請輸入備註事項" 
          value={formData.notes}
          onChange={(e) => handleInputChange('notes', e.target.value)}
        />
      </div>
      <div className="flex justify-end space-x-2">
        <Button type="button" variant="outline" onClick={onCancel} disabled={submitting}>
          取消
        </Button>
        <Button type="submit" disabled={submitting}>
          {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : '確認新增'}
        </Button>
      </div>
    </form>
  );
}

// 編輯預約表單元件
interface EditAppointmentFormProps {
  appointment: Appointment;
  services: any[];
  onSubmit: (data: any) => void;
  onCancel: () => void;
  submitting: boolean;
}

function EditAppointmentForm({ appointment, services, onSubmit, onCancel, submitting }: EditAppointmentFormProps) {
  const [formData, setFormData] = useState({
    date: appointment.date,
    time: appointment.time,
    service_id: appointment.service_id || '',
    status: appointment.status
  });


  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="edit-date">日期</Label>
          <Input 
            id="edit-date" 
            type="date" 
            value={formData.date}
            onChange={(e) => handleInputChange('date', e.target.value)}
          />
        </div>
        <div>
          <Label htmlFor="edit-time">時間</Label>
          <Input 
            id="edit-time" 
            type="time" 
            value={formData.time}
            onChange={(e) => handleInputChange('time', e.target.value)}
          />
        </div>
      </div>
      <div>
        <Label htmlFor="edit-service">服務項目</Label>
        <Select value={formData.service_id} onValueChange={(value) => handleInputChange('service_id', value)}>
          <SelectTrigger>
            <SelectValue placeholder="選擇服務項目" />
          </SelectTrigger>
          <SelectContent>
            {services.map((service) => (
              <SelectItem key={service.id} value={service.id}>
                {service.name} - ${service.price} ({service.duration_minutes}分鐘)
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label htmlFor="edit-status">狀態</Label>
        <Select value={formData.status} onValueChange={(value) => handleInputChange('status', value)}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="pending">待確認</SelectItem>
            <SelectItem value="confirmed">已確認</SelectItem>
            <SelectItem value="completed">已完成</SelectItem>
            <SelectItem value="cancelled">已取消</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="flex justify-end space-x-2">
        <Button type="button" variant="outline" onClick={onCancel} disabled={submitting}>
          取消
        </Button>
        <Button type="submit" disabled={submitting}>
          {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : '確認更新'}
        </Button>
      </div>
    </form>
  );
}
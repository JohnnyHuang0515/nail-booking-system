import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Plus, Search, Phone, Mail, Calendar, Edit, Trash2, User, Loader2 } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from '../ui/dialog';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import apiService from '../../services/api';

interface Customer {
  id: string;
  name: string;
  phone: string;
  email: string;
  totalAppointments: number;
  lastVisit: string;
  totalSpent: number;
  notes: string;
  status: string;
  birthDate: string;
}

export default function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // 使用正確的商家ID
      const merchantId = '5a89c20e-befd-4bb3-a43b-e185ab0e4841';

      const customersData = await apiService.getCustomers(merchantId) as Customer[];
      setCustomers(customersData);
    } catch (err) {
      console.error('載入客戶資料失敗:', err);
      setError('載入客戶資料失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      'active': { label: '活躍', color: 'bg-green-100 text-green-700' },
      'vip': { label: 'VIP', color: 'bg-purple-100 text-purple-700' },
      'new': { label: '新客戶', color: 'bg-blue-100 text-blue-700' },
      'inactive': { label: '非活躍', color: 'bg-gray-100 text-gray-700' },
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.active;
    return (
      <span className={`px-2 py-1 rounded-full text-xs ${config.color}`}>
        {config.label}
      </span>
    );
  };

  const filteredCustomers = customers.filter(customer =>
    customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.phone.includes(searchTerm) ||
    customer.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
        <Button onClick={loadCustomers} variant="outline">
          重新載入
        </Button>
      </div>
    );
  }

  const CustomerForm = ({ customer, onClose }: { customer?: any, onClose: () => void }) => (
    <div className="space-y-4">
      <div>
        <Label htmlFor="customer-name">姓名</Label>
        <Input 
          id="customer-name" 
          placeholder="請輸入顧客姓名" 
          defaultValue={customer?.name || ''}
        />
      </div>
      <div>
        <Label htmlFor="customer-phone">聯絡電話</Label>
        <Input 
          id="customer-phone" 
          placeholder="請輸入聯絡電話" 
          defaultValue={customer?.phone || ''}
        />
      </div>
      <div>
        <Label htmlFor="customer-email">電子郵件</Label>
        <Input 
          id="customer-email" 
          type="email"
          placeholder="請輸入電子郵件" 
          defaultValue={customer?.email || ''}
        />
      </div>
      <div>
        <Label htmlFor="customer-birth">生日</Label>
        <Input 
          id="customer-birth" 
          type="date"
          defaultValue={customer?.birthDate || ''}
        />
      </div>
      <div>
        <Label htmlFor="customer-notes">備註</Label>
        <Textarea 
          id="customer-notes" 
          placeholder="請輸入備註資訊" 
          defaultValue={customer?.notes || ''}
        />
      </div>
      <div className="flex justify-end space-x-2">
        <Button variant="outline" onClick={onClose}>
          取消
        </Button>
        <Button onClick={onClose}>
          {customer ? '更新' : '新增'}顧客
        </Button>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-foreground">顧客管理</h1>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-primary hover:bg-primary/90">
              <Plus className="h-4 w-4 mr-2" />
              新增顧客
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>新增顧客</DialogTitle>
              <DialogDescription>
                請填寫顧客的基本資訊，包括姓名、電話和電子郵件。
              </DialogDescription>
            </DialogHeader>
            <CustomerForm onClose={() => setIsAddDialogOpen(false)} />
          </DialogContent>
        </Dialog>
      </div>

      {/* 顧客統計 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{customers.length}</div>
            <p className="text-sm text-muted-foreground">總顧客數</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{customers.filter(c => c.status === 'vip').length}</div>
            <p className="text-sm text-muted-foreground">VIP顧客</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{customers.filter(c => c.status === 'new').length}</div>
            <p className="text-sm text-muted-foreground">新顧客</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">
              NT${Math.round(customers.reduce((sum, c) => sum + c.totalSpent, 0) / customers.length)}
            </div>
            <p className="text-sm text-muted-foreground">平均消費</p>
          </CardContent>
        </Card>
      </div>

      {/* 搜尋 */}
      <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="搜尋顧客姓名、電話或電子郵件..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* 顧客列表 */}
      <div className="grid gap-4">
        {filteredCustomers.map((customer) => (
          <Card key={customer.id}>
            <CardContent className="pt-6">
              <div className="flex justify-between items-start">
                <div className="space-y-3 flex-1">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-3">
                      <User className="h-5 w-5 text-muted-foreground" />
                      <div className="text-lg font-medium">{customer.name}</div>
                    </div>
                    {getStatusBadge(customer.status)}
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div className="space-y-2">
                      <div className="flex items-center text-muted-foreground">
                        <Phone className="h-3 w-3 mr-2" />
                        {customer.phone}
                      </div>
                      <div className="flex items-center text-muted-foreground">
                        <Mail className="h-3 w-3 mr-2" />
                        {customer.email}
                      </div>
                      <div className="flex items-center text-muted-foreground">
                        <Calendar className="h-3 w-3 mr-2" />
                        最後到訪：{customer.lastVisit}
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div>總預約次數：<span className="font-medium">{customer.totalAppointments}</span></div>
                      <div>總消費金額：<span className="font-medium text-primary">NT${customer.totalSpent}</span></div>
                      <div>平均消費：<span className="font-medium">NT${Math.round(customer.totalSpent / customer.totalAppointments)}</span></div>
                    </div>
                  </div>
                  
                  {customer.notes && (
                    <div className="text-sm text-muted-foreground bg-muted p-3 rounded">
                      <strong>備註：</strong>{customer.notes}
                    </div>
                  )}
                </div>
                
                <div className="flex space-x-2 ml-4">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button variant="outline" size="sm">
                        <Edit className="h-4 w-4" />
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-md">
                      <DialogHeader>
                        <DialogTitle>編輯顧客資料</DialogTitle>
                      </DialogHeader>
                      <CustomerForm 
                        customer={customer} 
                        onClose={() => {}} 
                      />
                    </DialogContent>
                  </Dialog>
                  <Button variant="outline" size="sm">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredCustomers.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <p className="text-muted-foreground">沒有找到符合條件的顧客</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
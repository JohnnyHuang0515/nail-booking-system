import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Plus, Edit, Trash2, Clock, DollarSign, Loader2 } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from '../ui/dialog';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Switch } from '../ui/switch';
import apiService from '../../services/api';

interface Service {
  id: string;
  merchant_id: string;
  name: string;
  price: number;
  duration_minutes: number;
  is_active: boolean;
  description?: string;
  image?: string | null;
}

export default function Services() {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);

  useEffect(() => {
    loadServices();
  }, []);

  const loadServices = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // 使用正確的商家ID
      const merchantId = '5a89c20e-befd-4bb3-a43b-e185ab0e4841';

      const servicesData = await apiService.getServices(merchantId) as Service[];
      setServices(servicesData);
    } catch (err) {
      console.error('載入服務資料失敗:', err);
      setError('載入服務資料失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateService = async (serviceData: any) => {
    try {
      // 使用正確的商家ID
      const merchantId = '5a89c20e-befd-4bb3-a43b-e185ab0e4841';

      await apiService.createService({
        ...serviceData,
        merchant_id: merchantId
      });
      
      setIsAddDialogOpen(false);
      loadServices();
    } catch (err) {
      console.error('建立服務失敗:', err);
      setError('建立服務失敗，請稍後再試');
    }
  };

  const handleUpdateService = async (serviceId: string, serviceData: Partial<Service>) => {
    try {
      await apiService.updateService(serviceId, serviceData);
      loadServices();
    } catch (err) {
      console.error('更新服務失敗:', err);
      setError('更新服務失敗，請稍後再試');
    }
  };

  const handleDeleteService = async (serviceId: string) => {
    if (!window.confirm('確定要刪除此服務嗎？')) {
      return;
    }
    
    try {
      await apiService.deleteService(serviceId);
      loadServices();
    } catch (err) {
      console.error('刪除服務失敗:', err);
      setError('刪除服務失敗，請稍後再試');
    }
  };

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
        <Button onClick={loadServices} variant="outline">
          重新載入
        </Button>
      </div>
    );
  }


  const ServiceForm = ({ service, onClose, onSubmit }: { 
    service?: Service | null, 
    onClose: () => void,
    onSubmit: (data: any) => void 
  }) => {
    const [formData, setFormData] = useState({
      name: service?.name || '',
      description: service?.description || '',
      duration_minutes: service?.duration_minutes || 60,
      price: service?.price || 0,
      is_active: service?.is_active ?? true
    });

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      onSubmit(formData);
    };

    return (
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="service-name">服務名稱</Label>
          <Input 
            id="service-name" 
            placeholder="請輸入服務名稱" 
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            required
          />
        </div>
        <div>
          <Label htmlFor="service-description">服務描述</Label>
          <Textarea 
            id="service-description" 
            placeholder="請輸入服務描述" 
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="service-duration">服務時間（分鐘）</Label>
            <Input 
              id="service-duration" 
              type="number" 
              placeholder="60" 
              value={formData.duration_minutes}
              onChange={(e) => setFormData({...formData, duration_minutes: parseInt(e.target.value) || 60})}
              required
            />
          </div>
          <div>
            <Label htmlFor="service-price">價格（NT$）</Label>
            <Input 
              id="service-price" 
              type="number" 
              placeholder="800" 
              value={formData.price}
              onChange={(e) => setFormData({...formData, price: parseInt(e.target.value) || 0})}
              required
            />
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Switch 
            id="service-active" 
            checked={formData.is_active}
            onCheckedChange={(checked) => setFormData({...formData, is_active: checked})}
          />
          <Label htmlFor="service-active">啟用此服務</Label>
        </div>
        <div className="flex justify-end space-x-2">
          <Button type="button" variant="outline" onClick={onClose}>
            取消
          </Button>
          <Button type="submit">
            {service ? '更新' : '新增'}服務
          </Button>
        </div>
      </form>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-foreground">服務管理</h1>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-primary hover:bg-primary/90">
              <Plus className="h-4 w-4 mr-2" />
              新增服務
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>新增服務項目</DialogTitle>
              <DialogDescription>
                請填寫服務項目的詳細資訊，包括名稱、描述、價格和時長。
              </DialogDescription>
            </DialogHeader>
            <ServiceForm 
              onClose={() => setIsAddDialogOpen(false)} 
              onSubmit={handleCreateService}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* 服務統計 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{services.length}</div>
            <p className="text-sm text-muted-foreground">總服務項目</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{services.filter(s => s.is_active).length}</div>
            <p className="text-sm text-muted-foreground">啟用服務</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">
              NT${services.length > 0 ? Math.round(services.reduce((sum, s) => sum + s.price, 0) / services.length) : 0}
            </div>
            <p className="text-sm text-muted-foreground">平均價格</p>
          </CardContent>
        </Card>
      </div>

      {/* 服務列表 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">服務項目</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {services.map((service) => (
              <div key={service.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="font-medium">{service.name}</h3>
                    {service.is_active ? (
                      <Badge className="bg-green-100 text-green-700">啟用</Badge>
                    ) : (
                      <Badge variant="secondary">停用</Badge>
                    )}
                  </div>
                  {service.description && (
                    <p className="text-sm text-muted-foreground mb-2">{service.description}</p>
                  )}
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <div className="flex items-center">
                      <Clock className="h-3 w-3 mr-1" />
                      {service.duration_minutes}分鐘
                    </div>
                    <div className="flex items-center">
                      <DollarSign className="h-3 w-3 mr-1" />
                      NT${service.price}
                    </div>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button variant="outline" size="sm">
                        <Edit className="h-4 w-4" />
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-md">
                      <DialogHeader>
                        <DialogTitle>編輯服務項目</DialogTitle>
                        <DialogDescription>
                          修改服務項目的詳細資訊，包括名稱、描述、價格和時長。
                        </DialogDescription>
                      </DialogHeader>
                      <ServiceForm 
                        service={service} 
                        onClose={() => {}} 
                        onSubmit={(data) => handleUpdateService(service.id, data)}
                      />
                    </DialogContent>
                  </Dialog>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleDeleteService(service.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
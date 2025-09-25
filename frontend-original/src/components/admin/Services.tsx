import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Plus, Edit, Trash2, Clock, DollarSign } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Switch } from '../ui/switch';

export default function Services() {
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [editingService, setEditingService] = useState(null);

  const services = [
    {
      id: 1,
      name: '基礎保養',
      description: '基礎指甲修剪、去角質、保濕護理',
      duration: 60,
      price: 800,
      category: '基礎護理',
      active: true,
      image: null
    },
    {
      id: 2,
      name: '法式指甲',
      description: '經典法式風格，優雅簡約',
      duration: 90,
      price: 1200,
      category: '彩繪指甲',
      active: true,
      image: null
    },
    {
      id: 3,
      name: '光療指甲',
      description: '持久光療，多種顏色選擇',
      duration: 120,
      price: 1500,
      category: '光療系列',
      active: true,
      image: null
    },
    {
      id: 4,
      name: '手部護理',
      description: '深層手部護理，包含按摩和保濕',
      duration: 75,
      price: 1000,
      category: '護理療程',
      active: true,
      image: null
    },
    {
      id: 5,
      name: '指甲彩繪',
      description: '個性化指甲彩繪設計',
      duration: 150,
      price: 2000,
      category: '彩繪指甲',
      active: true,
      image: null
    },
    {
      id: 6,
      name: '足部護理',
      description: '足部深層護理，去除老廢角質',
      duration: 90,
      price: 1200,
      category: '護理療程',
      active: false,
      image: null
    },
  ];

  const categories = ['基礎護理', '彩繪指甲', '光療系列', '護理療程'];

  const ServiceForm = ({ service, onClose }: { service?: any, onClose: () => void }) => (
    <div className="space-y-4">
      <div>
        <Label htmlFor="service-name">服務名稱</Label>
        <Input 
          id="service-name" 
          placeholder="請輸入服務名稱" 
          defaultValue={service?.name || ''}
        />
      </div>
      <div>
        <Label htmlFor="service-category">服務分類</Label>
        <select 
          id="service-category" 
          className="w-full px-3 py-2 border rounded-md"
          defaultValue={service?.category || ''}
        >
          <option value="">選擇分類</option>
          {categories.map(category => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="service-duration">服務時間（分鐘）</Label>
          <Input 
            id="service-duration" 
            type="number" 
            placeholder="60" 
            defaultValue={service?.duration || ''}
          />
        </div>
        <div>
          <Label htmlFor="service-price">價格（NT$）</Label>
          <Input 
            id="service-price" 
            type="number" 
            placeholder="800" 
            defaultValue={service?.price || ''}
          />
        </div>
      </div>
      <div>
        <Label htmlFor="service-description">服務描述</Label>
        <Textarea 
          id="service-description" 
          placeholder="請輸入服務描述" 
          defaultValue={service?.description || ''}
        />
      </div>
      <div className="flex items-center space-x-2">
        <Switch id="service-active" defaultChecked={service?.active !== false} />
        <Label htmlFor="service-active">啟用此服務</Label>
      </div>
      <div className="flex justify-end space-x-2">
        <Button variant="outline" onClick={onClose}>
          取消
        </Button>
        <Button onClick={onClose}>
          {service ? '更新' : '新增'}服務
        </Button>
      </div>
    </div>
  );

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
            </DialogHeader>
            <ServiceForm onClose={() => setIsAddDialogOpen(false)} />
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
            <div className="text-2xl font-bold">{services.filter(s => s.active).length}</div>
            <p className="text-sm text-muted-foreground">啟用服務</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{categories.length}</div>
            <p className="text-sm text-muted-foreground">服務分類</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">
              NT${Math.round(services.reduce((sum, s) => sum + s.price, 0) / services.length)}
            </div>
            <p className="text-sm text-muted-foreground">平均價格</p>
          </CardContent>
        </Card>
      </div>

      {/* 服務列表 */}
      <div className="grid gap-4">
        {categories.map(category => {
          const categoryServices = services.filter(service => service.category === category);
          if (categoryServices.length === 0) return null;

          return (
            <Card key={category}>
              <CardHeader>
                <CardTitle className="text-lg">{category}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  {categoryServices.map((service) => (
                    <div key={service.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="font-medium">{service.name}</h3>
                          {service.active ? (
                            <Badge className="bg-green-100 text-green-700">啟用</Badge>
                          ) : (
                            <Badge variant="secondary">停用</Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">{service.description}</p>
                        <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                          <div className="flex items-center">
                            <Clock className="h-3 w-3 mr-1" />
                            {service.duration}分鐘
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
                            </DialogHeader>
                            <ServiceForm 
                              service={service} 
                              onClose={() => {}} 
                            />
                          </DialogContent>
                        </Dialog>
                        <Button variant="outline" size="sm">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
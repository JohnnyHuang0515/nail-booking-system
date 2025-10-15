import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Plus, Edit, Trash2, Loader2, UserCog, Phone, Mail, CheckCircle, XCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import adminApiService from '../../services/api';

interface Staff {
  id: number;
  merchant_id: string;
  name: string;
  email?: string;
  phone?: string;
  is_active: boolean;
  skills: number[];
  working_hours: Array<{
    day_of_week: string;
    start_time: string;
    end_time: string;
  }>;
}

interface Service {
  id: number;
  name: string;
}

export default function Staff() {
  const [staffList, setStaffList] = useState<Staff[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // 對話框狀態
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingStaff, setEditingStaff] = useState<Staff | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  
  // 表單狀態
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    skills: [] as number[],
    is_active: true,
  });

  useEffect(() => {
    loadStaff();
    loadServices();
  }, []);

  const loadStaff = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await adminApiService.getStaff();
      setStaffList(data);
    } catch (err) {
      console.error('載入美甲師列表失敗:', err);
      setError('無法載入美甲師列表');
    } finally {
      setLoading(false);
    }
  };

  const loadServices = async () => {
    try {
      const data = await adminApiService.getServices();
      setServices(data);
    } catch (err) {
      console.error('載入服務列表失敗:', err);
    }
  };

  const openCreateDialog = () => {
    setEditingStaff(null);
    setFormData({
      name: '',
      email: '',
      phone: '',
      skills: [],
      is_active: true,
    });
    setIsDialogOpen(true);
  };

  const openEditDialog = (staff: Staff) => {
    setEditingStaff(staff);
    setFormData({
      name: staff.name,
      email: staff.email || '',
      phone: staff.phone || '',
      skills: staff.skills || [],
      is_active: staff.is_active,
    });
    setIsDialogOpen(true);
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      
      if (editingStaff) {
        // 更新
        await adminApiService.updateStaff(editingStaff.id, formData);
      } else {
        // 新增
        await adminApiService.createStaff(formData);
      }
      
      setIsDialogOpen(false);
      loadStaff();
    } catch (err) {
      console.error('儲存美甲師失敗:', err);
      alert(`儲存失敗: ${err}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (staff: Staff) => {
    if (!window.confirm(`確定要刪除美甲師 "${staff.name}" 嗎？`)) {
      return;
    }
    
    try {
      await adminApiService.deleteStaff(staff.id);
      loadStaff();
    } catch (err) {
      console.error('刪除美甲師失敗:', err);
      alert(`刪除失敗: ${err}`);
    }
  };

  const toggleSkill = (serviceId: number) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.includes(serviceId)
        ? prev.skills.filter(id => id !== serviceId)
        : [...prev.skills, serviceId]
    }));
  };

  const getServiceName = (serviceId: number): string => {
    const service = services.find(s => s.id === serviceId);
    return service?.name || `服務 ${serviceId}`;
  };

  return (
    <div className="p-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <UserCog className="h-6 w-6" />
            <span>美甲師管理</span>
          </CardTitle>
          <Button onClick={openCreateDialog}>
            <Plus className="h-4 w-4 mr-2" />
            新增美甲師
          </Button>
        </CardHeader>
        <CardContent>
          {loading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          )}
          
          {error && (
            <div className="text-center py-8 text-red-500">
              {error}
            </div>
          )}
          
          {!loading && !error && staffList.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              目前沒有美甲師資料
            </div>
          )}
          
          {!loading && !error && staffList.length > 0 && (
            <div className="space-y-3">
              {staffList.map((staff) => (
                <Card key={staff.id} className="overflow-hidden hover:shadow-md transition-shadow">
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-3">
                          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
                            {staff.name.charAt(0)}
                          </div>
                          <div>
                            <div className="font-bold text-lg flex items-center space-x-2">
                              <span>{staff.name}</span>
                              {staff.is_active ? (
                                <Badge variant="default" className="text-xs">
                                  <CheckCircle className="h-3 w-3 mr-1" />
                                  啟用中
                                </Badge>
                              ) : (
                                <Badge variant="secondary" className="text-xs">
                                  <XCircle className="h-3 w-3 mr-1" />
                                  已停用
                                </Badge>
                              )}
                            </div>
                            <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                              {staff.email && (
                                <div className="flex items-center space-x-1">
                                  <Mail className="h-3 w-3" />
                                  <span>{staff.email}</span>
                                </div>
                              )}
                              {staff.phone && (
                                <div className="flex items-center space-x-1">
                                  <Phone className="h-3 w-3" />
                                  <span>{staff.phone}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        {staff.skills && staff.skills.length > 0 && (
                          <div className="ml-15">
                            <div className="text-sm text-gray-500 mb-2">技能服務</div>
                            <div className="flex flex-wrap gap-2">
                              {staff.skills.map(skillId => (
                                <Badge key={skillId} variant="outline" className="text-xs">
                                  {getServiceName(skillId)}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openEditDialog(staff)}
                        >
                          <Edit className="h-4 w-4 mr-1" />
                          編輯
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDelete(staff)}
                        >
                          <Trash2 className="h-4 w-4 mr-1" />
                          刪除
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 新增/編輯對話框 */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingStaff ? '編輯美甲師' : '新增美甲師'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <Label htmlFor="name">姓名 *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="請輸入美甲師姓名"
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="example@email.com"
                />
              </div>
              
              <div>
                <Label htmlFor="phone">電話</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="0912-345-678"
                />
              </div>
            </div>
            
            <div>
              <Label className="mb-2 block">技能服務</Label>
              <div className="border rounded-lg p-4 bg-gray-50 max-h-48 overflow-y-auto">
                {services.length === 0 ? (
                  <p className="text-sm text-gray-500">載入服務中...</p>
                ) : (
                  <div className="space-y-2">
                    {services.map(service => (
                      <label
                        key={service.id}
                        className="flex items-center space-x-2 cursor-pointer hover:bg-white p-2 rounded"
                      >
                        <input
                          type="checkbox"
                          checked={formData.skills.includes(service.id)}
                          onChange={() => toggleSkill(service.id)}
                          className="rounded"
                        />
                        <span className="text-sm">{service.name}</span>
                      </label>
                    ))}
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="rounded"
              />
              <Label htmlFor="is_active" className="cursor-pointer">啟用此美甲師</Label>
            </div>
          </div>
          
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsDialogOpen(false)}
              disabled={isSaving}
            >
              取消
            </Button>
            <Button
              onClick={handleSave}
              disabled={isSaving || !formData.name}
            >
              {isSaving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  儲存中...
                </>
              ) : (
                '儲存'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}


import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { 
  Edit, 
  Settings, 
  Monitor, 
  BarChart3,
  Store,
  Calendar,
  CheckCircle,
  XCircle,
  RotateCcw
} from 'lucide-react';

interface Merchant {
  id: string;
  name: string;
  line_channel_id: string;
  liff_id?: string;
  timezone: string;
  is_active: boolean;
  created_at: string;
}

interface MerchantStats {
  total_users: number;
  total_appointments: number;
  total_revenue: number;
}

const MerchantDetail: React.FC<{ merchantId: string; onBack: () => void }> = ({ merchantId, onBack }) => {
  const [merchant, setMerchant] = useState<Merchant | null>(null);
  const [stats, setStats] = useState<MerchantStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);

  // 取得商家詳情
  const fetchMerchantDetail = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/merchants/${merchantId}`);
      if (response.ok) {
        const data = await response.json();
        setMerchant(data);
      } else {
        console.error('取得商家詳情失敗');
      }
    } catch (error) {
      console.error('網路錯誤');
    } finally {
      setLoading(false);
    }
  };

  // 取得商家統計
  const fetchMerchantStats = async () => {
    try {
      const response = await fetch(`/api/v1/merchants/${merchantId}/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data.stats);
      }
    } catch (error) {
      console.error('取得統計失敗:', error);
    }
  };

  // 更新商家資料
  const handleUpdate = async (values: any) => {
    try {
      const response = await fetch(`/api/v1/merchants/${merchantId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        console.log('商家資料更新成功');
        setEditModalVisible(false);
        fetchMerchantDetail();
      } else {
        const error = await response.json();
        console.error(error.detail || '更新失敗');
      }
    } catch (error) {
      console.error('網路錯誤');
    }
  };

  // 輪替憑證
  const handleRotateToken = async () => {
    try {
      const response = await fetch(`/api/v1/merchants/${merchantId}/rotate-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          new_token: 'new_access_token_here',
          new_secret: 'new_channel_secret_here'
        }),
      });

      if (response.ok) {
        console.log('憑證輪替成功');
      } else {
        console.error('憑證輪替失敗');
      }
    } catch (error) {
      console.error('網路錯誤');
    }
  };

  useEffect(() => {
    if (merchantId) {
      fetchMerchantDetail();
      fetchMerchantStats();
    }
  }, [merchantId]);

  if (!merchant) {
    return <div>載入中...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">商家詳情 - {merchant.name}</h2>
        <div className="flex items-center space-x-2">
          <Button onClick={() => setEditModalVisible(true)}>
            <Edit className="h-4 w-4 mr-2" />
            編輯
          </Button>
        </div>
      </div>

      <Tabs defaultValue="basic" className="space-y-4">
        <TabsList>
          <TabsTrigger value="basic">基本資料</TabsTrigger>
          <TabsTrigger value="settings">設定管理</TabsTrigger>
          <TabsTrigger value="monitoring">監控與健診</TabsTrigger>
          <TabsTrigger value="reports">報表統計</TabsTrigger>
        </TabsList>

        <TabsContent value="basic" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>基本資訊</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label className="text-sm font-medium">商家名稱</Label>
                  <p className="text-sm">{merchant.name}</p>
                </div>
                <div className="space-y-2">
                  <Label className="text-sm font-medium">LINE Channel ID</Label>
                  <p className="text-sm font-mono">{merchant.line_channel_id}</p>
                </div>
                <div className="space-y-2">
                  <Label className="text-sm font-medium">LIFF ID</Label>
                  <p className="text-sm">{merchant.liff_id || '未設定'}</p>
                </div>
                <div className="space-y-2">
                  <Label className="text-sm font-medium">時區</Label>
                  <p className="text-sm">{merchant.timezone}</p>
                </div>
                <div className="space-y-2">
                  <Label className="text-sm font-medium">狀態</Label>
                  <div className="flex items-center space-x-2">
                    {merchant.is_active ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-600" />
                    )}
                    <span className="text-sm">{merchant.is_active ? '活躍' : '停用'}</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label className="text-sm font-medium">創建時間</Label>
                  <p className="text-sm">{new Date(merchant.created_at).toLocaleString('zh-TW')}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>基本設定</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex space-x-2">
                <Button variant="outline" onClick={() => setEditModalVisible(true)}>
                  <Edit className="h-4 w-4 mr-2" />
                  編輯基本資料
                </Button>
                <Button variant="outline">
                  <Settings className="h-4 w-4 mr-2" />
                  營業規則
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>LINE 設定</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex space-x-2">
                <Button variant="outline">更新 LIFF 設定</Button>
                <Button variant="outline">管理 Rich Menu</Button>
                <Button variant="outline" onClick={handleRotateToken}>
                  <RotateCcw className="h-4 w-4 mr-2" />
                  輪替憑證
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>範本管理</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex space-x-2">
                <Button variant="outline">服務項目範本</Button>
                <Button variant="outline">Flex Message 範本</Button>
                <Button variant="outline">FAQ 範本</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="monitoring" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>健康狀態</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">正常</div>
                  <div className="text-sm text-muted-foreground">Webhook 健康</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">45%</div>
                  <div className="text-sm text-muted-foreground">推播配額</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">正常</div>
                  <div className="text-sm text-muted-foreground">任務佇列</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">99.9%</div>
                  <div className="text-sm text-muted-foreground">可用性</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>監控詳情</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex space-x-2">
                <Button variant="outline">
                  <Monitor className="h-4 w-4 mr-2" />
                  Webhook 健康檢查
                </Button>
                <Button variant="outline">推播配額狀態</Button>
                <Button variant="outline">任務排程監控</Button>
                <Button variant="outline">可用性監控</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>業務指標</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="text-center">
                  <div className="text-2xl font-bold">{stats?.total_users || 0}</div>
                  <div className="text-sm text-muted-foreground">總用戶數</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{stats?.total_appointments || 0}</div>
                  <div className="text-sm text-muted-foreground">總預約數</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">NT$ {stats?.total_revenue || 0}</div>
                  <div className="text-sm text-muted-foreground">總營收</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>報表功能</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex space-x-2">
                <Button variant="outline">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  業務指標
                </Button>
                <Button variant="outline">顧客規模分析</Button>
                <Button variant="outline">趨勢分析</Button>
                <Button variant="outline">匯出報表</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 編輯商家資料對話框 */}
      <Dialog open={editModalVisible} onOpenChange={setEditModalVisible}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>編輯商家資料</DialogTitle>
          </DialogHeader>
          <EditMerchantForm 
            merchant={merchant} 
            onSubmit={handleUpdate} 
            onCancel={() => setEditModalVisible(false)}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
};

// 編輯商家表單組件
const EditMerchantForm: React.FC<{ 
  merchant: Merchant; 
  onSubmit: (values: any) => void;
  onCancel: () => void;
}> = ({ merchant, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: merchant.name,
    liff_id: merchant.liff_id || '',
    timezone: merchant.timezone
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="name">商家名稱</Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="請輸入商家名稱"
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="liff_id">LIFF ID</Label>
        <Input
          id="liff_id"
          value={formData.liff_id}
          onChange={(e) => setFormData({ ...formData, liff_id: e.target.value })}
          placeholder="請輸入 LIFF ID"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="timezone">時區</Label>
        <Input
          id="timezone"
          value={formData.timezone}
          onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
          placeholder="請輸入時區"
          required
        />
      </div>

      <div className="flex justify-end space-x-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          取消
        </Button>
        <Button type="submit">更新</Button>
      </div>
    </form>
  );
};

export default MerchantDetail;
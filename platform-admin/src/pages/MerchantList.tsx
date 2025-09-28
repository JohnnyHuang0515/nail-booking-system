import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { 
  Plus, 
  Search, 
  Eye, 
  Edit, 
  Trash2,
  Store,
  Calendar,
  CheckCircle,
  XCircle
} from 'lucide-react';
// import { useMerchants } from '../hooks/useApi';

interface Merchant {
  id: string;
  name: string;
  line_channel_id: string;
  liff_id?: string;
  timezone: string;
  is_active: boolean;
  created_at: string;
}

interface MerchantListProps {
  onMerchantSelect: (merchantId: string) => void;
}

const MerchantList: React.FC<MerchantListProps> = ({ onMerchantSelect }) => {
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [loading, setLoading] = useState(false);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Use API hook for real data
  // const { data: apiMerchants, loading: apiLoading, refetch } = useMerchants();

  // 取得商家列表
  const fetchMerchants = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/merchants');
      if (response.ok) {
        const data = await response.json();
        setMerchants(data);
      } else {
        console.error('取得商家列表失敗');
      }
    } catch (error) {
      console.error('網路錯誤');
    } finally {
      setLoading(false);
    }
  };

  // 創建商家
  const handleCreate = async (values: any) => {
    try {
      const response = await fetch('/api/v1/merchants', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        console.log('商家創建成功');
        setCreateModalVisible(false);
        fetchMerchants();
      } else {
        const error = await response.json();
        console.error(error.detail || '創建商家失敗');
      }
    } catch (error) {
      console.error('網路錯誤');
    }
  };

  // 切換商家狀態
  const handleToggleStatus = async (merchantId: string, isActive: boolean) => {
    try {
      const response = await fetch(`/api/v1/merchants/${merchantId}/toggle-status`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_active: isActive }),
      });

      if (response.ok) {
        console.log(`商家已${isActive ? '啟用' : '停用'}`);
        fetchMerchants();
      } else {
        console.error('切換狀態失敗');
      }
    } catch (error) {
      console.error('網路錯誤');
    }
  };

  // 刪除商家
  const handleDelete = async (merchantId: string) => {
    try {
      const response = await fetch(`/api/v1/merchants/${merchantId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        console.log('商家已停用');
        fetchMerchants();
      } else {
        console.error('停用商家失敗');
      }
    } catch (error) {
      console.error('網路錯誤');
    }
  };

  useEffect(() => {
    fetchMerchants();
  }, []);

  const filteredMerchants = merchants.filter(merchant =>
    merchant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    merchant.line_channel_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">商家管理</h2>
        <Dialog open={createModalVisible} onOpenChange={setCreateModalVisible}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              新增商家
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>新增商家</DialogTitle>
            </DialogHeader>
            <CreateMerchantForm onSubmit={handleCreate} />
          </DialogContent>
        </Dialog>
      </div>

      {/* 搜尋 */}
      <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="搜尋商家名稱或 LINE Channel ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* 商家列表 */}
      <div className="grid gap-4">
        {filteredMerchants.map((merchant) => (
          <Card key={merchant.id}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <Store className="h-4 w-4 text-muted-foreground" />
                    <h3 className="text-lg font-semibold">{merchant.name}</h3>
                    {merchant.is_active ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-600" />
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">LINE Channel ID: {merchant.line_channel_id}</p>
                  {merchant.liff_id && (
                    <p className="text-sm text-muted-foreground">LIFF ID: {merchant.liff_id}</p>
                  )}
                  <p className="text-sm text-muted-foreground">時區: {merchant.timezone}</p>
                  <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                    <Calendar className="h-3 w-3" />
                    <span>創建時間: {new Date(merchant.created_at).toLocaleString('zh-TW')}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => onMerchantSelect(merchant.id)}
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    查看
                  </Button>
                  <Button variant="outline" size="sm">
                    <Edit className="h-4 w-4 mr-2" />
            編輯
          </Button>
          <Button
                    variant="outline" 
                    size="sm"
                    onClick={() => handleToggleStatus(merchant.id, !merchant.is_active)}
          >
                    {merchant.is_active ? '停用' : '啟用'}
          </Button>
                  <Button 
                    variant="destructive" 
                    size="sm"
                    onClick={() => handleDelete(merchant.id)}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
              停用
            </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredMerchants.length === 0 && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center text-muted-foreground">
              沒有找到符合條件的商家
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// 創建商家表單組件
const CreateMerchantForm: React.FC<{ onSubmit: (values: any) => void }> = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    line_channel_id: '',
    line_channel_secret: '',
    line_channel_access_token: '',
    liff_id: '',
    timezone: 'Asia/Taipei'
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
        <Label htmlFor="line_channel_id">LINE Channel ID</Label>
        <Input
          id="line_channel_id"
          value={formData.line_channel_id}
          onChange={(e) => setFormData({ ...formData, line_channel_id: e.target.value })}
          placeholder="請輸入 LINE Channel ID"
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="line_channel_secret">LINE Channel Secret</Label>
        <Input
          id="line_channel_secret"
          type="password"
          value={formData.line_channel_secret}
          onChange={(e) => setFormData({ ...formData, line_channel_secret: e.target.value })}
          placeholder="請輸入 LINE Channel Secret"
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="line_channel_access_token">LINE Access Token</Label>
        <textarea
          id="line_channel_access_token"
          className="w-full min-h-[80px] px-3 py-2 border border-input bg-background rounded-md text-sm"
          value={formData.line_channel_access_token}
          onChange={(e) => setFormData({ ...formData, line_channel_access_token: e.target.value })}
              placeholder="請輸入 LINE Access Token" 
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="liff_id">LIFF ID</Label>
        <Input
          id="liff_id"
          value={formData.liff_id}
          onChange={(e) => setFormData({ ...formData, liff_id: e.target.value })}
          placeholder="請輸入 LIFF ID（可選）"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="timezone">時區</Label>
        <Input
          id="timezone"
          value={formData.timezone}
          onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
          placeholder="請輸入時區"
        />
      </div>

      <div className="flex justify-end space-x-2">
        <Button type="submit">創建</Button>
    </div>
    </form>
  );
};

export default MerchantList;
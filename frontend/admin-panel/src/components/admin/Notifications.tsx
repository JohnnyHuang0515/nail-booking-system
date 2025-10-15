import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { Bell, Send, TestTube, AlertTriangle, CheckCircle } from 'lucide-react';
import adminApiService from '../../services/api';

interface NotificationTemplate {
  type: string;
  name: string;
  description: string;
}

export default function Notifications() {
  const [templates, setTemplates] = useState<NotificationTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // 發送通知表單
  const [sendForm, setSendForm] = useState({
    recipient: '',
    notification_type: '',
    variables: {
      customer_name: '',
      booking_id: '',
      start_at: '',
      service_name: ''
    }
  });

  // 測試通知表單
  const [testForm, setTestForm] = useState({
    recipient: '',
    message: ''
  });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      setError('');
      const templatesData = await adminApiService.getNotificationTemplates();
      setTemplates(templatesData.templates || templatesData);
    } catch (err: any) {
      console.error('載入通知模板失敗:', err);
      setError('載入通知模板失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  const handleSendNotification = async () => {
    try {
      setError('');
      setSuccess('');

      if (!sendForm.recipient || !sendForm.notification_type) {
        setError('請填寫所有必填欄位');
        return;
      }

      await adminApiService.sendNotification({
        recipient: sendForm.recipient,
        notification_type: sendForm.notification_type,
        variables: sendForm.variables
      });

      setSuccess('通知發送成功！');
      setSendForm({
        recipient: '',
        notification_type: '',
        variables: {
          customer_name: '',
          booking_id: '',
          start_at: '',
          service_name: ''
        }
      });
    } catch (err: any) {
      console.error('發送通知失敗:', err);
      setError(`發送通知失敗: ${err.message || '請稍後再試'}`);
    }
  };

  const handleTestNotification = async () => {
    try {
      setError('');
      setSuccess('');

      if (!testForm.recipient || !testForm.message) {
        setError('請填寫所有必填欄位');
        return;
      }

      await adminApiService.testNotification(testForm.recipient, testForm.message);

      setSuccess('測試通知發送成功！');
      setTestForm({ recipient: '', message: '' });
    } catch (err: any) {
      console.error('測試通知失敗:', err);
      setError(`測試通知失敗: ${err.message || '請稍後再試'}`);
    }
  };

  const getTemplateTypeName = (type: string) => {
    const template = templates.find(t => t.type === type);
    return template ? template.name : type;
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">通知管理</h1>
        <Bell className="h-8 w-8 text-gray-600" />
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* 通知模板列表 */}
      <Card>
        <CardHeader>
          <CardTitle>可用通知模板</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {templates.map((template) => (
              <Card key={template.type} className="p-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold">{template.name}</h3>
                    <Badge variant="outline">{template.type}</Badge>
                  </div>
                  <p className="text-sm text-gray-600">{template.description}</p>
                </div>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 發送通知 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Send className="h-5 w-5" />
            發送通知
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="recipient">收件人 LINE User ID</Label>
              <Input
                id="recipient"
                placeholder="U1234567890abcdef"
                value={sendForm.recipient}
                onChange={(e) => setSendForm(prev => ({ ...prev, recipient: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="notification_type">通知類型</Label>
              <Select
                value={sendForm.notification_type}
                onValueChange={(value) => setSendForm(prev => ({ ...prev, notification_type: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="選擇通知類型" />
                </SelectTrigger>
                <SelectContent>
                  {templates.map((template) => (
                    <SelectItem key={template.type} value={template.type}>
                      {template.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="customer_name">客戶姓名</Label>
              <Input
                id="customer_name"
                placeholder="張三"
                value={sendForm.variables.customer_name}
                onChange={(e) => setSendForm(prev => ({ 
                  ...prev, 
                  variables: { ...prev.variables, customer_name: e.target.value }
                }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="booking_id">預約編號</Label>
              <Input
                id="booking_id"
                placeholder="BK123456"
                value={sendForm.variables.booking_id}
                onChange={(e) => setSendForm(prev => ({ 
                  ...prev, 
                  variables: { ...prev.variables, booking_id: e.target.value }
                }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="start_at">預約時間</Label>
              <Input
                id="start_at"
                placeholder="2025-10-16 14:00"
                value={sendForm.variables.start_at}
                onChange={(e) => setSendForm(prev => ({ 
                  ...prev, 
                  variables: { ...prev.variables, start_at: e.target.value }
                }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="service_name">服務名稱</Label>
              <Input
                id="service_name"
                placeholder="基礎美甲"
                value={sendForm.variables.service_name}
                onChange={(e) => setSendForm(prev => ({ 
                  ...prev, 
                  variables: { ...prev.variables, service_name: e.target.value }
                }))}
              />
            </div>
          </div>

          <Button onClick={handleSendNotification} className="w-full">
            <Send className="h-4 w-4 mr-2" />
            發送通知
          </Button>
        </CardContent>
      </Card>

      {/* 測試通知 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TestTube className="h-5 w-5" />
            測試通知
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="test_recipient">收件人 LINE User ID</Label>
            <Input
              id="test_recipient"
              placeholder="U1234567890abcdef"
              value={testForm.recipient}
              onChange={(e) => setTestForm(prev => ({ ...prev, recipient: e.target.value }))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="test_message">測試訊息</Label>
            <Textarea
              id="test_message"
              placeholder="這是一條測試訊息..."
              value={testForm.message}
              onChange={(e) => setTestForm(prev => ({ ...prev, message: e.target.value }))}
              rows={3}
            />
          </div>
          <Button onClick={handleTestNotification} className="w-full">
            <TestTube className="h-4 w-4 mr-2" />
            發送測試通知
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

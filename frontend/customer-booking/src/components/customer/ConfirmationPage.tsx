import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Badge } from '../ui/badge';
import { Calendar, Clock, Sparkles, User, Phone, Mail, ChevronLeft, CheckCircle, History } from 'lucide-react';
import storageService from '../../services/storage';

interface ConfirmationPageProps {
  selectedDate: string;
  selectedTime: string;
  selectedService: any;
  lineUser?: any;
  onNext: (customerInfo: any) => void;
  onBack: () => void;
}

export default function ConfirmationPage({ 
  selectedDate, 
  selectedTime, 
  selectedService, 
  lineUser,
  onNext, 
  onBack 
}: ConfirmationPageProps) {
  const [customerInfo, setCustomerInfo] = useState({
    name: '',
    phone: '',
    email: '',
    notes: ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [dataSource, setDataSource] = useState<'line' | 'stored' | 'manual'>('manual');

  // 初始化用戶資料
  useEffect(() => {
    const initializeUserData = () => {
      // 優先順序：LINE 資料 > 儲存的資料 > 空白
      if (lineUser?.displayName) {
        setCustomerInfo(prev => ({
          ...prev,
          name: lineUser.displayName
        }));
        setDataSource('line');
      }

      // 檢查是否有儲存的資料
      const storedProfile = storageService.getUserProfile();
      if (storedProfile && !storageService.isProfileExpired()) {
        setCustomerInfo(prev => ({
          name: lineUser?.displayName || storedProfile.name,
          phone: storedProfile.phone,
          email: storedProfile.email,
          notes: prev.notes // 保留當前的備註
        }));
        
        if (!lineUser?.displayName) {
          setDataSource('stored');
        }
      }
    };

    initializeUserData();
  }, [lineUser]);

  const handleInputChange = (field: string, value: string) => {
    setCustomerInfo(prev => ({
      ...prev,
      [field]: value
    }));
    
    // 如果用戶手動修改資料，標記為手動輸入
    if (field !== 'notes') {
      setDataSource('manual');
    }
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!customerInfo.name.trim()) {
      newErrors.name = '請輸入姓名';
    }
    
    if (!customerInfo.phone.trim()) {
      newErrors.phone = '請輸入聯絡電話';
    } else if (!/^09\d{8}$/.test(customerInfo.phone.replace(/[-\s]/g, ''))) {
      newErrors.phone = '請輸入有效的手機號碼';
    }
    
    if (customerInfo.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(customerInfo.email)) {
      newErrors.email = '請輸入有效的電子郵件';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validateForm()) {
      // 儲存用戶資料供下次使用
      storageService.saveUserProfile({
        name: customerInfo.name,
        phone: customerInfo.phone,
        email: customerInfo.email
      });
      
      onNext(customerInfo);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    });
  };

  const calculateEndTime = (startTime: string, duration: number) => {
    const [hours, minutes] = startTime.split(':').map(Number);
    const totalMinutes = hours * 60 + minutes + duration;
    const endHours = Math.floor(totalMinutes / 60);
    const endMinutes = totalMinutes % 60;
    return `${String(endHours).padStart(2, '0')}:${String(endMinutes).padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-md mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-foreground mb-2">確認預約資訊</h1>
          <p className="text-muted-foreground">請確認您的預約詳情並填寫聯絡資訊</p>
        </div>

        {/* Booking Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              <CheckCircle className="h-5 w-5 mr-2 text-primary" />
              預約摘要
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Date & Time */}
            <div className="flex items-center space-x-3 p-3 bg-muted rounded-lg">
              <Calendar className="h-5 w-5 text-primary" />
              <div>
                <div className="font-medium">{formatDate(selectedDate)}</div>
                <div className="text-sm text-muted-foreground">
                  {selectedTime} - {calculateEndTime(selectedTime, selectedService.duration_minutes)}
                </div>
              </div>
            </div>

            {/* Service */}
            <div className="flex items-start space-x-3 p-3 bg-muted rounded-lg">
              <Sparkles className="h-5 w-5 text-primary mt-0.5" />
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="font-medium">{selectedService.name}</span>
                  {selectedService.category && (
                    <Badge className="bg-secondary text-secondary-foreground">
                      {selectedService.category}
                    </Badge>
                  )}
                </div>
                {selectedService.description && (
                  <div className="text-sm text-muted-foreground mb-2">
                    {selectedService.description}
                  </div>
                )}
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center text-muted-foreground">
                    <Clock className="h-3 w-3 mr-1" />
                    {selectedService.duration_minutes} 分鐘
                  </div>
                  <div className="font-medium text-primary">
                    NT${selectedService.price}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Customer Information */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              <User className="h-5 w-5 mr-2 text-primary" />
              聯絡資訊
              {dataSource === 'line' && (
                <Badge variant="secondary" className="ml-2 text-xs">
                  已從 LINE 自動填入
                </Badge>
              )}
              {dataSource === 'stored' && (
                <Badge variant="outline" className="ml-2 text-xs">
                  已載入上次資料
                </Badge>
              )}
            </CardTitle>
            {dataSource === 'line' && lineUser && (
              <div className="flex items-center space-x-3 mt-2">
                {lineUser.pictureUrl && (
                  <img 
                    src={lineUser.pictureUrl} 
                    alt="用戶頭像" 
                    className="w-8 h-8 rounded-full"
                  />
                )}
                <div className="text-sm text-muted-foreground">
                  <span className="font-medium">{lineUser.displayName}</span>
                  {lineUser.statusMessage && (
                    <span className="ml-2">• {lineUser.statusMessage}</span>
                  )}
                </div>
              </div>
            )}
            {dataSource === 'stored' && (
              <div className="flex items-center space-x-2 mt-2">
                <History className="h-4 w-4 text-muted-foreground" />
                <div className="text-sm text-muted-foreground">
                  載入了 {storageService.getProfileAge()} 天前的資料
                </div>
              </div>
            )}
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="name" className="flex items-center">
                姓名 *
                {dataSource === 'line' && customerInfo.name === lineUser?.displayName && (
                  <Badge variant="outline" className="ml-2 text-xs">
                    LINE 自動填入
                  </Badge>
                )}
                {dataSource === 'stored' && (
                  <Badge variant="outline" className="ml-2 text-xs">
                    上次資料
                  </Badge>
                )}
              </Label>
              <Input
                id="name"
                placeholder="請輸入您的姓名"
                value={customerInfo.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                className={errors.name ? 'border-red-500' : ''}
              />
              {errors.name && (
                <p className="text-red-500 text-sm mt-1">{errors.name}</p>
              )}
            </div>

            <div>
              <Label htmlFor="phone">聯絡電話 *</Label>
              <Input
                id="phone"
                placeholder="例：0912-345-678"
                value={customerInfo.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                className={errors.phone ? 'border-red-500' : ''}
              />
              {errors.phone && (
                <p className="text-red-500 text-sm mt-1">{errors.phone}</p>
              )}
            </div>

            <div>
              <Label htmlFor="email">電子郵件（選填）</Label>
              <Input
                id="email"
                type="email"
                placeholder="example@email.com"
                value={customerInfo.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                className={errors.email ? 'border-red-500' : ''}
              />
              {errors.email && (
                <p className="text-red-500 text-sm mt-1">{errors.email}</p>
              )}
            </div>

            <div>
              <Label htmlFor="notes">備註（選填）</Label>
              <Textarea
                id="notes"
                placeholder="有任何特殊需求或備註可以在此填寫"
                value={customerInfo.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                rows={3}
              />
            </div>
          </CardContent>
        </Card>

        {/* Terms */}
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-muted-foreground space-y-2">
              <div className="font-medium text-foreground">預約條款：</div>
              <ul className="space-y-1 list-disc list-inside">
                <li>請準時到達，建議提前10分鐘</li>
                <li>如需取消或更改，請提前24小時聯繫</li>
                <li>遲到超過15分鐘可能需要重新安排</li>
                <li>首次預約建議預留額外15分鐘諮詢時間</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Navigation buttons */}
        <div className="flex space-x-3">
          <Button variant="outline" onClick={onBack} className="flex-1">
            <ChevronLeft className="h-4 w-4 mr-2" />
            返回服務
          </Button>
          <Button 
            onClick={handleSubmit}
            className="flex-1"
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            確認預約
          </Button>
        </div>
      </div>
    </div>
  );
}
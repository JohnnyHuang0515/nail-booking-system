import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Sparkles, ChevronLeft, Clock, CheckCircle, Loader2 } from 'lucide-react';
import customerApiService from '../../services/api';

interface Service {
  id: number;
  merchant_id: string;
  name: string;
  description: string;
  base_price: number;
  duration_minutes: number;
  is_active: boolean;
  category?: string;
}

interface ServiceSelectionPageProps {
  selectedDate: string;
  selectedTime: string;
  onNext: (services: Service[], date: string, time: string) => void;
  onBack: () => void;
}

export default function ServiceSelectionPage({ 
  selectedDate, 
  selectedTime, 
  onNext, 
  onBack 
}: ServiceSelectionPageProps) {
  const [selectedServices, setSelectedServices] = useState<Service[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  // 載入服務列表
  useEffect(() => {
    const loadServices = async () => {
      try {
        setLoading(true);
        setError('');
        
        // 從 API 獲取服務列表
        const fetchedServices = await customerApiService.getServices();
        setServices(fetchedServices.filter(s => s.is_active));
        console.log('✅ 載入服務:', fetchedServices.length, '項');
      } catch (err) {
        console.error('❌ 載入服務失敗:', err);
        setError('無法載入服務列表，請稍後再試');
      } finally {
        setLoading(false);
      }
    };

    loadServices();
  }, []);

  const handleServiceToggle = (service: Service) => {
    setSelectedServices(prev => {
      const exists = prev.find(s => s.id === service.id);
      if (exists) {
        // 取消選擇
        setError('');  // 清除錯誤
        return prev.filter(s => s.id !== service.id);
      } else {
        // 檢查新增後是否超過3小時
        const newTotal = prev.reduce((sum, s) => sum + s.duration_minutes, 0) + service.duration_minutes;
        if (newTotal > 180) {
          setError('服務總時長不能超過3小時（180分鐘）');
          return prev;
        }
        setError('');  // 清除錯誤
        return [...prev, service];
      }
    });
  };

  const handleNext = () => {
    if (selectedServices.length > 0) {
      // 檢查總時長是否超過3小時（180分鐘）
      if (totalDuration > 180) {
        setError('服務總時長不能超過3小時');
        return;
      }
      onNext(selectedServices, selectedDate, selectedTime);
    }
  };
  
  // 計算總時長和總金額
  const totalDuration = selectedServices.reduce((sum, s) => sum + s.duration_minutes, 0);
  const totalPrice = selectedServices.reduce((sum, s) => sum + s.base_price, 0);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-TW', {
      month: 'long',
      day: 'numeric',
      weekday: 'short'
    });
  };

  // 按類別分組服務
  const groupServicesByCategory = () => {
    const groups: { [key: string]: Service[] } = {};
    
    services.forEach(service => {
      const category = service.category || '其他';
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(service);
    });
    
    return groups;
  };

  const serviceGroups = groupServicesByCategory();

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-md mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-foreground mb-2">選擇服務項目</h1>
          <p className="text-muted-foreground">
            {formatDate(selectedDate)} • {selectedTime}
          </p>
        </div>

        {/* Loading State */}
        {loading && (
          <Card>
            <CardContent className="pt-12 pb-12">
              <div className="flex flex-col items-center space-y-4">
                <Loader2 className="h-8 w-8 text-primary animate-spin" />
                <p className="text-muted-foreground">載入服務列表中...</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error State - 顯示在頂部但不遮擋服務列表 */}
        {error && (
          <Card className="border-red-300 bg-red-50">
            <CardContent className="pt-4 pb-4">
              <div className="flex items-center space-x-3 text-red-600">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="font-medium">{error}</p>
                  <p className="text-sm mt-1">請取消部分服務以降低總時長</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Services by Category */}
        {!loading && (
          <>
            {Object.entries(serviceGroups).map(([category, categoryServices]) => (
              <Card key={category}>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center">
                    <Sparkles className="h-5 w-5 mr-2 text-primary" />
                    {category}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {categoryServices.map((service) => {
                    const isSelected = selectedServices.some(s => s.id === service.id);
                    
                    return (
                      <button
                        key={service.id}
                        onClick={() => handleServiceToggle(service)}
                        className={`
                          w-full p-4 rounded-lg border-2 text-left transition-all
                          ${isSelected 
                            ? 'border-primary bg-primary/10 ring-2 ring-primary/20' 
                            : 'border-border bg-card hover:border-primary/50 hover:bg-muted'
                          }
                        `}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2">
                              <span className="font-medium text-foreground">
                                {service.name}
                              </span>
                              {isSelected && (
                                <CheckCircle className="h-4 w-4 text-primary" />
                              )}
                            </div>
                            <p className="text-sm text-muted-foreground mt-1">
                              {service.description}
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between text-sm">
                          <div className="flex items-center text-muted-foreground">
                            <Clock className="h-3 w-3 mr-1" />
                            {service.duration_minutes} 分鐘
                          </div>
                          <div className="font-medium text-primary text-lg">
                            NT${service.base_price}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </CardContent>
              </Card>
            ))}

            {services.length === 0 && (
              <Card>
                <CardContent className="pt-12 pb-12 text-center">
                  <div className="text-muted-foreground">
                    <Sparkles className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>目前沒有可用服務</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {/* Selected services summary */}
        {selectedServices.length > 0 && (
          <Card className="bg-secondary">
            <CardContent className="pt-6">
              <div className="space-y-3">
                <div className="text-sm text-secondary-foreground font-medium">
                  已選擇 {selectedServices.length} 項服務
                </div>
                {selectedServices.map((service, index) => (
                  <div key={service.id} className="flex items-center justify-between text-sm">
                    <span className="text-secondary-foreground">
                      {index + 1}. {service.name}
                    </span>
                    <span className="text-secondary-foreground">
                      NT${service.base_price}
                    </span>
                  </div>
                ))}
                <div className="border-t border-secondary-foreground/20 pt-2 space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-secondary-foreground">總時長</span>
                    <span className={`font-medium ${totalDuration > 180 ? 'text-red-600' : 'text-secondary-foreground'}`}>
                      {totalDuration} 分鐘
                      {totalDuration > 180 && ` (超過 ${totalDuration - 180} 分鐘)`}
                    </span>
                  </div>
                  {totalDuration > 180 && (
                    <div className="text-xs text-red-600 bg-red-50 p-2 rounded border border-red-200">
                      ⚠️ 服務總時長超過限制（最多180分鐘），請取消部分服務
                    </div>
                  )}
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-secondary-foreground">總金額</span>
                    <span className="font-medium text-primary text-xl">
                      NT${totalPrice}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Navigation buttons */}
        <div className="flex space-x-3">
          <Button variant="outline" onClick={onBack} className="flex-1">
            <ChevronLeft className="h-4 w-4 mr-2" />
            返回時段
          </Button>
          <Button 
            onClick={handleNext}
            disabled={selectedServices.length === 0 || totalDuration > 180}
            className="flex-1"
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            {totalDuration > 180 ? '超過時間限制' : '下一步'}
          </Button>
        </div>
      </div>
    </div>
  );
}


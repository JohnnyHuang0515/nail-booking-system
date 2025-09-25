import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Clock, ChevronLeft, CheckCircle, DollarSign } from 'lucide-react';

interface ServiceSelectionPageProps {
  selectedDate: string;
  selectedTime: string;
  onNext: (selectedService: any, selectedDate: string, selectedTime: string) => void;
  onBack: () => void;
}

export default function ServiceSelectionPage({ 
  selectedDate, 
  selectedTime, 
  onNext, 
  onBack 
}: ServiceSelectionPageProps) {
  const [selectedService, setSelectedService] = useState<any>(null);

  const services = [
    {
      id: 1,
      name: '基礎保養',
      description: '基礎指甲修剪、去角質、保濕護理',
      duration: 60,
      price: 800,
      category: '基礎護理',
      popular: false
    },
    {
      id: 2,
      name: '法式指甲',
      description: '經典法式風格，優雅簡約',
      duration: 90,
      price: 1200,
      category: '彩繪指甲',
      popular: true
    },
    {
      id: 3,
      name: '光療指甲',
      description: '持久光療，多種顏色選擇',
      duration: 120,
      price: 1500,
      category: '光療系列',
      popular: true
    },
    {
      id: 4,
      name: '手部護理',
      description: '深層手部護理，包含按摩和保濕',
      duration: 75,
      price: 1000,
      category: '護理療程',
      popular: false
    },
    {
      id: 5,
      name: '指甲彩繪',
      description: '個性化指甲彩繪設計',
      duration: 150,
      price: 2000,
      category: '彩繪指甲',
      popular: false
    },
  ];

  const handleServiceSelect = (service: any) => {
    setSelectedService(service);
  };

  const handleNext = () => {
    if (selectedService) {
      onNext(selectedService, selectedDate, selectedTime);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-TW', {
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    });
  };

  const categories = Array.from(new Set(services.map(s => s.category)));

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-md mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-foreground mb-2">選擇服務項目</h1>
          <p className="text-muted-foreground">請選擇您想要的美甲服務</p>
        </div>

        {/* Selected date and time */}
        <Card className="bg-secondary">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-sm text-secondary-foreground mb-1">預約資訊</div>
              <div className="font-medium text-secondary-foreground">
                {formatDate(selectedDate)} • {selectedTime}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Services by category */}
        {categories.map(category => {
          const categoryServices = services.filter(s => s.category === category);
          
          return (
            <Card key={category}>
              <CardHeader>
                <CardTitle className="text-lg">{category}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {categoryServices.map((service) => {
                    const isSelected = selectedService?.id === service.id;
                    
                    return (
                      <button
                        key={service.id}
                        onClick={() => handleServiceSelect(service)}
                        className={`
                          w-full p-4 rounded-lg border text-left transition-colors
                          ${isSelected 
                            ? 'border-primary bg-primary/5' 
                            : 'border-border hover:bg-muted'
                          }
                        `}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex items-center space-x-2">
                            <h3 className="font-medium">{service.name}</h3>
                            {service.popular && (
                              <Badge className="bg-orange-100 text-orange-700 text-xs">
                                熱門
                              </Badge>
                            )}
                            {isSelected && (
                              <CheckCircle className="h-4 w-4 text-primary" />
                            )}
                          </div>
                          <div className="text-right">
                            <div className="font-medium text-primary">NT${service.price}</div>
                          </div>
                        </div>
                        
                        <p className="text-sm text-muted-foreground mb-2">
                          {service.description}
                        </p>
                        
                        <div className="flex items-center text-xs text-muted-foreground">
                          <Clock className="h-3 w-3 mr-1" />
                          約 {service.duration} 分鐘
                        </div>
                      </button>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          );
        })}

        {/* Selected service summary */}
        {selectedService && (
          <Card className="bg-primary/10 border-primary/20">
            <CardContent className="pt-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-primary">已選擇服務</span>
                  <CheckCircle className="h-5 w-5 text-primary" />
                </div>
                <div className="text-sm">
                  <div className="font-medium">{selectedService.name}</div>
                  <div className="text-muted-foreground flex items-center justify-between mt-1">
                    <span>服務時間：{selectedService.duration} 分鐘</span>
                    <span className="font-medium text-primary">NT${selectedService.price}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Service info */}
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm space-y-2 text-muted-foreground">
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 rounded bg-orange-100"></div>
                <span>熱門服務項目</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-primary" />
                <span>已選擇的服務</span>
              </div>
              <div className="text-xs mt-3 p-3 bg-muted rounded">
                <strong>注意事項：</strong>
                所有服務均使用高品質材料，建議提前10分鐘到達。如需取消或更改預約，請提前24小時聯繫我們。
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Navigation buttons */}
        <div className="flex space-x-3">
          <Button variant="outline" onClick={onBack} className="flex-1">
            <ChevronLeft className="h-4 w-4 mr-2" />
            返回時段
          </Button>
          <Button 
            onClick={handleNext}
            disabled={!selectedService}
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
import React from 'react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { CheckCircle, Calendar, Clock, Sparkles, User, Phone, MapPin, Star } from 'lucide-react';

interface SuccessPageProps {
  selectedDate: string;
  selectedTime: string;
  selectedService: any;
  customerInfo: any;
  onNewBooking: () => void;
}

export default function SuccessPage({ 
  selectedDate, 
  selectedTime, 
  selectedService, 
  customerInfo,
  onNewBooking 
}: SuccessPageProps) {
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

  // Generate a mock booking reference
  const bookingRef = `NB${Date.now().toString().slice(-6)}`;

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-md mx-auto space-y-6">
        {/* Success Header */}
        <div className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-foreground mb-2">預約成功！</h1>
            <p className="text-muted-foreground">您的預約已成功建立，我們期待為您服務</p>
          </div>
        </div>

        {/* Booking Details */}
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="text-center mb-4">
              <div className="text-sm text-muted-foreground">預約編號</div>
              <div className="text-lg font-mono font-medium text-primary">{bookingRef}</div>
            </div>

            {/* Date & Time */}
            <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg border border-green-200">
              <Calendar className="h-5 w-5 text-green-600" />
              <div>
                <div className="font-medium text-green-800">{formatDate(selectedDate)}</div>
                <div className="text-sm text-green-600">
                  {selectedTime} - {calculateEndTime(selectedTime, selectedService.duration)}
                </div>
              </div>
            </div>

            {/* Service */}
            <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <Sparkles className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="font-medium text-blue-800">{selectedService.name}</span>
                  <Badge className="bg-blue-100 text-blue-700">
                    {selectedService.category}
                  </Badge>
                </div>
                <div className="text-sm text-blue-600 mb-2">
                  {selectedService.description}
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center text-blue-600">
                    <Clock className="h-3 w-3 mr-1" />
                    {selectedService.duration} 分鐘
                  </div>
                  <div className="font-medium text-blue-800">
                    NT${selectedService.price}
                  </div>
                </div>
              </div>
            </div>

            {/* Customer Info */}
            <div className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg border border-purple-200">
              <User className="h-5 w-5 text-purple-600" />
              <div>
                <div className="font-medium text-purple-800">{customerInfo.name}</div>
                <div className="text-sm text-purple-600">{customerInfo.phone}</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Store Information */}
        <Card>
          <CardContent className="pt-6 space-y-3">
            <h3 className="font-medium mb-3">店家資訊</h3>
            
            <div className="flex items-start space-x-3">
              <MapPin className="h-4 w-4 text-muted-foreground mt-0.5" />
              <div className="text-sm">
                <div className="font-medium">美甲工作室</div>
                <div className="text-muted-foreground">台北市信義區美甲街123號2樓</div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Phone className="h-4 w-4 text-muted-foreground" />
              <div className="text-sm">
                <span className="font-medium">聯絡電話：</span>
                <span className="text-muted-foreground">02-1234-5678</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Important Notes */}
        <Card>
          <CardContent className="pt-6">
            <h3 className="font-medium mb-3 text-amber-700">重要提醒</h3>
            <div className="text-sm text-muted-foreground space-y-2">
              <div className="flex items-start space-x-2">
                <div className="w-1 h-1 bg-amber-500 rounded-full mt-2 flex-shrink-0"></div>
                <span>請準時到達，建議提前10分鐘抵達</span>
              </div>
              <div className="flex items-start space-x-2">
                <div className="w-1 h-1 bg-amber-500 rounded-full mt-2 flex-shrink-0"></div>
                <span>如需取消或更改預約，請提前24小時致電聯繫</span>
              </div>
              <div className="flex items-start space-x-2">
                <div className="w-1 h-1 bg-amber-500 rounded-full mt-2 flex-shrink-0"></div>
                <span>遲到超過15分鐘，我們可能需要重新安排時段</span>
              </div>
              <div className="flex items-start space-x-2">
                <div className="w-1 h-1 bg-amber-500 rounded-full mt-2 flex-shrink-0"></div>
                <span>如有任何問題，歡迎隨時聯繫我們</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="space-y-3">
          <Button 
            onClick={onNewBooking}
            className="w-full h-12"
          >
            預約其他服務
          </Button>
          
          <div className="flex space-x-3">
            <Button variant="outline" className="flex-1">
              <Phone className="h-4 w-4 mr-2" />
              聯繫店家
            </Button>
            <Button variant="outline" className="flex-1">
              <Star className="h-4 w-4 mr-2" />
              加入最愛
            </Button>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-muted-foreground pt-4">
          感謝您選擇我們的服務，期待為您打造完美的美甲體驗！
        </div>
      </div>
    </div>
  );
}
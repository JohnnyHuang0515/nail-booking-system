import React, { useState, useEffect } from 'react';
import DateSelectionPage from './components/customer/DateSelectionPage';
import TimeSelectionPage from './components/customer/TimeSelectionPage';
import ServiceSelectionPage from './components/customer/ServiceSelectionPage';
import ConfirmationPage from './components/customer/ConfirmationPage';
import SuccessPage from './components/customer/SuccessPage';
import LoadingPage from './components/customer/LoadingPage';
import ErrorPage from './components/customer/ErrorPage';
import customerApiService from './services/api';
import liffService from './services/liff';
import authService from './services/auth';

type BookingStep = 'date' | 'time' | 'service' | 'confirmation' | 'success' | 'loading' | 'error';

export default function App() {
  const [currentStep, setCurrentStep] = useState<BookingStep>('loading');
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedTime, setSelectedTime] = useState<string>('');
  const [selectedServices, setSelectedServices] = useState<any[]>([]);
  const [selectedStaffId, setSelectedStaffId] = useState<number>(1); // 預設員工 ID
  const [customerInfo, setCustomerInfo] = useState<any>(null);
  const [bookingResult, setBookingResult] = useState<any>(null);
  const [lineUser, setLineUser] = useState<any>(null);
  const [merchantInfo, setMerchantInfo] = useState<any>(null);
  const [isReady, setIsReady] = useState(false);

  // 初始化：LIFF + 認證 + 商家資訊
  useEffect(() => {
    const initialize = async () => {
      try {
        setCurrentStep('loading');
        
        // 1. 初始化 LIFF
        const liffSuccess = await liffService.initialize();
        let userProfile = null;
        
        if (liffSuccess) {
          userProfile = liffService.getUserProfile();
          setLineUser(userProfile);
          console.log('✅ LIFF 初始化成功，用戶:', userProfile?.displayName);
          
          // 2. 認證 LINE 用戶
          if (userProfile) {
            const authResult = await authService.authenticateLineUser(userProfile);
            if (!authResult.success) {
              console.error('❌ 認證失敗:', authResult.error);
              setCurrentStep('error');
              return;
            }
            console.log('✅ 用戶認證成功');
          }
        } else {
          console.log('⚠️  非 LIFF 環境或未登入');
        }
        
        // 3. 載入商家資訊
        try {
          const merchant = await customerApiService.getMerchantInfo();
          setMerchantInfo(merchant);
          customerApiService.setMerchantId(merchant.id);
          customerApiService.setMerchantSlug(merchant.slug);
          console.log('✅ 商家資訊已載入:', merchant.name);
        } catch (error) {
          console.error('⚠️  載入商家資訊失敗，使用預設值:', error);
          // 使用預設值
          customerApiService.setMerchantId('00000000-0000-0000-0000-000000000001');
          customerApiService.setMerchantSlug('nail-abc');
        }
        
        setIsReady(true);
        setCurrentStep('date');
        
      } catch (error) {
        console.error('❌ 初始化失敗:', error);
        setCurrentStep('error');
      }
    };

    initialize();
  }, []);

  const handleDateSelect = (date: string, staffId: number) => {
    setSelectedDate(date);
    setSelectedStaffId(staffId);
    setCurrentStep('time');
  };

  const handleTimeSelect = (time: string, date: string) => {
    setSelectedTime(time);
    setSelectedDate(date);
    setCurrentStep('service');
  };

  const handleServiceSelect = (services: any[], date: string, time: string) => {
    setSelectedServices(services);
    setSelectedDate(date);
    setSelectedTime(time);
    setCurrentStep('confirmation');
  };

  const handleConfirmation = async (info: any) => {
    setCustomerInfo(info);
    setCurrentStep('loading');
    
    try {
      // 組合日期與時間為 ISO datetime
      const startDateTime = new Date(`${selectedDate}T${selectedTime}:00+08:00`);
      
      // 建立預約請求（符合後端 DTO）
      const bookingRequest = {
        merchant_id: customerApiService.getMerchantId(),
        customer: {
          line_user_id: lineUser?.userId,
          name: info.name,
          phone: info.phone,
          email: info.email || undefined,
        },
        staff_id: selectedStaffId,
        start_at: startDateTime.toISOString(),
        items: selectedServices.map(service => ({
          service_id: service.id,
          option_ids: [],
        })),
        notes: info.notes || undefined,
      };

      console.log('📤 提交預約:', bookingRequest);
      
      const result = await customerApiService.createBooking(bookingRequest);
      console.log('✅ 預約成功:', result);
      
      setBookingResult(result);
      setCurrentStep('success');
    } catch (error) {
      console.error('❌ 預約失敗:', error);
      setCurrentStep('error');
    }
  };

  const handleNewBooking = () => {
    setCurrentStep('date');
    setSelectedDate('');
    setSelectedTime('');
    setSelectedServices([]);
    setCustomerInfo(null);
    setBookingResult(null);
  };

  const handleError = () => {
    setCurrentStep('error');
  };

  const renderStep = () => {
    switch (currentStep) {
      case 'date':
        return <DateSelectionPage onNext={handleDateSelect} selectedStaffId={selectedStaffId} />;
      case 'time':
        return (
          <TimeSelectionPage
            selectedDate={selectedDate}
            selectedStaffId={selectedStaffId}
            onNext={handleTimeSelect}
            onBack={() => setCurrentStep('date')}
          />
        );
      case 'service':
        return (
          <ServiceSelectionPage
            selectedDate={selectedDate}
            selectedTime={selectedTime}
            onNext={handleServiceSelect}
            onBack={() => setCurrentStep('time')}
          />
        );
      case 'confirmation':
        return (
          <ConfirmationPage
            selectedDate={selectedDate}
            selectedTime={selectedTime}
            selectedServices={selectedServices}
            lineUser={lineUser}
            onNext={handleConfirmation}
            onBack={() => setCurrentStep('service')}
          />
        );
      case 'success':
        return (
          <SuccessPage
            selectedDate={selectedDate}
            selectedTime={selectedTime}
            selectedServices={selectedServices}
            customerInfo={customerInfo}
            bookingResult={bookingResult}
            onNewBooking={handleNewBooking}
          />
        );
      case 'loading':
        return <LoadingPage message="正在處理您的預約..." />;
      case 'error':
        return (
          <ErrorPage
            onRetry={() => setCurrentStep('date')}
            onGoHome={() => setCurrentStep('date')}
          />
        );
      default:
        return <DateSelectionPage onNext={handleDateSelect} />;
    }
  };

  return renderStep();
}


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

type BookingStep = 'date' | 'time' | 'service' | 'confirmation' | 'success' | 'loading' | 'error';

export default function App() {
  const [currentStep, setCurrentStep] = useState<BookingStep>('date');
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedTime, setSelectedTime] = useState<string>('');
  const [selectedService, setSelectedService] = useState<any>(null);
  const [customerInfo, setCustomerInfo] = useState<any>(null);
  const [lineUser, setLineUser] = useState<any>(null);
  const [merchantContext, setMerchantContext] = useState<any>(null);
  const [isLiffReady, setIsLiffReady] = useState(false);

  // 初始化 LIFF
  useEffect(() => {
    const initLiff = async () => {
      try {
        const success = await liffService.initialize();
        
        // 獲取商家上下文
        const merchantContext = liffService.getMerchantContext();
        if (merchantContext) {
          setMerchantContext(merchantContext);
          // 設定 API 服務的商家 ID
          customerApiService.setMerchantId(merchantContext.merchant_id);
          console.log('商家上下文已設定:', merchantContext);
        } else {
          // 如果沒有商家上下文，使用正確的商家 ID
          const defaultMerchantId = '00000000-0000-0000-0000-000000000001';
          customerApiService.setMerchantId(defaultMerchantId);
          console.log('使用預設商家 ID:', defaultMerchantId);
        }
        
        if (success) {
          const userProfile = liffService.getUserProfile();
          setLineUser(userProfile);
          console.log('LIFF 初始化成功，用戶資料:', userProfile);
        }
        
        setIsLiffReady(true);
      } catch (error) {
        console.error('LIFF 初始化失敗:', error);
        // 即使失敗也要設定預設商家 ID
        const defaultMerchantId = '00000000-0000-0000-0000-000000000001';
        customerApiService.setMerchantId(defaultMerchantId);
        setIsLiffReady(true);
      }
    };

    initLiff();
  }, []);

  const handleDateSelect = (date: string) => {
    setSelectedDate(date);
    setCurrentStep('time');
  };

  const handleTimeSelect = (time: string, date: string) => {
    setSelectedTime(time);
    setSelectedDate(date);
    setCurrentStep('service');
  };

  const handleServiceSelect = (service: any, date: string, time: string) => {
    setSelectedService(service);
    setSelectedDate(date);
    setSelectedTime(time);
    setCurrentStep('confirmation');
  };

  const handleConfirmation = async (info: any) => {
    setCustomerInfo(info);
    setCurrentStep('loading');
    
    try {
      // 提交預約到後端API
      const bookingData = {
        customer_name: info.name,
        customer_phone: info.phone,
        customer_email: info.email,
        service_id: selectedService.id,
        appointment_date: selectedDate,
        appointment_time: selectedTime,
        notes: info.notes,
        // 包含 LINE 用戶資訊
        line_user_id: lineUser?.userId,
        line_display_name: lineUser?.displayName,
        line_picture_url: lineUser?.pictureUrl
      };

      const result = await customerApiService.submitBooking(bookingData);
      console.log('預約成功:', result);
      setCurrentStep('success');
    } catch (error) {
      console.error('預約失敗:', error);
      setCurrentStep('error');
    }
  };

  const handleNewBooking = () => {
    setCurrentStep('date');
    setSelectedDate('');
    setSelectedTime('');
    setSelectedService(null);
    setCustomerInfo(null);
  };

  const handleError = () => {
    setCurrentStep('error');
  };

  const renderStep = () => {
    switch (currentStep) {
      case 'date':
        return <DateSelectionPage onNext={handleDateSelect} />;
      case 'time':
        return (
          <TimeSelectionPage
            selectedDate={selectedDate}
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
            selectedService={selectedService}
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
            selectedService={selectedService}
            customerInfo={customerInfo}
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


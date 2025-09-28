import React, { useState } from 'react';
import DateSelectionPage from './components/customer/DateSelectionPage';
import TimeSelectionPage from './components/customer/TimeSelectionPage';
import ServiceSelectionPage from './components/customer/ServiceSelectionPage';
import ConfirmationPage from './components/customer/ConfirmationPage';
import SuccessPage from './components/customer/SuccessPage';
import LoadingPage from './components/customer/LoadingPage';
import ErrorPage from './components/customer/ErrorPage';

type BookingStep = 'date' | 'time' | 'service' | 'confirmation' | 'success' | 'loading' | 'error';

export default function App() {
  const [currentStep, setCurrentStep] = useState<BookingStep>('date');
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedTime, setSelectedTime] = useState<string>('');
  const [selectedService, setSelectedService] = useState<any>(null);
  const [customerInfo, setCustomerInfo] = useState<any>(null);

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

  const handleConfirmation = (info: any) => {
    setCustomerInfo(info);
    setCurrentStep('loading');
    
    // 模擬預約處理
    setTimeout(() => {
      setCurrentStep('success');
    }, 2000);
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


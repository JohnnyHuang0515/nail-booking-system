import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Alert, Badge } from 'react-bootstrap';
import { useBooking } from '../components/BookingContext';
import { useNavigate } from 'react-router-dom';
import { appointmentAPI } from '../services/api';

const ConfirmationPage: React.FC = () => {
  const { state, dispatch } = useBooking();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    });
  };

  const formatTime = (time: string) => {
    return time.substring(0, 5);
  };

  const formatPrice = (price: number) => {
    return `NT$ ${price.toLocaleString()}`;
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) {
      return `${minutes} 分鐘`;
    } else {
      const hours = Math.floor(minutes / 60);
      const remainingMinutes = minutes % 60;
      return remainingMinutes > 0 
        ? `${hours} 小時 ${remainingMinutes} 分鐘`
        : `${hours} 小時`;
    }
  };

  const handleConfirmBooking = async () => {
    if (!state.user || !state.selectedService || !state.selectedDate || !state.selectedTime) {
      dispatch({ type: 'SET_ERROR', payload: '預約資訊不完整' });
      return;
    }


    setIsSubmitting(true);
    try {
      await appointmentAPI.createAppointment({
        user_id: state.user.id,
        service_id: state.selectedService.id,
        appointment_date: state.selectedDate,
        appointment_time: state.selectedTime,
      });

      navigate('/success');
    } catch (error) {
      console.error('預約錯誤:', error);
      dispatch({ type: 'SET_ERROR', payload: '預約失敗，請稍後再試' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const isReadyToBook = state.user && state.selectedService && state.selectedDate && state.selectedTime;

  return (
    <Container className="py-4">
      <Row className="justify-content-center">
        <Col md={8} lg={6}>
          <Card className="shadow-sm">
            <Card.Header className="bg-primary text-white text-center">
              <h4 className="mb-0">✅ 確認預約資訊</h4>
            </Card.Header>
            <Card.Body className="p-4">
              {state.error && (
                <Alert variant="warning" className="mb-3">
                  {state.error}
                </Alert>
              )}

              <div className="booking-summary">
                <h5 className="text-center mb-4">預約摘要</h5>
                
                {/* 服務資訊 */}
                {state.selectedService && (
                  <div className="summary-item mb-3">
                    <Row className="align-items-center">
                      <Col xs={4}>
                        <strong>服務項目</strong>
                      </Col>
                      <Col xs={8}>
                        <div>
                          <div>{state.selectedService.name}</div>
                          <div className="d-flex align-items-center mt-1">
                            <Badge bg="secondary" className="me-2">
                              {formatDuration(state.selectedService.duration_minutes)}
                            </Badge>
                            <span className="text-primary fw-bold">
                              {formatPrice(state.selectedService.price)}
                            </span>
                          </div>
                        </div>
                      </Col>
                    </Row>
                  </div>
                )}

                {/* 預約時間 */}
                {state.selectedDate && state.selectedTime && (
                  <div className="summary-item mb-3">
                    <Row className="align-items-center">
                      <Col xs={4}>
                        <strong>預約時間</strong>
                      </Col>
                      <Col xs={8}>
                        <div>
                          <div>{formatDate(state.selectedDate)}</div>
                          <div className="text-primary fw-bold">
                            {formatTime(state.selectedTime)}
                          </div>
                        </div>
                      </Col>
                    </Row>
                  </div>
                )}

                {/* 顧客資訊 */}
                {state.user && (
                  <div className="summary-item mb-3">
                    <Row className="align-items-center">
                      <Col xs={4}>
                        <strong>顧客姓名</strong>
                      </Col>
                      <Col xs={8}>
                        <div>{state.user.name || '未設定'}</div>
                      </Col>
                    </Row>
                  </div>
                )}
              </div>

              <div className="text-center mt-4">
                <Button 
                  variant="success" 
                  size="lg" 
                  className="me-2"
                  onClick={handleConfirmBooking}
                  disabled={!isReadyToBook || isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      預約中...
                    </>
                  ) : (
                    '確認預約'
                  )}
                </Button>
                
                <Button 
                  variant="outline-secondary" 
                  size="lg"
                  onClick={() => navigate('/service-selection')}
                  disabled={isSubmitting}
                >
                  修改服務
                </Button>
              </div>

              <div className="text-center mt-3">
                <Button 
                  variant="outline-secondary" 
                  onClick={() => navigate('/service-selection')}
                  disabled={isSubmitting}
                >
                  ← 重新選擇服務
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default ConfirmationPage;

import React, { useEffect } from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { useBooking } from '../components/BookingContext';
import { liffService } from '../utils/liff';

const SuccessPage: React.FC = () => {
  const { state } = useBooking();

  useEffect(() => {
    // 3秒後自動關閉 LIFF 視窗
    const timer = setTimeout(() => {
      liffService.closeWindow();
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

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

  const handleCloseWindow = () => {
    liffService.closeWindow();
  };

  return (
    <Container className="py-4">
      <Row className="justify-content-center">
        <Col md={8} lg={6}>
          <Card className="shadow-sm border-success">
            <Card.Header className="bg-success text-white text-center">
              <h4 className="mb-0">🎉 預約成功！</h4>
            </Card.Header>
            <Card.Body className="p-4 text-center">
              <div className="mb-4">
                <div className="success-icon mb-3">
                  <i className="fas fa-check-circle text-success" style={{ fontSize: '4rem' }}></i>
                </div>
                <h5 className="text-success mb-3">預約已成功建立</h5>
                <p className="text-muted">
                  感謝您的預約！我們已收到您的預約資訊，並會盡快與您確認。
                </p>
              </div>

              {state.selectedService && state.selectedDate && state.selectedTime && (
                <div className="booking-details bg-light p-3 rounded mb-4">
                  <h6 className="mb-3">預約詳情</h6>
                  <div className="row text-start">
                    <div className="col-6">
                      <strong>服務項目：</strong>
                    </div>
                    <div className="col-6">
                      {state.selectedService.name}
                    </div>
                    <div className="col-6">
                      <strong>預約日期：</strong>
                    </div>
                    <div className="col-6">
                      {formatDate(state.selectedDate)}
                    </div>
                    <div className="col-6">
                      <strong>預約時間：</strong>
                    </div>
                    <div className="col-6">
                      {formatTime(state.selectedTime)}
                    </div>
                    <div className="col-6">
                      <strong>服務費用：</strong>
                    </div>
                    <div className="col-6">
                      NT$ {state.selectedService.price.toLocaleString()}
                    </div>
                  </div>
                </div>
              )}

              <div className="mb-3">
                <p className="text-muted small">
                  我們會透過 LINE 訊息與您確認預約詳情
                </p>
              </div>

              <Button 
                variant="success" 
                size="lg" 
                onClick={handleCloseWindow}
                className="w-100"
              >
                關閉視窗
              </Button>

              <p className="text-muted small mt-3">
                視窗將在 3 秒後自動關閉
              </p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default SuccessPage;

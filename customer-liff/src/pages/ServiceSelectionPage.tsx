import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Alert, Badge } from 'react-bootstrap';
import { useBooking } from '../components/BookingContext';
import { useNavigate } from 'react-router-dom';
import { serviceAPI } from '../services/api';
import { Service } from '../types';

const ServiceSelectionPage: React.FC = () => {
  const { state, dispatch } = useBooking();
  const navigate = useNavigate();
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!state.selectedDate || !state.selectedTime) {
      navigate('/');
      return;
    }

    loadServices();
  }, [navigate]);

  const loadServices = async () => {
    setLoading(true);
    try {
      const availableServices = await serviceAPI.getServices();
      setServices(availableServices.filter(service => service.is_active));
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: '無法載入服務項目' });
    } finally {
      setLoading(false);
    }
  };

  const handleServiceSelect = (service: Service) => {
    dispatch({ type: 'SET_SELECTED_SERVICE', payload: service });
    navigate('/confirmation');
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-TW', {
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

  return (
    <Container className="py-4">
      <Row className="justify-content-center">
        <Col md={8} lg={6}>
          <Card className="shadow-sm">
            <Card.Header className="bg-primary text-white text-center">
              <h4 className="mb-0">💅 選擇服務項目</h4>
            </Card.Header>
            <Card.Body className="p-4">
              {state.error && (
                <Alert variant="warning" className="mb-3">
                  {state.error}
                </Alert>
              )}

              <div className="mb-3">
                <p className="text-muted text-center">
                  <strong>{state.selectedDate && formatDate(state.selectedDate)}</strong>
                  <br />
                  <small>{state.selectedTime && formatTime(state.selectedTime)}</small>
                </p>
                <p className="text-muted text-center small">
                  請選擇您想要的服務項目
                </p>
              </div>

              {loading ? (
                <div className="text-center">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">載入中...</span>
                  </div>
                </div>
              ) : services.length === 0 ? (
                <Alert variant="info" className="text-center">
                  <p className="mb-0">暫無可用服務項目</p>
                </Alert>
              ) : (
                <div className="service-list">
                  {services.map((service) => (
                    <Card 
                      key={service.id} 
                      className={`service-card mb-3 ${state.selectedService?.id === service.id ? 'border-primary' : ''}`}
                      style={{ cursor: 'pointer' }}
                      onClick={() => handleServiceSelect(service)}
                    >
                      <Card.Body className="p-3">
                        <Row className="align-items-center">
                          <Col xs={8}>
                            <h6 className="mb-1">{service.name}</h6>
                            <div className="d-flex align-items-center">
                              <Badge bg="secondary" className="me-2">
                                {formatDuration(service.duration_minutes)}
                              </Badge>
                              <small className="text-muted">
                                {formatPrice(service.price)}
                              </small>
                            </div>
                          </Col>
                          <Col xs={4} className="text-end">
                            <Button 
                              variant={state.selectedService?.id === service.id ? 'primary' : 'outline-primary'}
                              size="sm"
                            >
                              {state.selectedService?.id === service.id ? '已選擇' : '選擇'}
                            </Button>
                          </Col>
                        </Row>
                      </Card.Body>
                    </Card>
                  ))}
                </div>
              )}

              <div className="text-center mt-3">
                <Button 
                  variant="outline-secondary" 
                  onClick={() => navigate('/time-selection')}
                >
                  ← 重新選擇時段
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default ServiceSelectionPage;

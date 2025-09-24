import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Alert } from 'react-bootstrap';
import { useBooking } from '../components/BookingContext';
import { useNavigate } from 'react-router-dom';
import { appointmentAPI } from '../services/api';
import { AvailableSlot } from '../types';

const TimeSelectionPage: React.FC = () => {
  const { state, dispatch } = useBooking();
  const navigate = useNavigate();
  const [slots, setSlots] = useState<AvailableSlot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!state.selectedDate) {
      navigate('/');
      return;
    }

    loadAvailableSlots();
  }, [state.selectedDate, navigate]);

  const loadAvailableSlots = async () => {
    if (!state.selectedDate) return;

    setLoading(true);
    try {
      const availableSlots = await appointmentAPI.getAvailableSlots(state.selectedDate);
      setSlots(availableSlots);
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: '無法載入可用時段' });
    } finally {
      setLoading(false);
    }
  };

  const handleTimeSelect = (time: string) => {
    dispatch({ type: 'SET_SELECTED_TIME', payload: time });
    navigate('/service-selection');
  };

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
    return time.substring(0, 5); // 只顯示 HH:MM
  };

  const availableSlots = slots.filter(slot => slot.available);

  return (
    <Container className="py-4">
      <Row className="justify-content-center">
        <Col md={8} lg={6}>
          <Card className="shadow-sm">
            <Card.Header className="bg-primary text-white text-center">
              <h4 className="mb-0">⏰ 選擇預約時段</h4>
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
                </p>
                <p className="text-muted text-center small">
                  請選擇您希望的預約時段
                </p>
              </div>

              {loading ? (
                <div className="text-center">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">載入中...</span>
                  </div>
                </div>
              ) : availableSlots.length === 0 ? (
                <Alert variant="info" className="text-center">
                  <p className="mb-0">該日期暫無可用時段</p>
                  <Button 
                    variant="outline-primary" 
                    size="sm" 
                    className="mt-2"
                    onClick={() => navigate('/')}
                  >
                    重新選擇日期
                  </Button>
                </Alert>
              ) : (
                <div className="time-grid">
                  {availableSlots.map((slot) => (
                    <Button
                      key={slot.time}
                      variant={state.selectedTime === slot.time ? 'primary' : 'outline-primary'}
                      className="time-button mb-2 w-100"
                      onClick={() => handleTimeSelect(slot.time)}
                    >
                      {formatTime(slot.time)}
                    </Button>
                  ))}
                </div>
              )}

              <div className="text-center mt-3">
                <Button 
                  variant="outline-secondary" 
                  onClick={() => navigate('/')}
                >
                  ← 重新選擇日期
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default TimeSelectionPage;

import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Alert } from 'react-bootstrap';
import { useBooking } from '../components/BookingContext';
import { useNavigate } from 'react-router-dom';
import { appointmentAPI } from '../services/api';

const DateSelectionPage: React.FC = () => {
  const { state, dispatch } = useBooking();
  const navigate = useNavigate();
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [loading, setLoading] = useState(false);
  const [availableDates, setAvailableDates] = useState<Set<string>>(new Set());

  // 生成當前月份的日曆
  const generateCalendarDays = () => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    const firstDay = new Date(year, month, 1);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay()); // 從週日開始
    
    const days = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    for (let i = 0; i < 42; i++) { // 6週 x 7天
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      
      const isCurrentMonth = date.getMonth() === month;
      const isPast = date < today;
      const isToday = date.getTime() === today.getTime();
      // 使用本地日期格式，避免時區轉換問題
      const dateString = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
      const hasAvailableSlots = availableDates.has(dateString);
      
      days.push({
        date: dateString,
        day: date.getDate(),
        isCurrentMonth,
        isPast,
        isToday,
        isSelected: state.selectedDate === dateString,
        hasAvailableSlots
      });
    }
    
    return days;
  };

  // 檢查當前月份所有日期的可用時段
  const checkAvailableDates = async (month: Date) => {
    setLoading(true);
    
    const year = month.getFullYear();
    const monthIndex = month.getMonth();
    const daysInMonth = new Date(year, monthIndex + 1, 0).getDate();
    const availableDatesSet = new Set<string>();
    
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    // 計算一個月後的日期
    const oneMonthLater = new Date(today);
    oneMonthLater.setMonth(today.getMonth() + 1);
    oneMonthLater.setHours(0, 0, 0, 0);
    
    // 檢查當前月份的所有日期，但限制在一個月內
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, monthIndex, day);
      if (date >= today && date <= oneMonthLater) {
        // 使用本地日期格式，避免時區轉換問題
        const dateString = `${year}-${String(monthIndex + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        try {
          const slots = await appointmentAPI.getAvailableSlots(dateString);
          const hasAvailableSlots = slots && slots.length > 0 && slots.some(slot => slot.available === true);
          
          if (hasAvailableSlots) {
            availableDatesSet.add(dateString);
          }
        } catch (error) {
          console.error(`Error checking slots for ${dateString}:`, error);
        }
      }
    }
    
    setAvailableDates(availableDatesSet);
    setLoading(false);
  };

  const handleDateSelect = async (date: string) => {
    dispatch({ type: 'SET_SELECTED_DATE', payload: date });
    
    // 直接導航到時間選擇頁面，因為我們已經在 checkAvailableDates 中檢查過了
    navigate('/time-selection');
  };

  const goToPreviousMonth = () => {
    setCurrentMonth(prev => {
      const newMonth = new Date(prev);
      newMonth.setMonth(prev.getMonth() - 1);
      return newMonth;
    });
  };

  const goToNextMonth = () => {
    setCurrentMonth(prev => {
      const newMonth = new Date(prev);
      newMonth.setMonth(prev.getMonth() + 1);
      return newMonth;
    });
  };

  const formatMonthYear = (date: Date) => {
    return date.toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'long'
    });
  };

  // 組件載入時檢查可用日期
  useEffect(() => {
    checkAvailableDates(currentMonth);
  }, [currentMonth]);

  const calendarDays = generateCalendarDays();
  const weekDays = ['日', '一', '二', '三', '四', '五', '六'];

  return (
    <Container className="py-4">
      <Row className="justify-content-center">
        <Col md={10} lg={8}>
          <Card className="shadow-sm">
            <Card.Header className="bg-primary text-white text-center">
              <h4 className="mb-0">📅 選擇預約日期</h4>
            </Card.Header>
            <Card.Body className="p-4">
              {state.error && (
                <Alert variant="warning" className="mb-3">
                  {state.error}
                </Alert>
              )}
              
              {/* 月份導航 */}
              <div className="d-flex justify-content-between align-items-center mb-4">
                <Button 
                  variant="outline-primary" 
                  onClick={goToPreviousMonth}
                  className="calendar-nav-btn"
                >
                  ← 上個月
                </Button>
                <h5 className="mb-0 text-primary fw-bold">
                  {formatMonthYear(currentMonth)}
                </h5>
                <Button 
                  variant="outline-primary" 
                  onClick={goToNextMonth}
                  className="calendar-nav-btn"
                >
                  下個月 →
                </Button>
              </div>

              {/* 星期標題 */}
              <div className="calendar-header mb-2">
                <Row className="text-center">
                  {weekDays.map(day => (
                    <Col key={day} className="calendar-weekday">
                      <strong className="text-muted">{day}</strong>
                    </Col>
                  ))}
                </Row>
              </div>

              {/* 日曆格子 */}
              <div className="calendar-grid">
                {Array.from({ length: 6 }, (_, weekIndex) => (
                  <Row key={weekIndex} className="calendar-week">
                    {calendarDays.slice(weekIndex * 7, (weekIndex + 1) * 7).map(day => (
                      <Col key={day.date} className="calendar-day-col p-1">
                        <Button
                          variant={
                            day.isSelected ? 'primary' :
                            day.isToday ? 'success' :
                            day.isPast || !day.isCurrentMonth || !day.hasAvailableSlots ? 'outline-secondary' :
                            'outline-primary'
                          }
                          className={`calendar-day-btn w-100 ${
                            day.isPast || !day.isCurrentMonth || !day.hasAvailableSlots ? 'disabled' : ''
                          }`}
                          onClick={() => !day.isPast && day.isCurrentMonth && day.hasAvailableSlots && handleDateSelect(day.date)}
                          disabled={day.isPast || !day.isCurrentMonth || !day.hasAvailableSlots || loading}
                        >
                          <div className="calendar-day-number">
                            {day.day}
                          </div>
                          {day.isToday && (
                            <div className="calendar-today-indicator">今天</div>
                          )}
                        </Button>
                      </Col>
                    ))}
                  </Row>
                ))}
              </div>

              {loading && (
                <div className="text-center mt-3">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">載入中...</span>
                  </div>
                </div>
              )}

              {/* 圖例 */}
              <div className="calendar-legend mt-4">
                <Row className="text-center">
                  <Col>
                    <div className="legend-item">
                      <div className="legend-color bg-primary"></div>
                      <small>已選擇</small>
                    </div>
                  </Col>
                  <Col>
                    <div className="legend-item">
                      <div className="legend-color bg-success"></div>
                      <small>今天</small>
                    </div>
                  </Col>
                  <Col>
                    <div className="legend-item">
                      <div className="legend-color bg-outline-primary"></div>
                      <small>可預約</small>
                    </div>
                  </Col>
                  <Col>
                    <div className="legend-item">
                      <div className="legend-color bg-secondary"></div>
                      <small>不可預約</small>
                    </div>
                  </Col>
                </Row>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default DateSelectionPage;

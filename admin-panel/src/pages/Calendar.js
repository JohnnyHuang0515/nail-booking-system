import React, { useState, useCallback, useRef } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { Paper, Box, Typography, CircularProgress, Alert } from '@mui/material';
import { getAppointments, createAppointment } from '../api/appointmentsApi';
import { format } from 'date-fns';
import AppointmentFormDialog from '../components/AppointmentFormDialog';

export default function Calendar() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedDateInfo, setSelectedDateInfo] = useState(null);
  const calendarRef = useRef(null);

  const handleFetchEvents = useCallback(async (fetchInfo, successCallback, failureCallback) => {
    try {
      setLoading(true);
      setError(null);
      const response = await getAppointments(fetchInfo.start, fetchInfo.end);
      const events = response.data.map(apt => ({
        id: apt.id,
        title: `[${apt.status}] - 顧客ID: ${apt.user_id.substring(0, 4)}`,
        start: `${apt.appointment_date}T${apt.appointment_time}`,
      }));
      successCallback(events);
    } catch (err) {
      setError('無法讀取預約資料');
      failureCallback(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleEventClick = (clickInfo) => {
    alert(`預約 ID: ${clickInfo.event.id}\n標題: ${clickInfo.event.title}`);
  };

  const handleDateClick = (arg) => {
    setSelectedDateInfo(arg);
    setIsFormOpen(true);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setSelectedDateInfo(null);
  };

  const handleFormSubmit = async (formData) => {
    try {
      const payload = {
        ...formData,
        appointment_date: format(formData.appointment_date, 'yyyy-MM-dd'),
        appointment_time: format(formData.appointment_time, 'HH:mm:ss'),
      };
      await createAppointment(payload);
      handleCloseForm();
      if (calendarRef.current) {
        calendarRef.current.getApi().refetchEvents();
      }
    } catch (err) {
      alert('新增預約失敗');
    }
  };

  return (
    <Box>
      <Typography variant="h5" component="h1" sx={{ color: 'secondary.main', mb: 2 }}>
        行事曆管理
      </Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <Paper sx={{ p: 2, position: 'relative' }}>
        {loading && <CircularProgress sx={{ position: 'absolute', top: '50%', left: '50%' }} />}
        <FullCalendar
          ref={calendarRef}
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="dayGridMonth"
          headerToolbar={{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
          }}
          events={handleFetchEvents}
          eventClick={handleEventClick}
          dateClick={handleDateClick}
          locale="zh-tw"
          eventColor="#FFD1DC"
          eventTextColor="#4F4A45"
          height="auto"
        />
      </Paper>
      {isFormOpen && (
        <AppointmentFormDialog
          open={isFormOpen}
          onClose={handleCloseForm}
          onSubmit={handleFormSubmit}
          appointment={selectedDateInfo ? { appointment_date: selectedDateInfo.date, appointment_time: selectedDateInfo.date } : null}
        />
      )}
    </Box>
  );
}

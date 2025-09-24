import axiosInstance from './axiosInstance';
import { format } from 'date-fns';

export const getAppointments = (startDate, endDate) => {
  const params = {
    start_date: format(startDate, 'yyyy-MM-dd'),
    end_date: format(endDate, 'yyyy-MM-dd'),
  };
  return axiosInstance.get('/appointments', { params });
};

export const createAppointment = (appointmentData) => {
  return axiosInstance.post('/appointments', appointmentData);
};

export const updateAppointmentStatus = (id, status) => {
  return axiosInstance.put(`/appointments/${id}/status`, { status });
};

export const deleteAppointment = (id) => {
  return axiosInstance.delete(`/appointments/${id}`);
};

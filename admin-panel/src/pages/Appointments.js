import React, { useState, useEffect } from 'react';
import { Box, Typography, Alert, CircularProgress } from '@mui/material';
import { appointmentsAPI, servicesAPI } from '../api';
import AppointmentsFilters from '../components/AppointmentsFilters';
import AppointmentsTable from '../components/AppointmentsTable';
import AppointmentFormDialog from '../components/AppointmentFormDialog';
import ConfirmDialog from '../components/ConfirmDialog';
import { format, startOfMonth, endOfMonth } from 'date-fns';

export default function Appointments() {
  const [appointments, setAppointments] = useState([]);
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    startDate: format(startOfMonth(new Date()), 'yyyy-MM-dd'),
    endDate: format(endOfMonth(new Date()), 'yyyy-MM-dd'),
    customerName: '',
    status: ''
  });
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);

  // 載入服務列表
  useEffect(() => {
    const fetchServices = async () => {
      try {
        const data = await servicesAPI.getServices();
        setServices(data);
      } catch (err) {
        console.error('Failed to fetch services:', err);
      }
    };
    fetchServices();
  }, []);

  // 載入預約列表
  useEffect(() => {
    const fetchAppointments = async () => {
      if (!filters.startDate || !filters.endDate) return;
      
      try {
        setLoading(true);
        setError(null);
        const data = await appointmentsAPI.getAppointments(filters.startDate, filters.endDate);
        
        // 前端篩選
        let filteredData = data;
        
        if (filters.customerName) {
          filteredData = filteredData.filter(appointment => 
            appointment.user?.name?.toLowerCase().includes(filters.customerName.toLowerCase())
          );
        }
        
        if (filters.status) {
          filteredData = filteredData.filter(appointment => 
            appointment.status === filters.status
          );
        }
        
        setAppointments(filteredData);
      } catch (err) {
        console.error('Failed to fetch appointments:', err);
        setError('無法載入預約資料');
      } finally {
        setLoading(false);
      }
    };

    fetchAppointments();
  }, [filters]);

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleAddAppointment = () => {
    setSelectedAppointment(null);
    setFormDialogOpen(true);
  };

  const handleEditAppointment = (appointment) => {
    setSelectedAppointment(appointment);
    setFormDialogOpen(true);
  };

  const handleDeleteAppointment = (appointment) => {
    setSelectedAppointment(appointment);
    setConfirmDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!selectedAppointment) return;
    
    try {
      await appointmentsAPI.deleteAppointment(selectedAppointment.id);
      // 重新載入資料
      const data = await appointmentsAPI.getAppointments(filters.startDate, filters.endDate);
      setAppointments(data);
      setConfirmDialogOpen(false);
      setSelectedAppointment(null);
    } catch (err) {
      console.error('Failed to delete appointment:', err);
      setError('刪除預約失敗');
    }
  };

  const handleFormSubmit = async (appointmentData) => {
    try {
      if (selectedAppointment) {
        // 更新預約
        await appointmentsAPI.updateAppointment(selectedAppointment.id, appointmentData);
      } else {
        // 新增預約
        await appointmentsAPI.createAppointment(appointmentData);
      }
      
      // 重新載入資料
      const data = await appointmentsAPI.getAppointments(filters.startDate, filters.endDate);
      setAppointments(data);
      setFormDialogOpen(false);
      setSelectedAppointment(null);
    } catch (err) {
      console.error('Failed to save appointment:', err);
      setError('儲存預約失敗');
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ color: 'text.primary', mb: 3 }}>
        預約管理
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <AppointmentsFilters
        filters={filters}
        onFiltersChange={handleFiltersChange}
        onAddAppointment={handleAddAppointment}
        services={services}
      />
      
      <AppointmentsTable
        appointments={appointments}
        onEdit={handleEditAppointment}
        onDelete={handleDeleteAppointment}
        loading={loading}
      />
      
      <AppointmentFormDialog
        open={formDialogOpen}
        onClose={() => setFormDialogOpen(false)}
        onSubmit={handleFormSubmit}
        appointment={selectedAppointment}
        services={services}
      />
      
      <ConfirmDialog
        open={confirmDialogOpen}
        onClose={() => setConfirmDialogOpen(false)}
        onConfirm={handleConfirmDelete}
        title="確認刪除"
        content={`確定要刪除 ${selectedAppointment?.user?.name || '此客戶'} 的預約嗎？`}
      />
    </Box>
  );
}

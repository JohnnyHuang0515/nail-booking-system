import React, { useState, useEffect } from 'react';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Select, MenuItem, InputLabel, FormControl } from '@mui/material';
import { DatePicker, TimePicker } from '@mui/x-date-pickers';
import { usersAPI, servicesAPI } from '../api';

export default function AppointmentFormDialog({ open, onClose, onSubmit, appointment }) {
  const [formData, setFormData] = useState({});
  const [users, setUsers] = useState([]);
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      fetchData();
    }
  }, [open]);

  useEffect(() => {
    if (appointment) {
      setFormData({
        ...appointment,
        appointment_date: new Date(appointment.appointment_date),
        appointment_time: new Date(`1970-01-01T${appointment.appointment_time}`),
      });
    } else {
      setFormData({ user_id: '', service_id: '', appointment_date: null, appointment_time: null });
    }
  }, [appointment, open]);

  // 當數據載入完成後，確保選中的值在可選選項中
  useEffect(() => {
    if (users.length > 0 && services.length > 0 && appointment) {
      const userExists = users.some(user => user.id === formData.user_id);
      const serviceExists = services.some(service => service.id === formData.service_id);
      
      if (!userExists || !serviceExists) {
        setFormData(prev => ({
          ...prev,
          user_id: userExists ? prev.user_id : '',
          service_id: serviceExists ? prev.service_id : ''
        }));
      }
    }
  }, [users, services, appointment, formData.user_id, formData.service_id]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [usersData, servicesData] = await Promise.all([
        usersAPI.getUsers(),
        servicesAPI.getServices()
      ]);
      setUsers(usersData);
      setServices(servicesData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = () => {
    onSubmit(formData);
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth>
      <DialogTitle>{appointment ? '編輯預約' : '新增預約'}</DialogTitle>
      <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
        <FormControl fullWidth>
          <InputLabel>顧客</InputLabel>
          <Select
            name="user_id"
            value={formData.user_id || ''}
            label="顧客"
            onChange={(e) => handleChange('user_id', e.target.value)}
            disabled={loading}
          >
            {users.map(user => <MenuItem key={user.id} value={user.id}>{user.name}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl fullWidth>
          <InputLabel>服務項目</InputLabel>
          <Select
            name="service_id"
            value={formData.service_id || ''}
            label="服務項目"
            onChange={(e) => handleChange('service_id', e.target.value)}
            disabled={loading}
          >
            {services.map(service => <MenuItem key={service.id} value={service.id}>{service.name}</MenuItem>)}
          </Select>
        </FormControl>
        <DatePicker
          label="預約日期"
          value={formData.appointment_date}
          onChange={(newValue) => handleChange('appointment_date', newValue)}
          slotProps={{
            textField: {
              fullWidth: true,
              variant: 'outlined'
            }
          }}
        />
        <TimePicker
          label="預約時間"
          value={formData.appointment_time}
          onChange={(newValue) => handleChange('appointment_time', newValue)}
          slotProps={{
            textField: {
              fullWidth: true,
              variant: 'outlined'
            }
          }}
        />
        <FormControl fullWidth>
          <InputLabel>狀態</InputLabel>
          <Select
            name="status"
            value={formData.status || 'BOOKED'}
            label="狀態"
            onChange={(e) => handleChange('status', e.target.value)}
            disabled={loading}
          >
            <MenuItem value="BOOKED">已預約</MenuItem>
            <MenuItem value="CONFIRMED">已確認</MenuItem>
            <MenuItem value="COMPLETED">已完成</MenuItem>
            <MenuItem value="CANCELLED">已取消</MenuItem>
            <MenuItem value="NO_SHOW">未到</MenuItem>
          </Select>
        </FormControl>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>取消</Button>
        <Button onClick={handleSubmit} variant="contained">儲存</Button>
      </DialogActions>
    </Dialog>
  );
}

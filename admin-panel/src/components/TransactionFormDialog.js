import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { zhTW } from 'date-fns/locale';

export default function TransactionFormDialog({
  open,
  onClose,
  onSave,
  transaction = null,
  customers = [],
  selectedCustomer = null
}) {
  const [formData, setFormData] = useState({
    user_id: '',
    amount: '',
    notes: '',
    appointment_date: null,
    appointment_time: null
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (open) {
      if (transaction) {
        // 編輯模式
        setFormData({
          user_id: transaction.user_id,
          amount: transaction.amount.toString(),
          notes: transaction.notes || '',
          appointment_date: transaction.appointment_date ? new Date(transaction.appointment_date) : null,
          appointment_time: transaction.appointment_time ? new Date(`2000-01-01T${transaction.appointment_time}`) : null
        });
      } else {
        // 新增模式
        setFormData({
          user_id: selectedCustomer?.id || '',
          amount: '',
          notes: '',
          appointment_date: null,
          appointment_time: null
        });
      }
      setErrors({});
    }
  }, [open, transaction, selectedCustomer]);

  const handleChange = (field) => (event) => {
    const value = event.target.value;
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // 清除對應的錯誤
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleDateChange = (field) => (date) => {
    setFormData(prev => ({
      ...prev,
      [field]: date
    }));
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.user_id) {
      newErrors.user_id = '請選擇顧客';
    }

    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      newErrors.amount = '請輸入有效的金額';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (!validateForm()) {
      return;
    }

    const transactionData = {
      user_id: formData.user_id,
      amount: parseFloat(formData.amount),
      notes: formData.notes,
      appointment_date: formData.appointment_date ? formData.appointment_date.toISOString().split('T')[0] : null,
      appointment_time: formData.appointment_time ? formData.appointment_time.toTimeString().split(' ')[0] : null
    };

    onSave(transactionData);
  };

  const handleClose = () => {
    setFormData({
      user_id: '',
      amount: '',
      notes: '',
      appointment_date: null,
      appointment_time: null
    });
    setErrors({});
    onClose();
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={zhTW}>
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {transaction ? '編輯消費紀錄' : '新增消費紀錄'}
        </DialogTitle>
        
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid size={12}>
              <FormControl fullWidth error={!!errors.user_id}>
                <InputLabel>顧客</InputLabel>
                <Select
                  value={formData.user_id}
                  onChange={handleChange('user_id')}
                  label="顧客"
                  disabled={!!selectedCustomer} // 如果已選擇顧客則禁用
                >
                  {customers.map((customer) => (
                    <MenuItem key={customer.id} value={customer.id}>
                      {customer.name || '未命名客戶'} {customer.phone && `(${customer.phone})`}
                    </MenuItem>
                  ))}
                </Select>
                {errors.user_id && <Alert severity="error" sx={{ mt: 1 }}>{errors.user_id}</Alert>}
              </FormControl>
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="消費金額"
                type="number"
                value={formData.amount}
                onChange={handleChange('amount')}
                error={!!errors.amount}
                helperText={errors.amount}
                inputProps={{ min: 0, step: 1 }}
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <DatePicker
                label="關聯預約日期"
                value={formData.appointment_date}
                onChange={handleDateChange('appointment_date')}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    helperText: '可選：關聯到特定預約日期'
                  }
                }}
              />
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <TimePicker
                label="關聯預約時間"
                value={formData.appointment_time}
                onChange={handleDateChange('appointment_time')}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    helperText: '可選：關聯到特定預約時間'
                  }
                }}
              />
            </Grid>

            <Grid size={12}>
              <TextField
                fullWidth
                label="備註"
                multiline
                rows={3}
                value={formData.notes}
                onChange={handleChange('notes')}
                placeholder="輸入消費相關備註..."
              />
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose}>取消</Button>
          <Button onClick={handleSave} variant="contained">
            {transaction ? '更新' : '新增'}
          </Button>
        </DialogActions>
      </Dialog>
    </LocalizationProvider>
  );
}

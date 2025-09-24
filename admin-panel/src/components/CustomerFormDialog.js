import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Alert,
  Box
} from '@mui/material';

export default function CustomerFormDialog({ open, onClose, onSubmit, customer = null }) {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    line_user_id: ''
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (open) {
      if (customer) {
        // 編輯模式
        setFormData({
          name: customer.name || '',
          phone: customer.phone || '',
          line_user_id: customer.line_user_id || ''
        });
      } else {
        // 新增模式
        setFormData({
          name: '',
          phone: '',
          line_user_id: ''
        });
      }
      setErrors({});
    }
  }, [open, customer]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // 清除對應的錯誤
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = '請輸入顧客姓名';
    }

    if (formData.phone && !/^[0-9-+\s()]+$/.test(formData.phone)) {
      newErrors.phone = '請輸入有效的手機號碼';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validateForm()) {
      return;
    }

    const customerData = {
      name: formData.name.trim(),
      phone: formData.phone.trim() || null,
      line_user_id: formData.line_user_id.trim() || null
    };

    onSubmit(customerData);
  };

  const handleClose = () => {
    setFormData({
      name: '',
      phone: '',
      line_user_id: ''
    });
    setErrors({});
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {customer ? '編輯顧客' : '新增顧客'}
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ pt: 1 }}>
          <TextField
            autoFocus
            margin="dense"
            name="name"
            label="顧客姓名"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.name}
            onChange={handleChange}
            error={!!errors.name}
            helperText={errors.name}
            required
          />
          
          <TextField
            margin="dense"
            name="phone"
            label="手機號碼"
            type="tel"
            fullWidth
            variant="outlined"
            value={formData.phone}
            onChange={handleChange}
            error={!!errors.phone}
            helperText={errors.phone || '可選：輸入顧客的手機號碼'}
            placeholder="例如：0912-345-678"
          />
          
          <TextField
            margin="dense"
            name="line_user_id"
            label="LINE User ID"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.line_user_id}
            onChange={handleChange}
            helperText="可選：輸入顧客的 LINE User ID"
            placeholder="例如：U1234567890abcdef"
          />
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>取消</Button>
        <Button onClick={handleSubmit} variant="contained">
          {customer ? '儲存變更' : '新增顧客'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}


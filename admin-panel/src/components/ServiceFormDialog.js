import React, { useState, useEffect } from 'react';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, TextField, Switch, FormControlLabel } from '@mui/material';

export default function ServiceFormDialog({ open, onClose, onSubmit, service }) {
  const [formData, setFormData] = useState({
    name: '',
    price: '',
    duration_minutes: '',
    is_active: true,
  });

  useEffect(() => {
    if (service) {
      setFormData({
        name: service.name || '',
        price: service.price || '',
        duration_minutes: service.duration_minutes || '',
        is_active: service.is_active !== undefined ? service.is_active : true,
      });
    } else {
      // Reset form for new service
      setFormData({ name: '', price: '', duration_minutes: '', is_active: true });
    }
  }, [service, open]);

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = () => {
    // Basic validation
    if (!formData.name || !formData.price || !formData.duration_minutes) {
      alert('請填寫所有必填欄位');
      return;
    }
    onSubmit(formData);
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{service ? '編輯服務' : '新增服務'}</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          margin="dense"
          name="name"
          label="服務名稱"
          type="text"
          fullWidth
          variant="outlined"
          value={formData.name}
          onChange={handleChange}
        />
        <TextField
          margin="dense"
          name="price"
          label="價格"
          type="number"
          fullWidth
          variant="outlined"
          value={formData.price}
          onChange={handleChange}
        />
        <TextField
          margin="dense"
          name="duration_minutes"
          label="時長 (分鐘)"
          type="number"
          fullWidth
          variant="outlined"
          value={formData.duration_minutes}
          onChange={handleChange}
        />
        <FormControlLabel
          control={<Switch checked={formData.is_active} onChange={handleChange} name="is_active" />}
          label="啟用狀態"
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>取消</Button>
        <Button onClick={handleSubmit} variant="contained">{service ? '儲存變更' : '建立'}</Button>
      </DialogActions>
    </Dialog>
  );
}

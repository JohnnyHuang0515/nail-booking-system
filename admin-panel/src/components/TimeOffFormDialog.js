import React, { useState, useEffect } from 'react';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, TextField, Box } from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';

export default function TimeOffFormDialog({ open, onClose, onSubmit }) {
  const [startDateTime, setStartDateTime] = useState(null);
  const [endDateTime, setEndDateTime] = useState(null);
  const [reason, setReason] = useState('');

  // 當對話框關閉時重置表單
  useEffect(() => {
    if (!open) {
      setStartDateTime(null);
      setEndDateTime(null);
      setReason('');
    }
  }, [open]);

  const handleSubmit = () => {
    if (!startDateTime || !endDateTime) {
      alert('請選擇開始與結束時間');
      return;
    }
    
    const formData = { 
      start_datetime: startDateTime, 
      end_datetime: endDateTime, 
      reason: reason || null 
    };
    
    onSubmit(formData);
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="xs">
      <DialogTitle>新增休假</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <DateTimePicker
            label="開始時間"
            value={startDateTime}
            onChange={setStartDateTime}
            slotProps={{
              textField: {
                fullWidth: true,
                variant: 'outlined'
              }
            }}
          />
          <DateTimePicker
            label="結束時間"
            value={endDateTime}
            onChange={setEndDateTime}
            slotProps={{
              textField: {
                fullWidth: true,
                variant: 'outlined'
              }
            }}
          />
          <TextField
            label="事由 (選填)"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            fullWidth
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>取消</Button>
        <Button onClick={handleSubmit} variant="contained">建立</Button>
      </DialogActions>
    </Dialog>
  );
}

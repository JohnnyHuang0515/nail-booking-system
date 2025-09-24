import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Switch,
  FormControlLabel,
  Grid,
  Alert
} from '@mui/material';
import { TimePicker } from '@mui/x-date-pickers';
import { format } from 'date-fns';

const BusinessHoursEditDialog = ({ 
  open, 
  onClose, 
  onSave, 
  dayIndex, 
  dayName, 
  initialData 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [startTime, setStartTime] = useState(null);
  const [endTime, setEndTime] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (initialData) {
      setIsOpen(initialData.is_open);
      setStartTime(initialData.start_time);
      setEndTime(initialData.end_time);
    }
  }, [initialData]);

  const handleSave = () => {
    setError('');
    
    // 驗證
    if (isOpen && (!startTime || !endTime)) {
      setError('請設定開始和結束時間');
      return;
    }
    
    if (isOpen && startTime && endTime && startTime >= endTime) {
      setError('結束時間必須晚於開始時間');
      return;
    }

    const data = {
      day_of_week: dayIndex,
      is_open: isOpen,
      start_time: isOpen && startTime ? startTime : null,
      end_time: isOpen && endTime ? endTime : null
    };

    onSave(data);
    onClose();
  };

  const handleClose = () => {
    setError('');
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        編輯 {dayName} 營業時間
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {/* 營業開關 */}
          <Box sx={{ mb: 3 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={isOpen}
                  onChange={(e) => {
                    setIsOpen(e.target.checked);
                    if (!e.target.checked) {
                      setStartTime(null);
                      setEndTime(null);
                    }
                  }}
                />
              }
              label={
                <Typography variant="h6">
                  {isOpen ? '營業中' : '休息中'}
                </Typography>
              }
            />
          </Box>

          {/* 時間設定 */}
          {isOpen && (
            <Grid container spacing={3}>
              <Grid size={{ xs: 6 }}>
                <TimePicker
                  label="開始時間"
                  value={startTime}
                  onChange={(newValue) => setStartTime(newValue)}
                  sx={{ width: '100%' }}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      variant: 'outlined'
                    }
                  }}
                />
              </Grid>
              <Grid size={{ xs: 6 }}>
                <TimePicker
                  label="結束時間"
                  value={endTime}
                  onChange={(newValue) => setEndTime(newValue)}
                  sx={{ width: '100%' }}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      variant: 'outlined'
                    }
                  }}
                />
              </Grid>
            </Grid>
          )}

          {/* 預覽 */}
          {isOpen && startTime && endTime && (
            <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary">
                預覽：
              </Typography>
              <Typography variant="h6" color="success.main">
                {format(startTime, 'HH:mm')} - {format(endTime, 'HH:mm')}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                營業時長：{Math.round((endTime - startTime) / (1000 * 60 * 60))} 小時
              </Typography>
            </Box>
          )}
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>
          取消
        </Button>
        <Button onClick={handleSave} variant="contained">
          儲存
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default BusinessHoursEditDialog;


import React from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem,
  Grid,
  Paper,
  Typography
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { zhTW } from 'date-fns/locale';
import AddIcon from '@mui/icons-material/Add';

export default function AppointmentsFilters({ 
  filters, 
  onFiltersChange, 
  onAddAppointment,
  services = []
}) {
  const handleDateChange = (field) => (newValue) => {
    onFiltersChange({
      ...filters,
      [field]: newValue ? newValue.toISOString().split('T')[0] : ''
    });
  };

  const handleTextChange = (field) => (event) => {
    onFiltersChange({
      ...filters,
      [field]: event.target.value
    });
  };

  const handleSelectChange = (field) => (event) => {
    onFiltersChange({
      ...filters,
      [field]: event.target.value
    });
  };

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6" sx={{ 
          color: 'primary.main',
          fontWeight: 500,
          fontSize: '1.25rem',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}>
          💅 預約管理
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={onAddAppointment}
          sx={{ 
            background: 'linear-gradient(135deg, #F5E6D3 0%, #FFB6C1 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #E8D5C4 0%, #FF91A4 100%)',
            },
            borderRadius: 3,
            px: 3,
            py: 1,
            fontSize: '14px',
            fontWeight: 500,
          }}
        >
          ✨ 新增預約
        </Button>
      </Box>
      
      <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={zhTW}>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <DatePicker
              label="開始日期"
              value={filters.startDate ? new Date(filters.startDate) : null}
              onChange={handleDateChange('startDate')}
              slotProps={{
                textField: {
                  fullWidth: true,
                  size: 'small'
                }
              }}
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <DatePicker
              label="結束日期"
              value={filters.endDate ? new Date(filters.endDate) : null}
              onChange={handleDateChange('endDate')}
              slotProps={{
                textField: {
                  fullWidth: true,
                  size: 'small'
                }
              }}
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <TextField
              label="顧客姓名"
              value={filters.customerName || ''}
              onChange={handleTextChange('customerName')}
              fullWidth
              size="small"
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <FormControl fullWidth size="small">
              <InputLabel>預約狀態</InputLabel>
              <Select
                value={filters.status || ''}
                onChange={handleSelectChange('status')}
                label="預約狀態"
              >
                <MenuItem value="">全部</MenuItem>
                <MenuItem value="BOOKED">已預約</MenuItem>
                <MenuItem value="CONFIRMED">已確認</MenuItem>
                <MenuItem value="COMPLETED">已完成</MenuItem>
                <MenuItem value="CANCELLED">已取消</MenuItem>
                <MenuItem value="NO_SHOW">未到</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </LocalizationProvider>
    </Paper>
  );
}

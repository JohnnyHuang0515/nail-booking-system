import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  Typography,
  Box
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { format } from 'date-fns';
import { zhTW } from 'date-fns/locale';

export default function AppointmentsTable({ 
  appointments = [], 
  onEdit, 
  onDelete,
  loading = false 
}) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'BOOKED':
        return 'default';
      case 'CONFIRMED':
        return 'primary';
      case 'COMPLETED':
        return 'success';
      case 'CANCELLED':
        return 'error';
      case 'NO_SHOW':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'BOOKED':
        return '已預約';
      case 'CONFIRMED':
        return '已確認';
      case 'COMPLETED':
        return '已完成';
      case 'CANCELLED':
        return '已取消';
      case 'NO_SHOW':
        return '未到';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>載入中...</Typography>
      </Paper>
    );
  }

  if (appointments.length === 0) {
    return (
      <Paper sx={{ p: 3 }}>
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body1" color="text.secondary">
            沒有找到符合條件的預約
          </Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow sx={{ backgroundColor: 'background.paper' }}>
            <TableCell>預約日期</TableCell>
            <TableCell>時間</TableCell>
            <TableCell>顧客</TableCell>
            <TableCell>服務項目</TableCell>
            <TableCell>狀態</TableCell>
            <TableCell align="center">操作</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {appointments.map((appointment) => (
            <TableRow key={appointment.id} hover>
              <TableCell>
                {format(new Date(appointment.appointment_date), 'yyyy/MM/dd', { locale: zhTW })}
              </TableCell>
              <TableCell>
                {format(new Date(`2000-01-01T${appointment.appointment_time}`), 'HH:mm', { locale: zhTW })}
              </TableCell>
              <TableCell>
                {appointment.user?.name || '未命名客戶'}
              </TableCell>
              <TableCell>
                {appointment.service?.name || '未知服務'}
              </TableCell>
              <TableCell>
                <Chip 
                  label={getStatusText(appointment.status)} 
                  size="small" 
                  color={getStatusColor(appointment.status)}
                />
              </TableCell>
              <TableCell align="center">
                <IconButton 
                  size="small" 
                  onClick={() => onEdit(appointment)}
                  color="primary"
                >
                  <EditIcon />
                </IconButton>
                <IconButton 
                  size="small" 
                  onClick={() => onDelete(appointment)}
                  color="error"
                >
                  <DeleteIcon />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

import React from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemSecondaryAction,
  Button,
  Box,
  Chip
} from '@mui/material';
import { format } from 'date-fns';
import { zhTW } from 'date-fns/locale';

export default function TodayAppointmentsList({ appointments = [] }) {
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

  if (appointments.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ color: 'secondary.main' }}>
            今日預約
          </Typography>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body1" color="text.secondary">
              今日暫無預約
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ color: 'secondary.main' }}>
          今日預約
        </Typography>
        <List>
          {appointments.map((appointment) => (
            <ListItem key={appointment.id} divider>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                      {appointment.user?.name || '未命名客戶'}
                    </Typography>
                    <Chip 
                      label={getStatusText(appointment.status)} 
                      size="small" 
                      color={getStatusColor(appointment.status)}
                    />
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {format(new Date(`2000-01-01T${appointment.appointment_time}`), 'HH:mm', { locale: zhTW })}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {appointment.service?.name || '未知服務'}
                    </Typography>
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                <Button size="small" variant="outlined">
                  查看詳情
                </Button>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
}

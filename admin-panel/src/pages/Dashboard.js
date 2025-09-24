import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Grid, 
  Typography, 
  Card, 
  CardContent, 
  CircularProgress, 
  Alert,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider
} from '@mui/material';
import { dashboardAPI } from '../api';
import { format } from 'date-fns';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PeopleIcon from '@mui/icons-material/People';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import StarIcon from '@mui/icons-material/Star';

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const data = await dashboardAPI.getSummary();
        setDashboardData(data);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('無法載入儀表板資料');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress sx={{ color: 'secondary.main' }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  const todayAppointments = dashboardData?.today_appointments || [];
  const weeklySummary = dashboardData?.weekly_summary || {};

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

  return (
    <Box>
      {/* 標題區域 */}
      <Box sx={{ mb: 4, textAlign: 'center', position: 'relative' }}>
        <Typography variant="h4" gutterBottom sx={{ 
          color: 'primary.main', 
          fontWeight: 600,
          position: 'relative',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: -10,
            left: '50%',
            transform: 'translateX(-50%)',
            width: 60,
            height: 3,
            background: 'linear-gradient(90deg, #FFB6C1, #B0E0E6, #F5E6D3)',
            borderRadius: 2,
          },
        }}>
          ✨ 美甲預約管理系統 ✨
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary', mt: 1 }}>
          歡迎回來！今天是 {format(new Date(), 'yyyy年MM月dd日')}
        </Typography>
      </Box>

      {/* 統計卡片 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, rgba(255, 182, 193, 0.1), rgba(255, 255, 255, 0.8))',
            border: '1px solid rgba(255, 182, 193, 0.2)',
          }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar sx={{ 
                bgcolor: 'secondary.main', 
                mx: 'auto', 
                mb: 2,
                width: 56,
                height: 56,
              }}>
                <AccessTimeIcon />
              </Avatar>
              <Typography variant="h4" sx={{ color: 'secondary.main', fontWeight: 600 }}>
                {todayAppointments.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                今日預約
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, rgba(176, 224, 230, 0.1), rgba(255, 255, 255, 0.8))',
            border: '1px solid rgba(176, 224, 230, 0.2)',
          }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar sx={{ 
                bgcolor: 'accent.main', 
                mx: 'auto', 
                mb: 2,
                width: 56,
                height: 56,
              }}>
                <PeopleIcon />
              </Avatar>
              <Typography variant="h4" sx={{ color: 'accent.main', fontWeight: 600 }}>
                {weeklySummary.total_appointments || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                本週預約
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, rgba(245, 230, 211, 0.1), rgba(255, 255, 255, 0.8))',
            border: '1px solid rgba(245, 230, 211, 0.2)',
          }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar sx={{ 
                bgcolor: 'primary.main', 
                mx: 'auto', 
                mb: 2,
                width: 56,
                height: 56,
              }}>
                <TrendingUpIcon />
              </Avatar>
              <Typography variant="h4" sx={{ color: 'primary.main', fontWeight: 600 }}>
                {weeklySummary.completion_rate || 0}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                完成率
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, rgba(255, 182, 193, 0.1), rgba(176, 224, 230, 0.1), rgba(255, 255, 255, 0.8))',
            border: '1px solid rgba(255, 182, 193, 0.2)',
          }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar sx={{ 
                bgcolor: 'secondary.main', 
                mx: 'auto', 
                mb: 2,
                width: 56,
                height: 56,
              }}>
                <StarIcon />
              </Avatar>
              <Typography variant="h4" sx={{ color: 'secondary.main', fontWeight: 600 }}>
                4.8
              </Typography>
              <Typography variant="body2" color="text.secondary">
                客戶滿意度
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 今日預約列表 */}
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ 
                color: 'primary.main',
                display: 'flex',
                alignItems: 'center',
                gap: 1,
              }}>
                <AccessTimeIcon />
                今日預約安排
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {todayAppointments.length > 0 ? (
                <List>
                  {todayAppointments.map((appointment, index) => (
                    <React.Fragment key={appointment.id}>
                      <ListItem sx={{ px: 0 }}>
                        <ListItemAvatar>
                          <Avatar sx={{ 
                            bgcolor: 'secondary.main',
                            width: 40,
                            height: 40,
                          }}>
                            {appointment.user?.name?.charAt(0) || '客'}
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="subtitle1">
                                {appointment.user?.name || '未命名客戶'}
                              </Typography>
                              <Chip 
                                label={getStatusText(appointment.status)} 
                                size="small"
                                sx={{ 
                                  bgcolor: 'secondary.light',
                                  color: 'white',
                                  fontSize: '0.75rem',
                                }}
                              />
                            </Box>
                          }
                          secondary={
                            <Typography variant="body2" color="text.secondary">
                              {appointment.appointment_time} - {appointment.service?.name || '服務項目'}
                            </Typography>
                          }
                        />
                      </ListItem>
                      {index < todayAppointments.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    今日暫無預約安排 ✨
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* 快速操作 */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>
                快速操作
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Chip 
                  label="查看本週預約" 
                  clickable
                  sx={{ 
                    bgcolor: 'secondary.light',
                    color: 'white',
                    '&:hover': { bgcolor: 'secondary.main' }
                  }}
                />
                <Chip 
                  label="新增預約" 
                  clickable
                  sx={{ 
                    bgcolor: 'accent.light',
                    color: 'white',
                    '&:hover': { bgcolor: 'accent.main' }
                  }}
                />
                <Chip 
                  label="查看行事曆" 
                  clickable
                  sx={{ 
                    bgcolor: 'primary.light',
                    color: 'white',
                    '&:hover': { bgcolor: 'primary.main' }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

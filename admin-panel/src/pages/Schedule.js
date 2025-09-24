import React, { useState, useEffect, useCallback } from 'react';
import { Box, Button, Typography, Grid, Card, CardContent, Switch, FormControlLabel, CircularProgress, Alert, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton, Paper, Tabs, Tab } from '@mui/material';
import { TimePicker } from '@mui/x-date-pickers';
import DeleteIcon from '@mui/icons-material/Delete';
import { getBusinessHours, setBusinessHours, getAllTimeOff, addTimeOff, deleteTimeOff } from '../api/scheduleApi';
import { parse, format } from 'date-fns';
import TimeOffFormDialog from '../components/TimeOffFormDialog';
import ConfirmDialog from '../components/ConfirmDialog';
import BusinessHoursCard from '../components/BusinessHoursCard';
import BusinessHoursTemplate from '../components/BusinessHoursTemplate';
import BusinessHoursEditDialog from '../components/BusinessHoursEditDialog';

const weekDays = ['週一', '週二', '週三', '週四', '週五', '週六', '週日'];

const BusinessHoursSection = () => {
  const [businessHours, setBusinessHours] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingDayIndex, setEditingDayIndex] = useState(null);
  const [tabValue, setTabValue] = useState(0);

  const fetchHours = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getBusinessHours();
      const apiHours = response.data;
      
      const formattedHours = weekDays.map((day, index) => {
        const found = apiHours.find(h => h.day_of_week === index);
        if (found) {
          return {
            day_of_week: index,
            is_open: true,
            start_time: parse(found.start_time, 'HH:mm:ss', new Date()),
            end_time: parse(found.end_time, 'HH:mm:ss', new Date()),
          };
        }
        return { day_of_week: index, is_open: false, start_time: null, end_time: null };
      });
      setBusinessHours(formattedHours);
    } catch (err) {
      setError('無法讀取營業時間');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHours();
  }, [fetchHours]);

  const handleEditDay = (dayIndex) => {
    setEditingDayIndex(dayIndex);
    setEditDialogOpen(true);
  };

  const handleToggleDay = (dayIndex) => {
    const newHours = [...businessHours];
    newHours[dayIndex].is_open = !newHours[dayIndex].is_open;
    if (!newHours[dayIndex].is_open) {
      newHours[dayIndex].start_time = null;
      newHours[dayIndex].end_time = null;
    }
    setBusinessHours(newHours);
    handleSaveHours(newHours);
  };

  const handleSaveDay = (dayData) => {
    const newHours = [...businessHours];
    newHours[dayData.day_of_week] = dayData;
    setBusinessHours(newHours);
    handleSaveHours(newHours);
  };

  const handleApplyTemplate = (templateData) => {
    const newHours = [...businessHours];
    const startTime = parse(templateData.startTime, 'HH:mm', new Date());
    const endTime = parse(templateData.endTime, 'HH:mm', new Date());
    
    templateData.days.forEach(dayIndex => {
      newHours[dayIndex] = {
        day_of_week: dayIndex,
        is_open: true,
        start_time: startTime,
        end_time: endTime
      };
    });
    
    setBusinessHours(newHours);
    handleSaveHours(newHours);
  };

  const handleSaveHours = async (hoursToSave = businessHours) => {
    try {
      const payload = hoursToSave
        .filter(day => day.is_open && day.start_time && day.end_time)
        .map(day => ({
          day_of_week: day.day_of_week,
          start_time: format(day.start_time, 'HH:mm:ss'),
          end_time: format(day.end_time, 'HH:mm:ss'),
        }));
      await setBusinessHours(payload);
    } catch (err) {
      alert('儲存失敗！');
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          每週營業時間
        </Typography>
        
        {/* 標籤頁切換 */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab label="週曆視圖" />
            <Tab label="詳細設定" />
          </Tabs>
        </Box>

        {/* 週曆視圖 */}
        {tabValue === 0 && (
          <Box>
            {/* 模板快速設定 */}
            <BusinessHoursTemplate onApplyTemplate={handleApplyTemplate} />
            
            {/* 週曆卡片 */}
            <Grid container spacing={2}>
              {businessHours.map((day, index) => (
                <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }} key={index}>
                  <BusinessHoursCard
                    dayName={weekDays[index]}
                    dayIndex={index}
                    isOpen={day.is_open}
                    startTime={day.start_time}
                    endTime={day.end_time}
                    onEdit={handleEditDay}
                    onToggle={handleToggleDay}
                  />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* 詳細設定視圖 */}
        {tabValue === 1 && (
          <Grid container spacing={2} alignItems="center">
            {businessHours.map((day, index) => (
              <React.Fragment key={index}>
                <Grid size={{ xs: 2 }}>
                  <FormControlLabel
                    control={
                      <Switch 
                        checked={day.is_open} 
                        onChange={() => handleToggleDay(index)} 
                      />
                    }
                    label={weekDays[index]}
                  />
                </Grid>
                <Grid size={{ xs: 5 }}>
                  <TimePicker
                    label="開始時間"
                    value={day.start_time}
                    onChange={(newValue) => {
                      const newHours = [...businessHours];
                      newHours[index].start_time = newValue;
                      setBusinessHours(newHours);
                    }}
                    disabled={!day.is_open}
                    sx={{ width: '100%' }}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        variant: 'outlined'
                      }
                    }}
                  />
                </Grid>
                <Grid size={{ xs: 5 }}>
                  <TimePicker
                    label="結束時間"
                    value={day.end_time}
                    onChange={(newValue) => {
                      const newHours = [...businessHours];
                      newHours[index].end_time = newValue;
                      setBusinessHours(newHours);
                    }}
                    disabled={!day.is_open}
                    sx={{ width: '100%' }}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        variant: 'outlined'
                      }
                    }}
                  />
                </Grid>
              </React.Fragment>
            ))}
          </Grid>
        )}

        {/* 編輯對話框 */}
        <BusinessHoursEditDialog
          open={editDialogOpen}
          onClose={() => setEditDialogOpen(false)}
          onSave={handleSaveDay}
          dayIndex={editingDayIndex}
          dayName={editingDayIndex !== null ? weekDays[editingDayIndex] : ''}
          initialData={editingDayIndex !== null ? businessHours[editingDayIndex] : null}
        />
      </CardContent>
    </Card>
  );
};

const TimeOffSection = () => {
  const [timeOffs, setTimeOffs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  const fetchAllTimeOffs = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getAllTimeOff();
      setTimeOffs(response.data);
    } catch (err) {
      console.error('查詢休假失敗:', err);
      setError('無法讀取休假列表');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllTimeOffs();
  }, [fetchAllTimeOffs]);

  const handleAddSubmit = async (formData) => {
    try {
      const response = await addTimeOff(formData);
      await fetchAllTimeOffs();
      setIsFormOpen(false);
      alert('休假新增成功！');
    } catch (err) {
      console.error('新增休假失敗:', err);
      alert(`新增失敗！錯誤: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handleDelete = (id) => {
    setDeletingId(id);
    setIsConfirmOpen(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      await deleteTimeOff(deletingId);
      await fetchAllTimeOffs();
      setIsConfirmOpen(false);
      setDeletingId(null);
    } catch (err) {
      alert('刪除失敗！');
    }
  };

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">特殊休假管理</Typography>
          <Button variant="outlined" color="secondary" onClick={() => setIsFormOpen(true)}>新增休假</Button>
        </Box>
        {loading ? <CircularProgress /> : error ? <Alert severity="error">{error}</Alert> : (
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>開始時間</TableCell>
                  <TableCell>結束時間</TableCell>
                  <TableCell>事由</TableCell>
                  <TableCell align="right">操作</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {timeOffs.map((to) => (
                  <TableRow key={to.id}>
                    <TableCell>{format(new Date(to.start_datetime), 'yyyy-MM-dd HH:mm')}</TableCell>
                    <TableCell>{format(new Date(to.end_datetime), 'yyyy-MM-dd HH:mm')}</TableCell>
                    <TableCell>{to.reason}</TableCell>
                    <TableCell align="right">
                      <IconButton size="small" onClick={() => handleDelete(to.id)}><DeleteIcon /></IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
      <TimeOffFormDialog open={isFormOpen} onClose={() => setIsFormOpen(false)} onSubmit={handleAddSubmit} />
      <ConfirmDialog 
        open={isConfirmOpen} 
        onClose={() => setIsConfirmOpen(false)} 
        onConfirm={handleDeleteConfirm} 
        title="確認刪除"
        message="您確定要刪除這段休假嗎？"
      />
    </Card>
  );
};

export default function Schedule() {
  return (
    <Box>
      <Typography variant="h5" component="h1" sx={{ color: 'secondary.main', mb: 2 }}>
        時段管理
      </Typography>
      <BusinessHoursSection />
      <TimeOffSection />
    </Box>
  );
}

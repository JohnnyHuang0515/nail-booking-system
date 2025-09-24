import React from 'react';
import { Card, CardContent, Typography, Box, Chip, IconButton, Tooltip } from '@mui/material';
import { Edit as EditIcon, Schedule as ScheduleIcon } from '@mui/icons-material';
import { format } from 'date-fns';

const BusinessHoursCard = ({ dayName, dayIndex, isOpen, startTime, endTime, onEdit, onToggle }) => {
  const getStatusColor = () => {
    return isOpen ? 'success' : 'default';
  };

  const getStatusText = () => {
    if (!isOpen) return '休息';
    if (!startTime || !endTime) return '未設定';
    return `${format(startTime, 'HH:mm')} - ${format(endTime, 'HH:mm')}`;
  };

  const getStatusIcon = () => {
    return isOpen ? <ScheduleIcon /> : null;
  };

  return (
    <Card 
      sx={{ 
        height: '100%',
        border: isOpen ? '2px solid' : '1px solid',
        borderColor: isOpen ? 'success.main' : 'divider',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          boxShadow: 3,
          transform: 'translateY(-2px)'
        }
      }}
    >
      <CardContent sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* 星期標題 */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold' }}>
            {dayName}
          </Typography>
          <Tooltip title="編輯時間">
            <IconButton size="small" onClick={() => onEdit(dayIndex)}>
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        {/* 營業狀態 */}
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <Chip
            icon={getStatusIcon()}
            label={getStatusText()}
            color={getStatusColor()}
            variant={isOpen ? 'filled' : 'outlined'}
            sx={{ 
              mb: 1,
              fontWeight: 'bold',
              fontSize: '0.875rem'
            }}
          />
          
          {/* 營業時長顯示 */}
          {isOpen && startTime && endTime && (
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
              營業 {Math.round((endTime - startTime) / (1000 * 60 * 60))} 小時
            </Typography>
          )}
        </Box>

        {/* 開關按鈕 */}
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
          <Chip
            label={isOpen ? '營業中' : '休息中'}
            color={isOpen ? 'success' : 'default'}
            variant="outlined"
            clickable
            onClick={() => onToggle(dayIndex)}
            sx={{ 
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: isOpen ? 'success.light' : 'action.hover'
              }
            }}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default BusinessHoursCard;


import React from 'react';
import { Card, CardContent, Typography, Button, Box, Chip } from '@mui/material';
import { Business as BusinessIcon, Weekend as WeekendIcon, Settings as SettingsIcon } from '@mui/icons-material';

const BusinessHoursTemplate = ({ onApplyTemplate }) => {
  const templates = [
    {
      id: 'standard',
      name: '標準營業時間',
      description: '週一至週五',
      icon: <BusinessIcon />,
      hours: '09:00-18:00',
      days: [0, 1, 2, 3, 4], // 週一到週五
      color: 'primary'
    },
    {
      id: 'weekend',
      name: '週末營業時間',
      description: '週六至週日',
      icon: <WeekendIcon />,
      hours: '10:00-16:00',
      days: [5, 6], // 週六週日
      color: 'secondary'
    },
    {
      id: 'custom',
      name: '彈性營業時間',
      description: '自訂時間',
      icon: <SettingsIcon />,
      hours: '自訂',
      days: [],
      color: 'info'
    }
  ];

  const handleApplyTemplate = (template) => {
    if (template.id === 'custom') {
      // 自訂模板不執行任何操作，只是提示
      return;
    }
    
    const templateData = {
      days: template.days,
      startTime: template.hours.split('-')[0],
      endTime: template.hours.split('-')[1]
    };
    
    onApplyTemplate(templateData);
  };

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SettingsIcon />
          快速模板設定
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          選擇常用模板快速套用營業時間設定
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          {templates.map((template) => (
            <Card 
              key={template.id}
              sx={{ 
                minWidth: 200,
                cursor: template.id !== 'custom' ? 'pointer' : 'default',
                transition: 'all 0.2s ease-in-out',
                '&:hover': template.id !== 'custom' ? {
                  boxShadow: 3,
                  transform: 'translateY(-2px)'
                } : {}
              }}
              onClick={() => handleApplyTemplate(template)}
            >
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  {template.icon}
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                    {template.name}
                  </Typography>
                </Box>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {template.description}
                </Typography>
                
                <Chip
                  label={template.hours}
                  color={template.color}
                  size="small"
                  sx={{ mb: 1 }}
                />
                
                {template.id !== 'custom' && (
                  <Button
                    size="small"
                    variant="outlined"
                    color={template.color}
                    sx={{ width: '100%' }}
                  >
                    套用模板
                  </Button>
                )}
                
                {template.id === 'custom' && (
                  <Typography variant="caption" color="text.secondary">
                    點擊個別日期進行自訂設定
                  </Typography>
                )}
              </CardContent>
            </Card>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

export default BusinessHoursTemplate;


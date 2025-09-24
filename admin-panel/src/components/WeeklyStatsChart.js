import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, Typography, Box } from '@mui/material';

export default function WeeklyStatsChart({ data }) {
  const chartData = [
    { day: '週一', count: data?.monday || 0 },
    { day: '週二', count: data?.tuesday || 0 },
    { day: '週三', count: data?.wednesday || 0 },
    { day: '週四', count: data?.thursday || 0 },
    { day: '週五', count: data?.friday || 0 },
    { day: '週六', count: data?.saturday || 0 },
    { day: '週日', count: data?.sunday || 0 },
  ];

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ color: 'secondary.main' }}>
          本週預約統計
        </Typography>
        <Box sx={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Bar 
                dataKey="count" 
                fill="#8A9AAB" 
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  );
}

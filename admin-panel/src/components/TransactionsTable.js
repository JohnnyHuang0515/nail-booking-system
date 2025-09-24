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
  Typography,
  Box,
  Chip
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { format } from 'date-fns';
import { zhTW } from 'date-fns/locale';

export default function TransactionsTable({ 
  transactions = [], 
  onEdit, 
  onDelete,
  loading = false 
}) {

  if (loading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>載入中...</Typography>
      </Paper>
    );
  }

  if (transactions.length === 0) {
    return (
      <Paper sx={{ p: 3 }}>
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body1" color="text.secondary">
            沒有找到消費紀錄
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
            <TableCell>消費日期</TableCell>
            <TableCell>金額</TableCell>
            <TableCell>關聯預約</TableCell>
            <TableCell>服務項目</TableCell>
            <TableCell>備註</TableCell>
            <TableCell align="center">操作</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {transactions.map((transaction) => (
            <TableRow key={transaction.id} hover>
              <TableCell>
                {format(new Date(transaction.created_at), 'yyyy/MM/dd HH:mm', { locale: zhTW })}
              </TableCell>
              <TableCell>
                <Typography variant="body1" sx={{ fontWeight: 'medium', color: 'secondary.main' }}>
                  ${parseFloat(transaction.amount).toFixed(0)}
                </Typography>
              </TableCell>
              <TableCell>
                {transaction.appointment_date ? (
                  <Box>
                    <Typography variant="body2">
                      {format(new Date(transaction.appointment_date), 'yyyy/MM/dd', { locale: zhTW })}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {transaction.appointment_time ? 
                        format(new Date(`2000-01-01T${transaction.appointment_time}`), 'HH:mm', { locale: zhTW }) : 
                        '無時間資訊'
                      }
                    </Typography>
                  </Box>
                ) : (
                  <Chip label="無關聯預約" size="small" color="default" variant="outlined" />
                )}
              </TableCell>
              <TableCell>
                {transaction.service_name || '無服務資訊'}
              </TableCell>
              <TableCell>
                <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {transaction.notes || '無備註'}
                </Typography>
              </TableCell>
              <TableCell align="center">
                <IconButton 
                  size="small" 
                  onClick={() => onEdit(transaction)}
                  color="primary"
                >
                  <EditIcon />
                </IconButton>
                <IconButton 
                  size="small" 
                  onClick={() => onDelete(transaction)}
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

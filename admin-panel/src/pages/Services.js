import React, { useState, useEffect, useCallback } from 'react';
import { Box, Button, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton, CircularProgress, Alert } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { getServices, createService, updateService, deleteService } from '../api/servicesApi';
import ServiceFormDialog from '../components/ServiceFormDialog';
import ConfirmDialog from '../components/ConfirmDialog';

export default function Services() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingService, setEditingService] = useState(null);

  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [deletingServiceId, setDeletingServiceId] = useState(null);

  const fetchServices = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getServices();
      setServices(response.data);
    } catch (err) {
      setError('無法讀取服務列表');
      console.error('Fetch services error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchServices();
  }, [fetchServices]);

  const handleOpenFormDialog = (service = null) => {
    setEditingService(service);
    setIsFormOpen(true);
  };

  const handleCloseFormDialog = () => {
    setIsFormOpen(false);
    setEditingService(null);
  };

  const handleOpenConfirmDialog = (id) => {
    setDeletingServiceId(id);
    setIsConfirmOpen(true);
  };

  const handleCloseConfirmDialog = () => {
    setIsConfirmOpen(false);
    setDeletingServiceId(null);
  };

  const handleFormSubmit = async (formData) => {
    try {
      const serviceData = { ...formData, price: parseFloat(formData.price), duration_minutes: parseInt(formData.duration_minutes, 10) };
      if (editingService) {
        await updateService(editingService.id, serviceData);
      } else {
        await createService(serviceData);
      }
      fetchServices();
      handleCloseFormDialog();
    } catch (err) {
      console.error('儲存服務失敗:', err);
      alert('儲存失敗！');
    }
  };

  const handleDeleteConfirm = async () => {
    try {
      await deleteService(deletingServiceId);
      fetchServices();
      handleCloseConfirmDialog();
    } catch (err) {
      console.error('刪除服務失敗:', err);
      alert('刪除失敗！');
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" component="h1" sx={{ color: 'secondary.main' }}>
          服務管理
        </Typography>
        <Button variant="contained" color="primary" onClick={() => handleOpenFormDialog()}>
          新增服務
        </Button>
      </Box>
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>服務名稱</TableCell>
                <TableCell>價格</TableCell>
                <TableCell>時長 (分鐘)</TableCell>
                <TableCell>狀態</TableCell>
                <TableCell align="right">操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {services.map((service) => (
                <TableRow key={service.id}>
                  <TableCell>{service.name}</TableCell>
                  <TableCell>{service.price}</TableCell>
                  <TableCell>{service.duration_minutes}</TableCell>
                  <TableCell>{service.is_active ? '啟用' : '停用'}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => handleOpenFormDialog(service)}><EditIcon /></IconButton>
                    <IconButton size="small" onClick={() => handleOpenConfirmDialog(service.id)}><DeleteIcon /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
      <ServiceFormDialog
        open={isFormOpen}
        onClose={handleCloseFormDialog}
        onSubmit={handleFormSubmit}
        service={editingService}
      />
      <ConfirmDialog
        open={isConfirmOpen}
        onClose={handleCloseConfirmDialog}
        onConfirm={handleDeleteConfirm}
        title="確認刪除"
        message="您確定要刪除這項服務嗎？此操作無法復原。"
      />
    </Box>
  );
}

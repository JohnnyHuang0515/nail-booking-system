import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { format } from 'date-fns';
import { zhTW } from 'date-fns/locale';
import { usersAPI, transactionsAPI } from '../api';
import TransactionsTable from '../components/TransactionsTable';
import TransactionFormDialog from '../components/TransactionFormDialog';
import CustomerFormDialog from '../components/CustomerFormDialog';
import ConfirmDialog from '../components/ConfirmDialog';

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [transactionDialogOpen, setTransactionDialogOpen] = useState(false);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [customerFilter, setCustomerFilter] = useState('');
  
  // 顧客管理狀態
  const [customerDialogOpen, setCustomerDialogOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [deleteCustomerDialogOpen, setDeleteCustomerDialogOpen] = useState(false);
  const [deletingCustomerId, setDeletingCustomerId] = useState(null);

  // 載入顧客列表
  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        setLoading(true);
        const data = await usersAPI.getUsers();
        setCustomers(data);
      } catch (err) {
        console.error('Failed to fetch customers:', err);
        setError('載入顧客資料失敗');
      } finally {
        setLoading(false);
      }
    };
    fetchCustomers();
  }, []);

  // 載入交易記錄
  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setLoading(true);
        const data = await transactionsAPI.getTransactions();
        setTransactions(data);
      } catch (err) {
        console.error('Failed to fetch transactions:', err);
        setError('載入消費紀錄失敗');
      } finally {
        setLoading(false);
      }
    };
    fetchTransactions();
  }, []);

  const handleAddTransaction = () => {
    setSelectedTransaction(null);
    setTransactionDialogOpen(true);
  };

  const handleEditTransaction = (transaction) => {
    setSelectedTransaction(transaction);
    setTransactionDialogOpen(true);
  };

  const handleDeleteTransaction = (transaction) => {
    setSelectedTransaction(transaction);
    setConfirmDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!selectedTransaction) return;

    try {
      await transactionsAPI.deleteTransaction(selectedTransaction.id);
      setTransactions(transactions.filter(t => t.id !== selectedTransaction.id));
      setConfirmDialogOpen(false);
      setSelectedTransaction(null);
    } catch (err) {
      console.error('Failed to delete transaction:', err);
      setError('刪除消費紀錄失敗');
    }
  };

  const handleTransactionSave = async (transactionData) => {
    try {
      if (selectedTransaction) {
        // 更新交易
        const updatedTransaction = await transactionsAPI.updateTransaction(
          selectedTransaction.id,
          transactionData
        );
        setTransactions(transactions.map(t => 
          t.id === selectedTransaction.id ? updatedTransaction : t
        ));
      } else {
        // 新增交易
        const newTransaction = await transactionsAPI.createTransaction(transactionData);
        setTransactions([newTransaction, ...transactions]);
      }
      setTransactionDialogOpen(false);
      setSelectedTransaction(null);
    } catch (err) {
      console.error('Failed to save transaction:', err);
      setError('儲存消費紀錄失敗');
    }
  };

  // 顧客管理處理函數
  const handleAddCustomer = () => {
    setEditingCustomer(null);
    setCustomerDialogOpen(true);
  };

  const handleEditCustomer = (customer) => {
    setEditingCustomer(customer);
    setCustomerDialogOpen(true);
  };

  const handleDeleteCustomer = (customerId) => {
    setDeletingCustomerId(customerId);
    setDeleteCustomerDialogOpen(true);
  };

  const handleCustomerSave = async (customerData) => {
    try {
      if (editingCustomer) {
        // 更新顧客
        const updatedCustomer = await usersAPI.updateUser(editingCustomer.id, customerData);
        setCustomers(customers.map(c => 
          c.id === editingCustomer.id ? updatedCustomer : c
        ));
      } else {
        // 新增顧客
        const newCustomer = await usersAPI.createUser(customerData);
        setCustomers([newCustomer, ...customers]);
      }
      setCustomerDialogOpen(false);
      setEditingCustomer(null);
    } catch (err) {
      console.error('Failed to save customer:', err);
      setError('儲存顧客資料失敗');
    }
  };

  const handleCustomerDeleteConfirm = async () => {
    try {
      await usersAPI.deleteUser(deletingCustomerId);
      setCustomers(customers.filter(c => c.id !== deletingCustomerId));
      
      // 如果刪除的是當前選中的顧客，清除選擇
      if (selectedCustomer?.id === deletingCustomerId) {
        setSelectedCustomer(null);
      }
      
      setDeleteCustomerDialogOpen(false);
      setDeletingCustomerId(null);
    } catch (err) {
      console.error('Failed to delete customer:', err);
      setError('刪除顧客失敗');
    }
  };

  const filteredCustomers = customers.filter(customer =>
    customer.name?.toLowerCase().includes(customerFilter.toLowerCase()) ||
    customer.phone?.includes(customerFilter)
  );

  const getCustomerTransactionSummary = (customerId) => {
    const customerTransactions = transactions.filter(t => t.user_id === customerId);
    const totalAmount = customerTransactions.reduce((sum, t) => sum + parseFloat(t.amount), 0);
    return {
      count: customerTransactions.length,
      totalAmount: totalAmount
    };
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ color: 'secondary.main', mb: 3 }}>
        顧客管理
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* 顧客列表 */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" sx={{ color: 'secondary.main' }}>
                  顧客列表
                </Typography>
                <Box display="flex" gap={1} alignItems="center">
                  <TextField
                    size="small"
                    placeholder="搜尋顧客..."
                    value={customerFilter}
                    onChange={(e) => setCustomerFilter(e.target.value)}
                    sx={{ width: 200 }}
                  />
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={<AddIcon />}
                    onClick={handleAddCustomer}
                  >
                    新增顧客
                  </Button>
                </Box>
              </Box>
              
              {filteredCustomers.map((customer) => {
                const summary = getCustomerTransactionSummary(customer.id);
                return (
                  <Card 
                    key={customer.id} 
                    sx={{ 
                      mb: 1, 
                      backgroundColor: selectedCustomer?.id === customer.id ? 'primary.light' : 'background.paper',
                      '&:hover': { backgroundColor: 'primary.light' }
                    }}
                  >
                    <CardContent sx={{ py: 1 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                        <Box 
                          sx={{ flex: 1, cursor: 'pointer' }}
                          onClick={() => setSelectedCustomer(customer)}
                        >
                          <Typography variant="subtitle1" sx={{ fontWeight: 'medium' }}>
                            {customer.name || '未命名客戶'}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {customer.phone || '未提供電話'}
                          </Typography>
                          <Box display="flex" gap={1} mt={1}>
                            <Chip 
                              label={`${summary.count} 筆消費`} 
                              size="small" 
                              color="primary" 
                              variant="outlined"
                            />
                            <Chip 
                              label={`總計 $${summary.totalAmount.toFixed(0)}`} 
                              size="small" 
                              color="secondary" 
                              variant="outlined"
                            />
                          </Box>
                        </Box>
                        <Box display="flex" gap={0.5}>
                          <IconButton 
                            size="small" 
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEditCustomer(customer);
                            }}
                            color="primary"
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton 
                            size="small" 
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteCustomer(customer.id);
                            }}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                );
              })}
            </CardContent>
          </Card>
        </Grid>

        {/* 消費紀錄 */}
        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" sx={{ color: 'secondary.main' }}>
                  {selectedCustomer ? `${selectedCustomer.name || '未命名客戶'} 的消費紀錄` : '消費紀錄'}
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleAddTransaction}
                  disabled={!selectedCustomer}
                >
                  新增消費紀錄
                </Button>
              </Box>

              {selectedCustomer ? (
                <TransactionsTable
                  transactions={transactions.filter(t => t.user_id === selectedCustomer.id)}
                  onEdit={handleEditTransaction}
                  onDelete={handleDeleteTransaction}
                  loading={loading}
                />
              ) : (
                <Box textAlign="center" py={4}>
                  <Typography variant="body1" color="text.secondary">
                    請選擇一個顧客查看其消費紀錄
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 交易表單對話框 */}
      <TransactionFormDialog
        open={transactionDialogOpen}
        onClose={() => {
          setTransactionDialogOpen(false);
          setSelectedTransaction(null);
        }}
        onSave={handleTransactionSave}
        transaction={selectedTransaction}
        customers={customers}
        selectedCustomer={selectedCustomer}
      />

      {/* 顧客表單對話框 */}
      <CustomerFormDialog
        open={customerDialogOpen}
        onClose={() => {
          setCustomerDialogOpen(false);
          setEditingCustomer(null);
        }}
        onSubmit={handleCustomerSave}
        customer={editingCustomer}
      />

      {/* 確認刪除對話框 */}
      <ConfirmDialog
        open={confirmDialogOpen}
        onClose={() => {
          setConfirmDialogOpen(false);
          setSelectedTransaction(null);
        }}
        onConfirm={handleConfirmDelete}
        title="確認刪除"
        message="確定要刪除這筆消費紀錄嗎？此操作無法復原。"
      />

      {/* 確認刪除顧客對話框 */}
      <ConfirmDialog
        open={deleteCustomerDialogOpen}
        onClose={() => {
          setDeleteCustomerDialogOpen(false);
          setDeletingCustomerId(null);
        }}
        onConfirm={handleCustomerDeleteConfirm}
        title="確認刪除顧客"
        message="確定要刪除這個顧客嗎？此操作將同時刪除該顧客的所有消費紀錄，且無法復原。"
      />
    </Box>
  );
}

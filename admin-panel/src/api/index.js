import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dashboard API
export const dashboardAPI = {
  getSummary: async () => {
    const response = await api.get('/api/v1/dashboard/summary');
    return response.data;
  },
};

// Appointments API
export const appointmentsAPI = {
  getAppointments: async (startDate, endDate) => {
    const response = await api.get('/api/v1/appointments', {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },
  
  createAppointment: async (appointmentData) => {
    const response = await api.post('/api/v1/appointments', appointmentData);
    return response.data;
  },
  
  updateAppointment: async (id, appointmentData) => {
    const response = await api.put(`/api/v1/appointments/${id}`, appointmentData);
    return response.data;
  },
  
  deleteAppointment: async (id) => {
    const response = await api.delete(`/api/v1/appointments/${id}`);
    return response.data;
  },
};

// Users API
export const usersAPI = {
  getUsers: async () => {
    const response = await api.get('/api/v1/users');
    return response.data;
  },
  
  getUser: async (id) => {
    const response = await api.get(`/api/v1/users/${id}`);
    return response.data;
  },
  
  createUser: async (userData) => {
    const response = await api.post('/api/v1/users', userData);
    return response.data;
  },
  
  updateUser: async (id, userData) => {
    const response = await api.put(`/api/v1/users/${id}`, userData);
    return response.data;
  },
  
  deleteUser: async (id) => {
    const response = await api.delete(`/api/v1/users/${id}`);
    return response.data;
  },
};

// Services API
export const servicesAPI = {
  getServices: async () => {
    const response = await api.get('/api/v1/services');
    return response.data;
  },
  
  createService: async (serviceData) => {
    const response = await api.post('/api/v1/services', serviceData);
    return response.data;
  },
  
  updateService: async (id, serviceData) => {
    const response = await api.put(`/api/v1/services/${id}`, serviceData);
    return response.data;
  },
  
  deleteService: async (id) => {
    const response = await api.delete(`/api/v1/services/${id}`);
    return response.data;
  },
};

// Schedule API
export const scheduleAPI = {
  getBusinessHours: async () => {
    const response = await api.get('/api/v1/schedule/business_hours');
    return response.data;
  },
  
  setBusinessHours: async (hoursData) => {
    const response = await api.post('/api/v1/schedule/business_hours', hoursData);
    return response.data;
  },
  
  getTimeOff: async (forDate) => {
    const response = await api.get('/api/v1/schedule/time_off', {
      params: { for_date: forDate },
    });
    return response.data;
  },
  
  addTimeOff: async (timeOffData) => {
    const response = await api.post('/api/v1/schedule/time_off', timeOffData);
    return response.data;
  },
  
  deleteTimeOff: async (id) => {
    const response = await api.delete(`/api/v1/schedule/time_off/${id}`);
    return response.data;
  },
};

// Transactions API
export const transactionsAPI = {
  getTransactions: async (userId = null, startDate = null, endDate = null) => {
    const params = {};
    if (userId) params.user_id = userId;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const response = await api.get('/api/v1/transactions', { params });
    return response.data;
  },
  
  getTransaction: async (id) => {
    const response = await api.get(`/api/v1/transactions/${id}`);
    return response.data;
  },
  
  createTransaction: async (transactionData) => {
    const response = await api.post('/api/v1/transactions', transactionData);
    return response.data;
  },
  
  updateTransaction: async (id, transactionData) => {
    const response = await api.put(`/api/v1/transactions/${id}`, transactionData);
    return response.data;
  },
  
  deleteTransaction: async (id) => {
    const response = await api.delete(`/api/v1/transactions/${id}`);
    return response.data;
  },
  
  getUserTransactions: async (userId, startDate = null, endDate = null) => {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const response = await api.get(`/api/v1/users/${userId}/transactions`, { params });
    return response.data;
  },
};

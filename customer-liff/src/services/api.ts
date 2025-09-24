import axios from 'axios';
import { User, Service, Appointment, AvailableSlot } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 用戶相關 API
export const userAPI = {
  // 透過 LINE User ID 登入或註冊
  loginWithLine: async (lineUserId: string, profile?: any): Promise<User> => {
    const response = await api.post('/api/v1/users/login', {
      line_user_id: lineUserId,
      name: profile?.displayName,
    });
    return response.data;
  },

  // 更新用戶資料
  updateProfile: async (userId: string, data: Partial<User>): Promise<User> => {
    const response = await api.put(`/api/v1/users/${userId}`, data);
    return response.data;
  },
};

// 服務相關 API
export const serviceAPI = {
  // 取得所有可用服務
  getServices: async (): Promise<Service[]> => {
    const response = await api.get('/api/v1/services');
    return response.data;
  },
};

// 預約相關 API
export const appointmentAPI = {
  // 取得可用時段
  getAvailableSlots: async (date: string): Promise<AvailableSlot[]> => {
    const response = await api.get(`/api/v1/slots/${date}`);
    return response.data;
  },

  // 創建預約
  createAppointment: async (appointmentData: {
    user_id: string;
    service_id: string;
    appointment_date: string;
    appointment_time: string;
  }): Promise<Appointment> => {
    const response = await api.post('/api/v1/appointments', appointmentData);
    return response.data;
  },

  // 取得用戶的預約記錄
  getUserAppointments: async (userId: string): Promise<Appointment[]> => {
    const response = await api.get(`/api/v1/appointments?user_id=${userId}`);
    return response.data;
  },
};

export default api;

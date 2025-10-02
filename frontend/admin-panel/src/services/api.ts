const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T | null> {
    const url = `${this.baseURL}${endpoint}`;
    
    // 取得認證 token
    const token = localStorage.getItem('merchant_token');
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        if (response.status === 401) {
          // Token 過期或無效，清除本地儲存
          localStorage.removeItem('merchant_token');
          localStorage.removeItem('merchant_data');
          window.location.reload();
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // 處理空響應（如 204 No Content）
      if (response.status === 204 || response.headers.get('content-length') === '0') {
        return null as T | null;
      }
      
      // 檢查響應內容類型
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json() as T;
      } else {
        // 對於非 JSON 響應，返回 null 而不是 string
        return null as T | null;
      }
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // 商家認證 API
  async merchantEmailLogin(email: string, password: string) {
    return this.request('/api/v1/merchant-auth/email-login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async getMerchantProfile() {
    return this.request('/api/v1/merchant-auth/profile');
  }

  // 預約管理 API
  async getAppointments(merchantId: string, startDate?: string, endDate?: string) {
    const today = new Date().toISOString().split('T')[0];
    const defaultEndDate = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    const params = new URLSearchParams({
      merchant_id: merchantId,
      start_date: startDate || today,
      end_date: endDate || defaultEndDate
    });
    return this.request(`/api/v1/appointments?${params}`);
  }

  async createAppointment(appointmentData: any) {
    return this.request('/api/v1/appointments', {
      method: 'POST',
      body: JSON.stringify(appointmentData),
    });
  }

  async updateAppointment(appointmentId: string, appointmentData: any) {
    return this.request(`/api/v1/appointments/${appointmentId}`, {
      method: 'PUT',
      body: JSON.stringify(appointmentData),
    });
  }

  async deleteAppointment(appointmentId: string) {
    return this.request(`/api/v1/appointments/${appointmentId}`, {
      method: 'DELETE',
    });
  }

  // 服務管理 API
  async getServices(merchantId: string) {
    return this.request(`/api/v1/services?merchant_id=${merchantId}`);
  }

  async createService(serviceData: any) {
    return this.request('/api/v1/services', {
      method: 'POST',
      body: JSON.stringify(serviceData),
    });
  }

  async updateService(serviceId: string, serviceData: any) {
    return this.request(`/api/v1/services/${serviceId}`, {
      method: 'PUT',
      body: JSON.stringify(serviceData),
    });
  }

  async deleteService(serviceId: string) {
    return this.request(`/api/v1/services/${serviceId}`, {
      method: 'DELETE',
    });
  }

  // 顧客管理 API
  async getCustomers(merchantId: string) {
    return this.request(`/api/v1/users?merchant_id=${merchantId}`);
  }

  async getCustomer(customerId: string) {
    return this.request(`/api/v1/users/${customerId}`);
  }

  // 營業時間管理 API
  async getBusinessHours(merchantId: string) {
    return this.request(`/api/v1/business-hours?merchant_id=${merchantId}`);
  }

  async updateBusinessHours(merchantId: string, businessHours: any) {
    return this.request(`/api/v1/business-hours?merchant_id=${merchantId}`, {
      method: 'PUT',
      body: JSON.stringify(businessHours),
    });
  }

  // 休假管理 API
  async getTimeOffs(merchantId: string) {
    return this.request(`/api/v1/time-offs?merchant_id=${merchantId}`);
  }

  async createTimeOff(timeOffData: any) {
    return this.request('/api/v1/time-offs', {
      method: 'POST',
      body: JSON.stringify(timeOffData),
    });
  }

  async deleteTimeOff(timeOffId: string) {
    return this.request(`/api/v1/time-offs/${timeOffId}`, {
      method: 'DELETE',
    });
  }

  // 儀表板 API
  async getDashboardData(merchantId: string) {
    return this.request(`/api/v1/dashboard/summary`);
  }

  // 交易記錄 API
  async getTransactions(merchantId: string) {
    return this.request(`/api/v1/transactions?merchant_id=${merchantId}`);
  }

  async createTransaction(transactionData: any) {
    return this.request('/api/v1/transactions', {
      method: 'POST',
      body: JSON.stringify(transactionData),
    });
  }
}

export const apiService = new ApiService();
export default apiService;

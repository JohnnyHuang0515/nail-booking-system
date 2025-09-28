const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
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
      
      return await response.json();
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
  async getAppointments(merchantId: string) {
    return this.request(`/api/v1/appointments?merchant_id=${merchantId}`);
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
    return this.request(`/api/v1/dashboard?merchant_id=${merchantId}`);
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

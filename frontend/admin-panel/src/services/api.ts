const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface Appointment {
  id: string;
  merchant_id: string;
  user_id?: string;
  service_id: string;
  appointment_date: string;
  appointment_time: string;
  status: string;
  customer_name?: string;
  customer_phone?: string;
  customer_email?: string;
  notes?: string;
  created_at: string;
  service?: {
    id: string;
    name: string;
    price: number;
    duration_minutes: number;
  };
}

interface CalendarAppointment {
  id: string;
  time: string;
  service: string;
  customer: string;
  status: string;
  customer_phone?: string;
  notes?: string;
  appointment_date?: string;
}

class AdminApiService {
  private baseURL: string;
  private merchantId: string | null = null;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  setMerchantId(merchantId: string): void {
    this.merchantId = merchantId;
  }

  getMerchantId(): string {
    if (!this.merchantId) {
      // 使用預設的商家 ID
      const defaultMerchantId = '930d5cde-2e01-456a-915c-92c234b613bc';
      this.merchantId = defaultMerchantId;
      console.log('使用預設商家 ID:', defaultMerchantId);
      return defaultMerchantId;
    }
    return this.merchantId;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
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
        
        // 嘗試從響應中取得錯誤詳情
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        } catch (e) {
          // 無法解析 JSON 錯誤訊息，使用預設訊息
        }
        
        throw new Error(errorMessage);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // 獲取指定日期範圍的預約（原始格式）
  async getAppointments(startDate?: string, endDate?: string): Promise<Appointment[]> {
    const merchantId = this.getMerchantId();
    
    // 如果沒有提供日期範圍，使用當前月份
    let url = `/api/v1/appointments?merchant_id=${merchantId}`;
    if (startDate && endDate) {
      url += `&start_date=${startDate}&end_date=${endDate}`;
    } else {
      // 使用當前月份作為預設範圍
      const now = new Date();
      const start = new Date(now.getFullYear(), now.getMonth(), 1);
      const end = new Date(now.getFullYear(), now.getMonth() + 1, 0);
      url += `&start_date=${start.toISOString().split('T')[0]}&end_date=${end.toISOString().split('T')[0]}`;
    }
    
    const response = await this.request<Appointment[]>(url);
    return response;
  }

  // 獲取指定日期範圍的預約（行事曆格式）
  async getCalendarAppointments(startDate?: string, endDate?: string): Promise<CalendarAppointment[]> {
    const merchantId = this.getMerchantId();
    
    // 如果沒有提供日期範圍，使用當前月份
    let url = `/api/v1/appointments?merchant_id=${merchantId}`;
    if (startDate && endDate) {
      url += `&start_date=${startDate}&end_date=${endDate}`;
    } else {
      // 使用當前月份作為預設範圍
      const now = new Date();
      const start = new Date(now.getFullYear(), now.getMonth(), 1);
      const end = new Date(now.getFullYear(), now.getMonth() + 1, 0);
      url += `&start_date=${start.toISOString().split('T')[0]}&end_date=${end.toISOString().split('T')[0]}`;
    }
    
    const response = await this.request<Appointment[]>(url);
    
    // 轉換為行事曆格式
    const result = response.map(apt => ({
      id: apt.id,
      time: apt.appointment_time.substring(0, 5), // 只取 HH:MM
      service: apt.service?.name || '未知服務',
      customer: apt.customer_name || '未知顧客',
      status: apt.status,
      customer_phone: apt.customer_phone,
      notes: apt.notes,
      appointment_date: apt.appointment_date // 保留日期用於分組
    }));
    
    return result;
  }

  // 預約管理 API
  async getAppointments(startDate?: string, endDate?: string) {
    const today = new Date().toISOString().split('T')[0];
    const defaultEndDate = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    const merchantId = '00000000-0000-0000-0000-000000000001'; // 測試商家 ID
    const params = new URLSearchParams({
      merchant_id: merchantId,
      start_date: startDate || today,
      end_date: endDate || defaultEndDate
    });
    return this.request(`/api/v1/appointments?${params}`);
  }

  // 創建預約
  async createAppointment(appointmentData: any): Promise<any> {
    const merchantId = this.getMerchantId();
    return await this.request(`/api/v1/bookings?merchant_id=${merchantId}`, {
      method: 'POST',
      body: JSON.stringify(appointmentData),
    });
  }

  // 更新預約
  async updateAppointment(appointmentId: string, appointmentData: any): Promise<any> {
    const merchantId = this.getMerchantId();
    return await this.request(`/api/v1/appointments/${appointmentId}?merchant_id=${merchantId}`, {
      method: 'PUT',
      body: JSON.stringify(appointmentData),
    });
  }

  // 刪除預約
  async deleteAppointment(appointmentId: string): Promise<any> {
    const merchantId = this.getMerchantId();
    return await this.request(`/api/v1/appointments/${appointmentId}?merchant_id=${merchantId}`, {
      method: 'DELETE',
    });
  }

  // 服務管理 API
  async getServices() {
    const merchantId = '00000000-0000-0000-0000-000000000001'; // 測試商家 ID
    return this.request(`/api/v1/services?merchant_id=${merchantId}`);
  }

  async createService(serviceData: any) {
    return this.request('/api/v1/services', {
      method: 'POST',
      body: JSON.stringify(serviceData),
    });
  }

  // 更新服務
  async updateService(serviceId: string, serviceData: any): Promise<any> {
    const merchantId = this.getMerchantId();
    return await this.request(`/api/v1/services/${serviceId}?merchant_id=${merchantId}`, {
      method: 'PUT',
      body: JSON.stringify(serviceData),
    });
  }

  // 刪除服務
  async deleteService(serviceId: string): Promise<any> {
    const merchantId = this.getMerchantId();
    return await this.request(`/api/v1/services/${serviceId}?merchant_id=${merchantId}`, {
      method: 'DELETE',
    });
  }
}

export const adminApiService = new AdminApiService();
export default adminApiService;
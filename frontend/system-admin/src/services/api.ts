const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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
  private authToken: string | null = null;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  setMerchantId(merchantId: string): void {
    this.merchantId = merchantId;
  }

  setAuthToken(token: string): void {
    this.authToken = token;
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

  private getAuthToken(): string | null {
    return localStorage.getItem('merchant_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const token = this.getAuthToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config: RequestInit = {
      ...options,
      headers,
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
  async getAppointments(startDate?: string, endDate?: string): Promise<any[]> {
    // 使用新的 /merchant/bookings 端點
    const bookings = await this.getBookings(startDate, endDate);
    
    // 轉換為前端期望的格式
    return bookings.map(booking => ({
      id: booking.id,
      merchant_id: booking.merchant_id,
      user_id: booking.customer?.line_user_id,
      service_id: booking.items[0]?.service_id || null,
      appointment_date: booking.start_at.split('T')[0], // "2025-10-15"
      appointment_time: booking.start_at.split('T')[1].substring(0, 5), // "12:00"
      status: booking.status,
      customer_name: booking.customer?.name || '未知客戶',
      customer_phone: booking.customer?.phone || '',
      customer_email: booking.customer?.email || '',
      notes: booking.notes || '',
      created_at: booking.created_at,
      service: booking.items[0] ? {
        id: booking.items[0].service_id,
        name: booking.items[0].service_name,
        price: booking.items[0].service_price,
        duration_minutes: booking.items[0].service_duration
      } : null
    }));
  }

  // 獲取指定日期範圍的預約（行事曆格式）
  async getCalendarAppointments(startDate?: string, endDate?: string): Promise<CalendarAppointment[]> {
    // 使用新的 /merchant/bookings 端點
    const bookings = await this.getBookings(startDate, endDate);
    
    // 轉換為行事曆格式
    return bookings.map(booking => ({
      id: booking.id,
      time: booking.start_at.split('T')[1].substring(0, 5), // "12:00"
      service: booking.items.map((item: any) => item.service_name).join(', '),
      customer: booking.customer?.name || '未知顧客',
      status: booking.status,
      customer_phone: booking.customer?.phone,
      notes: booking.notes,
      appointment_date: booking.start_at.split('T')[0], // "2025-10-15"
      staff_id: booking.staff_id  // 美甲師ID
    }));
  }

  // 預約管理 API
  async getBookings(startDate?: string, endDate?: string, staffId?: number, status?: string): Promise<any[]> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (staffId) params.append('staff_id', staffId.toString());
    if (status) params.append('status', status);
    
    const query = params.toString();
    return this.request<any[]>(`/merchant/bookings${query ? '?' + query : ''}`);
  }

  // 創建預約（暫時使用LIFF端點）
  async createAppointment(appointmentData: any): Promise<any> {
    // 轉換為後端期望的格式
    const bookingRequest = {
      merchant_id: this.getMerchantId(),
      customer: {
        name: appointmentData.customer_name,
        phone: appointmentData.customer_phone,
        email: appointmentData.customer_email || undefined
      },
      staff_id: appointmentData.staff_id || 1,
      start_at: `${appointmentData.appointment_date}T${appointmentData.appointment_time}:00+08:00`,
      items: [{
        service_id: parseInt(appointmentData.service_id),
        option_ids: []
      }],
      notes: appointmentData.notes || undefined
    };
    
    return await this.request('/liff/bookings', {
      method: 'POST',
      body: JSON.stringify(bookingRequest),
    });
  }

  // 更新預約
  async updateAppointment(appointmentId: string, appointmentData: any): Promise<any> {
    return this.request(`/merchant/bookings/${appointmentId}`, {
      method: 'PUT',
      body: JSON.stringify(appointmentData),
    });
  }

  // 刪除預約
  async deleteAppointment(appointmentId: string): Promise<void> {
    await this.request(`/merchant/bookings/${appointmentId}`, {
      method: 'DELETE',
    });
  }

  // Business Hours API
  async getBusinessHours(): Promise<any> {
    return this.request('/merchant/business-hours');
  }

  async updateBusinessHours(businessHours: {
    monday: boolean;
    tuesday: boolean;
    wednesday: boolean;
    thursday: boolean;
    friday: boolean;
    saturday: boolean;
    sunday: boolean;
  }): Promise<any> {
    return this.request('/merchant/business-hours', {
      method: 'PUT',
      body: JSON.stringify(businessHours),
    });
  }

  // 服務管理 API
  async getServices() {
    const services = await this.request<any[]>('/merchant/services');
    
    // 轉換為前端期望的格式
    return services.map(service => ({
      id: service.id.toString(),
      merchant_id: service.merchant_id,
      name: service.name,
      price: service.base_price,  // base_price → price
      duration_minutes: service.duration_minutes,
      is_active: service.is_active,
      description: service.description || '',
      category: service.category || '',
      image: null
    }));
  }

  async createService(serviceData: any) {
    return this.request('/merchant/services', {
      method: 'POST',
      body: JSON.stringify(serviceData),
    });
  }

  // 更新服務
  async updateService(serviceId: string, serviceData: any): Promise<any> {
    return await this.request(`/merchant/services/${serviceId}`, {
      method: 'PUT',
      body: JSON.stringify(serviceData),
    });
  }

  // 刪除服務
  async deleteService(serviceId: string): Promise<any> {
    return await this.request(`/merchant/services/${serviceId}`, {
      method: 'DELETE',
    });
  }
  
  // 員工管理 API
  async getStaff(): Promise<any[]> {
    return this.request<any[]>('/merchant/staff');
  }

  async createStaff(staffData: {
    name: string;
    email?: string;
    phone?: string;
    skills?: number[];
    is_active?: boolean;
  }): Promise<any> {
    return this.request('/merchant/staff', {
      method: 'POST',
      body: JSON.stringify(staffData),
    });
  }

  async updateStaff(staffId: number, staffData: {
    name?: string;
    email?: string;
    phone?: string;
    skills?: number[];
    is_active?: boolean;
  }): Promise<any> {
    return this.request(`/merchant/staff/${staffId}`, {
      method: 'PUT',
      body: JSON.stringify(staffData),
    });
  }

  async deleteStaff(staffId: number): Promise<void> {
    await this.request(`/merchant/staff/${staffId}`, {
      method: 'DELETE',
    });
  }

  // Staff Holiday API
  async getStaffHolidays(startDate?: string, endDate?: string): Promise<any[]> {
    let url = '/merchant/staff-holidays';
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (params.toString()) url += `?${params.toString()}`;
    
    return this.request<any[]>(url);
  }

  async createStaffHoliday(holidayData: {
    staff_id: number;
    holiday_date: string;
    name: string;
    is_recurring?: boolean;
  }): Promise<any> {
    return this.request('/merchant/staff-holidays', {
      method: 'POST',
      body: JSON.stringify(holidayData),
    });
  }

  async updateStaffHoliday(holidayId: number, holidayData: {
    holiday_date?: string;
    name?: string;
    is_recurring?: boolean;
  }): Promise<any> {
    return this.request(`/merchant/staff-holidays/${holidayId}`, {
      method: 'PUT',
      body: JSON.stringify(holidayData),
    });
  }

  async deleteStaffHoliday(holidayId: number): Promise<void> {
    await this.request(`/merchant/staff-holidays/${holidayId}`, {
      method: 'DELETE',
    });
  }

  // ========== Billing API ==========

  async getPlans(): Promise<any[]> {
    return this.request<any[]>('/billing/plans');
  }

  async getPlan(planId: number): Promise<any> {
    return this.request<any>(`/billing/plans/${planId}`);
  }

  async getSubscriptionStatus(): Promise<any> {
    if (!this.merchantId) {
      throw new Error('Merchant ID not set');
    }
    return this.request<any>(`/billing/merchants/${this.merchantId}/subscription/status`);
  }

  async getSubscription(): Promise<any> {
    if (!this.merchantId) {
      throw new Error('Merchant ID not set');
    }
    return this.request<any>(`/billing/merchants/${this.merchantId}/subscription`);
  }

  async createSubscription(planId: number, trialDays: number = 14): Promise<any> {
    if (!this.merchantId) {
      throw new Error('Merchant ID not set');
    }
    return this.request<any>('/billing/subscriptions', {
      method: 'POST',
      body: JSON.stringify({
        merchant_id: this.merchantId,
        plan_id: planId,
        trial_days: trialDays
      })
    });
  }

  async activateSubscription(subscriptionId: string): Promise<any> {
    return this.request<any>(`/billing/subscriptions/${subscriptionId}/activate`, {
      method: 'POST'
    });
  }

  async cancelSubscription(subscriptionId: string): Promise<any> {
    return this.request<any>(`/billing/subscriptions/${subscriptionId}/cancel`, {
      method: 'POST'
    });
  }

  // ========== Auth API ==========

  async login(email: string, password: string): Promise<any> {
    return this.request<any>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  }

  async register(userData: {
    email: string;
    password: string;
    name: string;
    merchant_id?: string;
  }): Promise<any> {
    return this.request<any>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  }

  async getCurrentUser(): Promise<any> {
    return this.request<any>('/auth/me');
  }

  // ========== Notification API ==========

  async getNotificationTemplates(): Promise<any[]> {
    return this.request<any[]>('/notifications/templates');
  }

  async sendNotification(request: {
    recipient: string;
    notification_type: string;
    variables: Record<string, any>;
  }): Promise<any> {
    if (!this.merchantId) {
      throw new Error('Merchant ID not set');
    }
    return this.request<any>('/notifications/send', {
      method: 'POST',
      body: JSON.stringify({
        merchant_id: this.merchantId,
        ...request
      })
    });
  }

  async testNotification(recipient: string, message: string): Promise<any> {
    if (!this.merchantId) {
      throw new Error('Merchant ID not set');
    }
    return this.request<any>('/notifications/test', {
      method: 'POST',
      body: JSON.stringify({
        merchant_id: this.merchantId,
        recipient,
        message
      })
    });
  }
}

export const adminApiService = new AdminApiService();
export default adminApiService;
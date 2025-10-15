const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// === 後端 DTO 類型定義 ===

interface MerchantInfo {
  id: string;
  slug: string;
  name: string;
  business_hours: string;
  timezone: string;
  liff_id?: string;
}

interface TimeSlot {
  start_time: string;  // ISO datetime
  end_time: string;    // ISO datetime
  available: boolean;
  staff_id: number;
}

interface Service {
  id: number;
  merchant_id: string;
  name: string;
  description: string;
  base_price: number;
  duration_minutes: number;
  is_active: boolean;
  category?: string;
}

interface Staff {
  id: number;
  merchant_id: string;
  name: string;
  email?: string;
  phone?: string;
  is_active: boolean;
  skills: number[];
}

interface BookingItem {
  service_id: number;
  option_ids: number[];
}

interface Customer {
  line_user_id?: string;
  name?: string;
  phone?: string;
  email?: string;
}

interface CreateBookingRequest {
  merchant_id: string;
  customer: Customer;
  staff_id: number;
  start_at: string;  // ISO datetime
  items: BookingItem[];
  notes?: string;
}

interface BookingResponse {
  id: string;
  merchant_id: string;
  customer: Customer;
  staff_id: number;
  start_at: string;
  end_at: string;
  status: string;
  total_price: number;
  notes?: string;
  created_at: string;
}

class CustomerApiService {
  private baseURL: string;
  private merchantSlug: string | null = null;
  private merchantId: string | null = null;
  private token: string | null = null;

  constructor() {
    this.baseURL = API_BASE_URL;
    this.loadToken();
  }

  // === Token 管理 ===

  private loadToken(): void {
    const stored = localStorage.getItem('liff_jwt_token');
    if (stored) {
      this.token = stored;
    }
  }

  setToken(token: string): void {
    this.token = token;
    localStorage.setItem('liff_jwt_token', token);
  }

  clearToken(): void {
    this.token = null;
    localStorage.removeItem('liff_jwt_token');
  }

  getToken(): string | null {
    return this.token;
  }

  // === 商家資訊管理 ===

  setMerchantSlug(slug: string): void {
    this.merchantSlug = slug;
    localStorage.setItem('merchant_slug', slug);
  }

  getMerchantSlug(): string {
    if (!this.merchantSlug) {
      const stored = localStorage.getItem('merchant_slug');
      if (stored) {
        this.merchantSlug = stored;
        return stored;
      }
      
      // 從 URL 參數獲取
      const urlParams = new URLSearchParams(window.location.search);
      const urlSlug = urlParams.get('merchant_slug');
      if (urlSlug) {
        this.merchantSlug = urlSlug;
        localStorage.setItem('merchant_slug', urlSlug);
        return urlSlug;
      }
      
      // 預設值（使用資料庫中實際的 slug）
      const defaultSlug = 'nail-abc';
      this.merchantSlug = defaultSlug;
      return defaultSlug;
    }
    return this.merchantSlug;
  }

  setMerchantId(merchantId: string): void {
    this.merchantId = merchantId;
  }

  getMerchantId(): string {
    if (!this.merchantId) {
      const defaultMerchantId = '00000000-0000-0000-0000-000000000001';
      this.merchantId = defaultMerchantId;
      return defaultMerchantId;
    }
    return this.merchantId;
  }

  // === HTTP 請求方法 ===

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    requiresAuth: boolean = false
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    // 添加認證 Token
    if (requiresAuth && this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const config: RequestInit = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        if (response.status === 401 && requiresAuth) {
          // Token 無效，清除並提示重新登入
          this.clearToken();
          throw new Error('認證失效，請重新登入');
        }
        
        // 嘗試解析錯誤訊息
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            // 簡化時段衝突的錯誤訊息
            if (errorData.detail.includes('時段衝突') || errorData.detail.includes('已有預約')) {
              errorMessage = '該時段員工已經有預約';
            } else {
              errorMessage = errorData.detail;
            }
          }
        } catch (e) {
          // 無法解析 JSON
        }
        
        throw new Error(errorMessage);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // === 公開 API（無需認證）===

  async getMerchantInfo(slug?: string): Promise<MerchantInfo> {
    const merchantSlug = slug || this.getMerchantSlug();
    return this.request<MerchantInfo>(`/public/merchants/${merchantSlug}`);
  }

  async getAvailableTimeSlots(
    targetDate: string,
    staffId: number,
    serviceIds: number[] = []
  ): Promise<TimeSlot[]> {
    const slug = this.getMerchantSlug();
    const params = new URLSearchParams({
      target_date: targetDate,
      staff_id: staffId.toString(),
    });
    
    // 添加多個 service_ids
    serviceIds.forEach(id => params.append('service_ids', id.toString()));
    
    return this.request<TimeSlot[]>(
      `/public/merchants/${slug}/slots?${params.toString()}`
    );
  }

  async getServices(): Promise<Service[]> {
    const slug = this.getMerchantSlug();
    return this.request<Service[]>(`/public/merchants/${slug}/services`);
  }

  async getStaff(): Promise<Staff[]> {
    const slug = this.getMerchantSlug();
    return this.request<Staff[]>(`/public/merchants/${slug}/staff`);
  }

  async getHolidays(startDate?: string, endDate?: string): Promise<any[]> {
    const slug = this.getMerchantSlug();
    let url = `/public/merchants/${slug}/holidays`;
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (params.toString()) url += `?${params.toString()}`;
    
    return this.request<any[]>(url);
  }

  // === LIFF API（需要認證）===

  async createBooking(request: CreateBookingRequest): Promise<BookingResponse> {
    return this.request<BookingResponse>(
      '/liff/bookings',
      {
        method: 'POST',
        body: JSON.stringify(request),
      },
      true  // 需要認證
    );
  }

  async listBookings(merchantId: string): Promise<BookingResponse[]> {
    return this.request<BookingResponse[]>(
      `/liff/bookings?merchant_id=${merchantId}`,
      {},
      true  // 需要認證
    );
  }

  async getBooking(bookingId: string, merchantId: string): Promise<BookingResponse> {
    return this.request<BookingResponse>(
      `/liff/bookings/${bookingId}?merchant_id=${merchantId}`,
      {},
      true  // 需要認證
    );
  }

  async cancelBooking(
    bookingId: string,
    merchantId: string,
    requesterLineId: string,
    reason?: string
  ): Promise<void> {
    const params = new URLSearchParams({
      merchant_id: merchantId,
      requester_line_id: requesterLineId,
    });
    
    if (reason) {
      params.append('reason', reason);
    }
    
    return this.request<void>(
      `/liff/bookings/${bookingId}?${params.toString()}`,
      { method: 'DELETE' },
      true  // 需要認證
    );
  }

  // === 認證 API ===

  async registerLineUser(
    email: string,
    lineUserId: string,
    displayName?: string
  ): Promise<{ id: string; email: string; name: string }> {
    return this.request<{ id: string; email: string; name: string }>(
      '/auth/register',
      {
        method: 'POST',
        body: JSON.stringify({
          email,
          password: `line_${lineUserId}`,  // LINE 用戶使用特殊密碼
          name: displayName,
          merchant_id: this.getMerchantId(),
        }),
      }
    );
  }

  async loginLineUser(
    email: string,
    lineUserId: string
  ): Promise<{ access_token: string; token_type: string; user: any }> {
    return this.request<{ access_token: string; token_type: string; user: any }>(
      '/auth/login',
      {
        method: 'POST',
        body: JSON.stringify({
          email,
          password: `line_${lineUserId}`,
        }),
      }
    );
  }
}

export const customerApiService = new CustomerApiService();
export default customerApiService;

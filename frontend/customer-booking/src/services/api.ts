const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface TimeSlot {
  time: string;
  available: boolean;
  bookedBy?: string;
}

interface Service {
  id: string;
  merchant_id: string;
  name: string;
  price: number;
  duration_minutes: number;
  is_active: boolean;
  description?: string;
  category?: string;
}

interface BookingRequest {
  customer_name: string;
  customer_phone: string;
  customer_email?: string;
  service_id: string;
  appointment_date: string;
  appointment_time: string;
  notes?: string;
  // LINE 用戶資訊
  line_user_id?: string;
  line_display_name?: string;
  line_picture_url?: string;
}

class CustomerApiService {
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
      // 嘗試從 URL 參數獲取商家 ID
      const urlParams = new URLSearchParams(window.location.search);
      const urlMerchantId = urlParams.get('merchant_id');
      
      if (urlMerchantId) {
        this.merchantId = urlMerchantId;
        console.log('從 URL 參數獲取商家 ID:', urlMerchantId);
        return urlMerchantId;
      }
      
      // 如果都沒有，使用預設的測試商家 ID
      const defaultMerchantId = '5a89c20e-befd-4bb3-a43b-e185ab0e4841';
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
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // 取得可用時間段
  async getAvailableTimeSlots(date: string): Promise<TimeSlot[]> {
    const merchantId = this.getMerchantId();
    const response = await this.request<TimeSlot[]>(`/api/v1/slots/${date}?merchant_id=${merchantId}`);
    return response;
  }

  // 取得服務列表
  async getServices(): Promise<Service[]> {
    const merchantId = this.getMerchantId();
    const response = await this.request<Service[]>(`/api/v1/services?merchant_id=${merchantId}`);
    return response;
  }

  // 提交預約
  async submitBooking(bookingData: BookingRequest): Promise<any> {
    try {
      const merchantId = this.getMerchantId();
      const response = await this.request(`/api/v1/bookings?merchant_id=${merchantId}`, {
        method: 'POST',
        body: JSON.stringify(bookingData),
      });
      return response;
    } catch (error) {
      console.error('Failed to submit booking:', error);
      throw error;
    }
  }

}

export const customerApiService = new CustomerApiService();
export default customerApiService;

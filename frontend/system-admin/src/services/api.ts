/**
 * 系統管理員 API 服務
 */

interface SystemStats {
  total_merchants: number;
  active_merchants: number;
  total_bookings: number;
  total_revenue: number;
  subscription_stats: {
    active: number;
    past_due: number;
    canceled: number;
  };
}

interface MerchantSummary {
  id: string;
  name: string;
  email: string;
  slug: string;
  is_active: boolean;
  created_at: string;
  subscription_status?: string;
  total_bookings: number;
  total_revenue: number;
}

interface CreateMerchantRequest {
  name: string;
  email: string;
  slug: string;
  line_channel_id?: string;
  line_channel_secret?: string;
  liff_id?: string;
  timezone?: string;
}

interface UpdateMerchantRequest {
  name?: string;
  email?: string;
  slug?: string;
  line_channel_id?: string;
  line_channel_secret?: string;
  liff_id?: string;
  timezone?: string;
  is_active?: boolean;
}

class SystemAdminApiService {
  private baseURL: string;
  private authToken: string | null = null;

  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  }

  setAuthToken(token: string): void {
    this.authToken = token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // ========== 認證 API ==========
  async login(email: string, password: string): Promise<any> {
    const response = await fetch(`${this.baseURL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        username: email,
        password: password,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  }

  async getCurrentUser(): Promise<any> {
    return this.request('/api/v1/auth/me');
  }

  // ========== 系統統計 API ==========
  async getSystemStats(): Promise<SystemStats> {
    return this.request<SystemStats>('/api/v1/admin/stats');
  }

  // ========== 商家管理 API ==========
  async getMerchants(skip: number = 0, limit: number = 100, search?: string): Promise<MerchantSummary[]> {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    if (search) params.append('search', search);

    return this.request<MerchantSummary[]>(`/api/v1/admin/merchants?${params.toString()}`);
  }

  async getMerchant(merchantId: string): Promise<MerchantSummary> {
    return this.request<MerchantSummary>(`/api/v1/admin/merchants/${merchantId}`);
  }

  async createMerchant(data: CreateMerchantRequest): Promise<MerchantSummary> {
    return this.request<MerchantSummary>('/api/v1/admin/merchants', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateMerchant(merchantId: string, data: UpdateMerchantRequest): Promise<MerchantSummary> {
    return this.request<MerchantSummary>(`/api/v1/admin/merchants/${merchantId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteMerchant(merchantId: string): Promise<void> {
    return this.request<void>(`/api/v1/admin/merchants/${merchantId}`, {
      method: 'DELETE',
    });
  }

  // ========== 用戶管理 API ==========
  async getUsers(skip: number = 0, limit: number = 100, merchantId?: string): Promise<any[]> {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    if (merchantId) params.append('merchant_id', merchantId);

    return this.request<any[]>(`/api/v1/admin/users?${params.toString()}`);
  }

  // ========== 系統設定 API ==========
  async getSystemSettings(): Promise<any> {
    return this.request('/api/v1/admin/settings');
  }

  async updateSystemSettings(data: any): Promise<any> {
    return this.request('/api/v1/admin/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }
}

export const systemAdminApiService = new SystemAdminApiService();
export default systemAdminApiService;

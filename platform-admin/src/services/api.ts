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
    const token = localStorage.getItem('admin_token');
    
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
          localStorage.removeItem('admin_token');
          localStorage.removeItem('admin_data');
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

  // 平台管理員 API
  async adminLogin(username: string, password: string) {
    return this.request('/api/v1/admin/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async getAdminProfile() {
    return this.request('/api/v1/admin/profile');
  }

  // 商家管理 API
  async getMerchants() {
    return this.request('/api/v1/merchants');
  }

  async getMerchant(merchantId: string) {
    return this.request(`/api/v1/merchants/${merchantId}`);
  }

  async createMerchant(merchantData: any) {
    return this.request('/api/v1/merchants', {
      method: 'POST',
      body: JSON.stringify(merchantData),
    });
  }

  async updateMerchant(merchantId: string, merchantData: any) {
    return this.request(`/api/v1/merchants/${merchantId}`, {
      method: 'PUT',
      body: JSON.stringify(merchantData),
    });
  }

  async toggleMerchantStatus(merchantId: string, isActive: boolean) {
    return this.request(`/api/v1/merchants/${merchantId}/toggle-status`, {
      method: 'POST',
      body: JSON.stringify({ is_active: isActive }),
    });
  }

  // 商家設定 API
  async getMerchantBasicSettings(merchantId: string) {
    return this.request(`/api/v1/merchants/${merchantId}/settings/basic`);
  }

  async updateMerchantBasicSettings(merchantId: string, settings: any) {
    return this.request(`/api/v1/merchants/${merchantId}/settings/basic`, {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }

  // 監控 API
  async getMonitoringOverview() {
    return this.request('/api/v1/monitoring/overview');
  }

  async getMonitoringAlerts() {
    return this.request('/api/v1/monitoring/alerts');
  }

  async getMerchantWebhookHealth(merchantId: string) {
    return this.request(`/api/v1/merchants/${merchantId}/monitoring/webhook-health`);
  }

  async getMerchantPushQuota(merchantId: string) {
    return this.request(`/api/v1/merchants/${merchantId}/monitoring/push-quota`);
  }

  // 報表 API
  async getReportsDashboard() {
    return this.request('/api/v1/reports/dashboard');
  }

  async getMerchantBusinessMetrics(merchantId: string) {
    return this.request(`/api/v1/merchants/${merchantId}/reports/business-metrics`);
  }

  async getMerchantCustomerScale(merchantId: string) {
    return this.request(`/api/v1/merchants/${merchantId}/reports/customer-scale`);
  }

  // 審計 API
  async getAuditLogs(params?: any) {
    const queryString = params ? `?${new URLSearchParams(params).toString()}` : '';
    return this.request(`/api/v1/audit/logs${queryString}`);
  }

  async getAuditSummary() {
    return this.request('/api/v1/audit/summary');
  }

  async exportAuditLogs(params?: any) {
    const queryString = params ? `?${new URLSearchParams(params).toString()}` : '';
    return this.request(`/api/v1/audit/export${queryString}`);
  }

  // 工單 API
  async getTickets() {
    return this.request('/api/v1/tickets');
  }

  async getTicket(ticketId: string) {
    return this.request(`/api/v1/tickets/${ticketId}`);
  }

  async createTicket(ticketData: any) {
    return this.request('/api/v1/tickets', {
      method: 'POST',
      body: JSON.stringify(ticketData),
    });
  }

  async updateTicket(ticketId: string, ticketData: any) {
    return this.request(`/api/v1/tickets/${ticketId}`, {
      method: 'PUT',
      body: JSON.stringify(ticketData),
    });
  }

  async sendTicketMessage(ticketId: string, message: string) {
    return this.request(`/api/v1/tickets/${ticketId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content: message }),
    });
  }

  // 通知 API
  async getNotifications() {
    return this.request('/api/v1/notifications');
  }

  async markNotificationAsRead(notificationId: string) {
    return this.request(`/api/v1/notifications/${notificationId}/read`, {
      method: 'POST',
    });
  }

  // 回滾 API
  async rollbackMerchant(merchantId: string, operation: string) {
    return this.request(`/api/v1/rollback/merchant/${merchantId}`, {
      method: 'POST',
      body: JSON.stringify({ operation }),
    });
  }

  // 系統設定 API
  async getSystemConfig() {
    return this.request('/api/v1/admin/system-config');
  }

  async updateSystemConfig(config: any) {
    return this.request('/api/v1/admin/system-config', {
      method: 'PUT',
      body: JSON.stringify(config),
    });
  }
}

export const apiService = new ApiService();
export default apiService;

import { useState, useEffect } from 'react';
import apiService from '../services/api';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>(
  apiCall: () => Promise<T>,
  dependencies: any[] = []
): UseApiState<T> & { refetch: () => void } {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchData = async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      const data = await apiCall();
      setState({ data, loading: false, error: null });
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  useEffect(() => {
    fetchData();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  return {
    ...state,
    refetch: fetchData,
  };
}

// 特定 API hooks
export function useMerchants() {
  return useApi(() => apiService.getMerchants());
}

export function useMerchant(merchantId: string) {
  return useApi(() => apiService.getMerchant(merchantId), [merchantId]);
}

export function useMonitoringOverview() {
  return useApi(() => apiService.getMonitoringOverview());
}

export function useReportsDashboard() {
  return useApi(() => apiService.getReportsDashboard());
}

export function useAuditLogs(params?: any) {
  return useApi(() => apiService.getAuditLogs(params), [params]);
}

export function useTickets() {
  return useApi(() => apiService.getTickets());
}

export function useSystemConfig() {
  return useApi(() => apiService.getSystemConfig());
}

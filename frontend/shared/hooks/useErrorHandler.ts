import { useState, useCallback } from 'react';

interface ErrorState {
  error: string | null;
  isLoading: boolean;
}

interface UseErrorHandlerReturn {
  error: string | null;
  isLoading: boolean;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  handleError: (error: unknown, defaultMessage?: string) => void;
  clearError: () => void;
  executeWithErrorHandling: <T>(
    asyncFn: () => Promise<T>,
    defaultErrorMessage?: string
  ) => Promise<T | null>;
}

export function useErrorHandler(): UseErrorHandlerReturn {
  const [state, setState] = useState<ErrorState>({
    error: null,
    isLoading: false,
  });

  const setError = useCallback((error: string | null) => {
    setState(prev => ({ ...prev, error }));
  }, []);

  const setLoading = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoading: loading }));
  }, []);

  const handleError = useCallback((error: unknown, defaultMessage = '發生錯誤') => {
    let errorMessage = defaultMessage;
    
    if (error instanceof Error) {
      errorMessage = error.message;
    } else if (typeof error === 'string') {
      errorMessage = error;
    } else if (error && typeof error === 'object' && 'message' in error) {
      errorMessage = String((error as any).message);
    }
    
    setState(prev => ({ ...prev, error: errorMessage, isLoading: false }));
    console.error('Error handled:', error);
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const executeWithErrorHandling = useCallback(async <T>(
    asyncFn: () => Promise<T>,
    defaultErrorMessage = '操作失敗'
  ): Promise<T | null> => {
    try {
      setState(prev => ({ ...prev, error: null, isLoading: true }));
      const result = await asyncFn();
      setState(prev => ({ ...prev, isLoading: false }));
      return result;
    } catch (error) {
      handleError(error, defaultErrorMessage);
      return null;
    }
  }, [handleError]);

  return {
    error: state.error,
    isLoading: state.isLoading,
    setError,
    setLoading,
    handleError,
    clearError,
    executeWithErrorHandling,
  };
}

import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { BookingState, Service, User } from '../types';

// 預約流程的 Action 類型
type BookingAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_SELECTED_DATE'; payload: string | null }
  | { type: 'SET_SELECTED_TIME'; payload: string | null }
  | { type: 'SET_SELECTED_SERVICE'; payload: Service | null }
  | { type: 'RESET_BOOKING' }
  | { type: 'NEXT_STEP' }
  | { type: 'PREV_STEP' };

// 初始狀態
const initialState: BookingState = {
  selectedDate: null,
  selectedTime: null,
  selectedService: null,
  user: null,
  isLoading: false,
  error: null,
};

// Reducer
function bookingReducer(state: BookingState, action: BookingAction): BookingState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'SET_SELECTED_DATE':
      return { ...state, selectedDate: action.payload };
    case 'SET_SELECTED_TIME':
      return { ...state, selectedTime: action.payload };
    case 'SET_SELECTED_SERVICE':
      return { ...state, selectedService: action.payload };
    case 'RESET_BOOKING':
      return initialState;
    default:
      return state;
  }
}

// Context 類型
interface BookingContextType {
  state: BookingState;
  dispatch: React.Dispatch<BookingAction>;
}

// 創建 Context
const BookingContext = createContext<BookingContextType | undefined>(undefined);

// Provider 組件
interface BookingProviderProps {
  children: ReactNode;
}

export function BookingProvider({ children }: BookingProviderProps) {
  const [state, dispatch] = useReducer(bookingReducer, initialState);

  return (
    <BookingContext.Provider value={{ state, dispatch }}>
      {children}
    </BookingContext.Provider>
  );
}

// Hook
export function useBooking() {
  const context = useContext(BookingContext);
  if (context === undefined) {
    throw new Error('useBooking must be used within a BookingProvider');
  }
  return context;
}

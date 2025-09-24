// 用戶相關類型
export interface User {
  id: string;
  line_user_id: string;
  name: string | null;
  phone: string | null;
}

// 服務相關類型
export interface Service {
  id: string;
  name: string;
  price: number;
  duration_minutes: number;
  is_active: boolean;
}

// 預約相關類型
export interface Appointment {
  id: string;
  user_id: string;
  service_id: string;
  appointment_date: string;
  appointment_time: string;
  status: AppointmentStatus;
  user?: User;
  service?: Service;
}

export enum AppointmentStatus {
  BOOKED = "BOOKED",
  CONFIRMED = "CONFIRMED",
  COMPLETED = "COMPLETED",
  CANCELLED = "CANCELLED",
  NO_SHOW = "NO_SHOW"
}

// 可用時段類型
export interface AvailableSlot {
  time: string;
  available: boolean;
}

// LIFF 相關類型
export interface LiffProfile {
  userId: string;
  displayName: string;
  pictureUrl?: string;
  statusMessage?: string;
}

// 預約流程狀態
export interface BookingState {
  selectedDate: string | null;
  selectedTime: string | null;
  selectedService: Service | null;
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

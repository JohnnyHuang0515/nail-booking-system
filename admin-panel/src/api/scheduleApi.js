import axiosInstance from './axiosInstance';

// --- Business Hours ---
export const getBusinessHours = () => {
  return axiosInstance.get('/schedule/business_hours');
};

export const setBusinessHours = (hoursData) => {
  return axiosInstance.post('/schedule/business_hours', hoursData);
};

// --- Time Off ---
export const getTimeOff = (forDate) => {
  return axiosInstance.get(`/schedule/time_off?for_date=${forDate}`);
};

export const getAllTimeOff = () => {
  return axiosInstance.get('/schedule/time_off/all');
};

export const addTimeOff = (timeOffData) => {
  return axiosInstance.post('/schedule/time_off', timeOffData);
};

export const deleteTimeOff = (id) => {
  return axiosInstance.delete(`/schedule/time_off/${id}`);
};

import axiosInstance from './axiosInstance';

export const getServices = () => {
  return axiosInstance.get('/services');
};

export const createService = (serviceData) => {
  return axiosInstance.post('/services', serviceData);
};

export const updateService = (id, serviceData) => {
  return axiosInstance.put(`/services/${id}`, serviceData);
};

export const deleteService = (id) => {
  return axiosInstance.delete(`/services/${id}`);
};

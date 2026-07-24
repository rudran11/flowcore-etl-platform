import { apiClient as api } from './client';
import { Schedule } from '../types/schedule';

export const schedulesApi = {
  getSchedules: async (params?: { skip?: number; limit?: number }) => {
    const { data } = await api.get<Schedule[]>('/schedules', { params });
    return data;
  },

  getSchedule: async (id: string) => {
    const { data } = await api.get<Schedule>(`/schedules/${id}`);
    return data;
  },

  createSchedule: async (payload: Partial<Schedule>) => {
    const { data } = await api.post<Schedule>('/schedules', payload);
    return data;
  },

  updateSchedule: async (id: string, payload: Partial<Schedule>) => {
    const { data } = await api.put<Schedule>(`/schedules/${id}`, payload);
    return data;
  },

  deleteSchedule: async (id: string) => {
    const { data } = await api.delete(`/schedules/${id}`);
    return data;
  },

  pauseSchedule: async (id: string) => {
    const { data } = await api.post<Schedule>(`/schedules/${id}/pause`);
    return data;
  },

  resumeSchedule: async (id: string) => {
    const { data } = await api.post<Schedule>(`/schedules/${id}/resume`);
    return data;
  },

  triggerSchedule: async (id: string) => {
    const { data } = await api.post(`/schedules/${id}/trigger`);
    return data;
  }
};

import axios from 'axios';
import { Complaint, AdminStats, Department, User } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Attach JWT token to every request if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('civic_auth_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  // Auth
  login: async (email: string, password: string) => {
    const res = await apiClient.post('/auth/login', { email, password });
    return res.data;
  },
  register: async (name: string, email: string, password: string, role = 'CITIZEN') => {
    const res = await apiClient.post('/auth/register', { name, email, password, role });
    return res.data;
  },
  getMe: async (): Promise<User> => {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },

  // Complaints
  getComplaints: async (params?: { status?: string; category?: string; severity?: string }): Promise<Complaint[]> => {
    const res = await apiClient.get('/complaints', { params });
    return res.data;
  },
  getComplaintById: async (id: string): Promise<Complaint> => {
    const res = await apiClient.get(`/complaints/${id}`);
    return res.data;
  },
  createComplaint: async (formData: FormData) => {
    const res = await apiClient.post('/complaints', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },
  updateComplaint: async (id: string, updateData: { status?: string; comment?: string; department?: string; priority_score?: number }) => {
    const res = await apiClient.patch(`/complaints/${id}`, updateData);
    return res.data;
  },

  // ML Direct
  analyzeText: async (text: string) => {
    const res = await apiClient.post('/ml/analyze-text', { text });
    return res.data;
  },
  calculatePriority: async (factors: any) => {
    const res = await apiClient.post('/priority/calculate', factors);
    return res.data;
  },

  // Admin
  getAdminDashboard: async (): Promise<AdminStats> => {
    const res = await apiClient.get('/admin/dashboard');
    return res.data;
  },
  getAllUsers: async (): Promise<User[]> => {
    const res = await apiClient.get('/admin/users');
    return res.data;
  },
  getDepartments: async (): Promise<Department[]> => {
    const res = await apiClient.get('/admin/departments');
    return res.data;
  },

  // Officer
  getOfficerComplaints: async (): Promise<Complaint[]> => {
    const res = await apiClient.get('/officer/complaints');
    return res.data;
  },
  updateOfficerStatus: async (id: string, status: string, comment?: string): Promise<Complaint> => {
    const res = await apiClient.patch(`/officer/complaints/${id}/status`, { status, comment });
    return res.data;
  }
};

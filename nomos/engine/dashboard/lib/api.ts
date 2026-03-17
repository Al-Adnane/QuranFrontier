import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API Endpoints
export const api = {
  // Verses
  getVerses: (limit = 10, offset = 0) =>
    apiClient.get('/api/verses', { params: { limit, offset } }),
  getVerse: (verseId: string) => apiClient.get(`/api/verses/${verseId}`),
  searchVerses: (query: string) =>
    apiClient.get('/api/verses/search', { params: { q: query } }),

  // Tafsirs
  getTafsirs: (verseId: string) =>
    apiClient.get(`/api/verses/${verseId}/tafsirs`),
  getTafsir: (tafsirId: string) =>
    apiClient.get(`/api/tafsirs/${tafsirId}`),
  getTafsirComparison: (tafsirIds: string[]) =>
    apiClient.post('/api/tafsirs/compare', { ids: tafsirIds }),

  // Hadiths
  getHadiths: (limit = 10, offset = 0) =>
    apiClient.get('/api/hadiths', { params: { limit, offset } }),
  getHadith: (hadithId: string) =>
    apiClient.get(`/api/hadiths/${hadithId}`),
  searchHadiths: (query: string) =>
    apiClient.get('/api/hadiths/search', { params: { q: query } }),

  // Corrections
  getCorrections: (status?: string) =>
    apiClient.get('/api/corrections', { params: { status } }),
  getCorrection: (correctionId: string) =>
    apiClient.get(`/api/corrections/${correctionId}`),
  submitCorrection: (data: any) =>
    apiClient.post('/api/corrections', data),
  approveCorrection: (correctionId: string, comment?: string) =>
    apiClient.post(`/api/corrections/${correctionId}/approve`, { comment }),
  rejectCorrection: (correctionId: string, reason: string) =>
    apiClient.post(`/api/corrections/${correctionId}/reject`, { reason }),

  // Conflicts
  getConflicts: () => apiClient.get('/api/conflicts'),
  getConflict: (conflictId: string) =>
    apiClient.get(`/api/conflicts/${conflictId}`),
  resolveConflict: (conflictId: string, resolution: string) =>
    apiClient.post(`/api/conflicts/${conflictId}/resolve`, { resolution }),

  // Audit Log
  getAuditLog: (limit = 50, offset = 0, filters?: any) =>
    apiClient.get('/api/audit', { params: { limit, offset, ...filters } }),
  searchAuditLog: (query: string) =>
    apiClient.get('/api/audit/search', { params: { q: query } }),

  // Analytics
  getAnalytics: (timeframe = 'week') =>
    apiClient.get('/api/analytics', { params: { timeframe } }),
  getUsageStats: () => apiClient.get('/api/analytics/usage'),
  getErrorMetrics: () => apiClient.get('/api/analytics/errors'),
  getPerformanceMetrics: () =>
    apiClient.get('/api/analytics/performance'),

  // Authentication
  login: (email: string, password: string) =>
    apiClient.post('/api/auth/login', { email, password }),
  logout: () => apiClient.post('/api/auth/logout'),
  getMe: () => apiClient.get('/api/auth/me'),

  // Users
  getUsers: (role?: string) =>
    apiClient.get('/api/users', { params: { role } }),
  getUser: (userId: string) => apiClient.get(`/api/users/${userId}`),
  updateUserRole: (userId: string, role: string) =>
    apiClient.patch(`/api/users/${userId}`, { role }),

  // Scholar Board
  getScholarBoard: () => apiClient.get('/api/board/members'),
  addBoardMember: (data: any) =>
    apiClient.post('/api/board/members', data),
  removeBoardMember: (memberId: string) =>
    apiClient.delete(`/api/board/members/${memberId}`),
};

export default apiClient;

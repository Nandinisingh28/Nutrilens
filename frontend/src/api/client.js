import axios from 'axios';

// API Base URL - use environment variable or fallback
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('nutrilens_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('nutrilens_token');
            localStorage.removeItem('nutrilens_user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    signup: (data) => api.post('/auth/signup', data),
    login: (data) => api.post('/auth/login', data),
    logout: () => api.post('/auth/logout'),
    me: () => api.get('/auth/me'),
};

// Users API
export const usersAPI = {
    getProfile: () => api.get('/users/me'),
    updateProfile: (data) => api.put('/users/me', data),
};

// Scans API
export const scansAPI = {
    precisionScan: (formData) => api.post('/scans/precision', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    }),
    quickScan: (formData) => api.post('/scans/quick', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    }),
    getHistory: () => api.get('/scans/history'),
    getScan: (id) => api.get(`/scans/${id}`),
};

export default api;

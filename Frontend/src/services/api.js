import axios from 'axios';
import { authService } from './authService';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token to every request automatically
api.interceptors.request.use((config) => {
  const token = authService.getToken();
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// On 401 response, clear auth and redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authService.logout();
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

export const chatAPI = {
  // Send message and get AI response
  sendMessage: async (messages, uploadedMaterials = []) => {
    try {
      const response = await api.post('/api/chat', {
        messages: messages.map(msg => ({
          role: msg.sender === 'user' ? 'user' : 'assistant',
          content: msg.text
        })),
        uploaded_materials: uploadedMaterials
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get response');
    }
  },

  // Upload files
  uploadFiles: async (files) => {
    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      const response = await api.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to upload files');
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await api.get('/api/health');
      return response.data;
    } catch (error) {
      throw new Error('Backend is not responding');
    }
  },

  // Test API
  testAPI: async () => {
    try {
      const response = await api.get('/api/test');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'API test failed');
    }
  }
};

export default api;
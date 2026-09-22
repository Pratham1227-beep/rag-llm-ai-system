import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
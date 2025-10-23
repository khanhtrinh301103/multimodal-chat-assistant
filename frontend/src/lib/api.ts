// frontend/src/lib/api.ts
import axios from 'axios';
import { supabase } from './supabase';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add Supabase JWT token to all requests
apiClient.interceptors.request.use(
  async (config) => {
    // Get token from Supabase session
    const { data: { session } } = await supabase.auth.getSession();
    const token = session?.access_token;
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Chat API with conversation memory
export async function sendChatMessage(message: string, conversationId: string | null = null) {
  const response = await apiClient.post('/chat/', {
    message,
    conversation_id: conversationId
  });
  return response.data;
}

export async function getChatHistory(conversationId: string) {
  const response = await apiClient.get(`/chat/history/${conversationId}`);
  return response.data;
}

// Image API
export async function sendImageQuestion(imageUrl: string, question: string) {
  const response = await apiClient.post('/image/', { imageUrl, question });
  return response.data;
}

// CSV API
export async function analyzeCsvFromUrl(csvUrl: string, prompt: string) {
  const response = await apiClient.post('/csv/url', { csvUrl, prompt });
  return response.data;
}

export async function analyzeCsvFromFile(file: File, prompt: string) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('prompt', prompt);

  const response = await apiClient.post('/csv/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}

// Auth API
export async function getCurrentUser() {
  const response = await apiClient.get('/auth/me');
  return response.data;
}

export { apiClient };
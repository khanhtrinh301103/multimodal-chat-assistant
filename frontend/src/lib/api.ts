import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

// Create axios instance with interceptors
const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    // TODO: Replace with real token from Supabase/Firebase
    const token = localStorage.getItem('auth_token') || 'demo-token-12345';
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Chat API
export async function sendChatMessage(message: string) {
  const response = await apiClient.post('/chat/', { message });
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
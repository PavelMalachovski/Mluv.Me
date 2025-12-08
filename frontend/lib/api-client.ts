/**
 * API Client for communicating with backend
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { useAuthStore } from './auth-store';

// API Base URL - use relative URL to work in both browser and Telegram Web App
// Backend serves frontend via proxy on the same domain
const API_BASE_URL = typeof window !== 'undefined' ? window.location.origin : '';

class APIClient {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = useAuthStore.getState().token;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Unauthorized - logout user
          useAuthStore.getState().logout();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Generic HTTP methods
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }

  // Health check
  async health() {
    const response = await this.client.get('/health');
    return response.data;
  }

  // User endpoints
  async getUserByTelegramId(telegramId: number) {
    const response = await this.client.get(`/api/v1/users/telegram/${telegramId}`);
    return response.data;
  }

  async createUser(userData: {
    telegram_id: number;
    username?: string;
    first_name: string;
    last_name?: string;
    ui_language: 'ru' | 'uk';
    level: 'beginner' | 'intermediate' | 'advanced' | 'native';
  }) {
    const response = await this.client.post('/api/v1/users', userData);
    return response.data;
  }

  async updateUser(userId: number, updates: any) {
    const response = await this.client.patch(`/api/v1/users/${userId}`, updates);
    return response.data;
  }

  // Stats endpoints
  async getStats(telegramId: number) {
    const response = await this.client.get(`/api/v1/stats/${telegramId}/summary`);
    return response.data;
  }

  async getStreak(userId: number) {
    const response = await this.client.get(`/api/v1/stats/streak`, {
      params: { user_id: userId },
    });
    return response.data;
  }

  async getDailyStats(userId: number, from?: string, to?: string) {
    const response = await this.client.get(`/api/v1/stats/daily`, {
      params: { user_id: userId, from, to },
    });
    return response.data;
  }

  // Lessons endpoints
  async processVoice(userId: number, audioBlob: Blob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.ogg');
    formData.append('user_id', userId.toString());

    const response = await this.client.post('/api/v1/lessons/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for voice processing
    });
    return response.data;
  }

  async getRecentLessons(userId: number, limit: number = 10) {
    const response = await this.client.get(`/api/v1/lessons`, {
      params: { user_id: userId, limit },
    });
    return response.data;
  }

  // Words endpoints
  async getSavedWords(telegramId: number) {
    const response = await this.client.get(`/api/v1/words/${telegramId}`);
    return response.data;
  }

  async saveWord(userId: number, wordData: {
    word_czech: string;
    translation: string;
    context_sentence?: string;
    phonetics?: string;
  }) {
    const response = await this.client.post('/api/v1/words', {
      user_id: userId,
      ...wordData,
    });
    return response.data;
  }

  async deleteWord(wordId: number) {
    const response = await this.client.delete(`/api/v1/words/${wordId}`);
    return response.data;
  }

  // Translation endpoint
  async translateWord(word: string, targetLanguage: "ru" | "uk" = "ru") {
    const response = await this.client.post('/api/v1/words/translate', {
      word,
      target_language: targetLanguage,
    });
    return response.data;
  }

  // Web auth endpoints (for Telegram Login Widget)
  async authenticateWithTelegram(telegramData: any) {
    const response = await this.client.post('/api/v1/web/auth/telegram', telegramData);
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new APIClient();

// Export for custom instances
export default APIClient;

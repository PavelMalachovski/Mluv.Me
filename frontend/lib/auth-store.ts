/**
 * Authentication state management using Zustand
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface User {
  id: number;
  telegram_id: number;
  username?: string;
  first_name: string;
  last_name?: string;
  native_language: 'ru' | 'uk';
  level: 'beginner' | 'intermediate' | 'advanced' | 'native';
  created_at: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;

  // Actions
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      setUser: (user) => set({ user, isAuthenticated: true }),

      setToken: (token) => set({ token }),

      login: (user, token) => set({
        user,
        token,
        isAuthenticated: true
      }),

      logout: () => set({
        user: null,
        token: null,
        isAuthenticated: false
      }),

      updateUser: (updates) => set((state) => ({
        user: state.user ? { ...state.user, ...updates } : null,
      })),
    }),
    {
      name: 'auth-storage', // localStorage key
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Helper hook to get auth status
export function useAuth() {
  const { user, token, isAuthenticated } = useAuthStore();
  return { user, token, isAuthenticated };
}

// Helper hook to check if user is authenticated
export function useRequireAuth() {
  const { isAuthenticated, user } = useAuthStore();

  if (typeof window !== 'undefined' && !isAuthenticated) {
    window.location.href = '/login';
  }

  return { isAuthenticated, user };
}

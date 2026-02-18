/**
 * Telegram authentication utilities for web interface
 */

export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

export interface TelegramAuthResult {
  success: boolean;
  user?: TelegramUser;
  error?: string;
}

/**
 * Get Telegram user from URL parameters (after redirect)
 */
export function getTelegramUserFromUrl(): TelegramUser | null {
  if (typeof window === 'undefined') return null;

  const params = new URLSearchParams(window.location.search);

  const id = params.get('id');
  const first_name = params.get('first_name');
  const auth_date = params.get('auth_date');
  const hash = params.get('hash');

  if (!id || !first_name || !auth_date || !hash) {
    return null;
  }

  return {
    id: parseInt(id),
    first_name,
    last_name: params.get('last_name') || undefined,
    username: params.get('username') || undefined,
    photo_url: params.get('photo_url') || undefined,
    auth_date: parseInt(auth_date),
    hash,
  };
}

/**
 * Login with Telegram - returns a promise that resolves when user authenticates
 */
export function loginWithTelegram(): Promise<TelegramUser> {
  return new Promise((resolve, reject) => {
    // Set up the callback for Telegram widget
    (window as any).onTelegramAuth = (user: TelegramUser) => {
      resolve(user);
    };

    // Check if user data is already in URL (redirect case)
    const urlUser = getTelegramUserFromUrl();
    if (urlUser) {
      resolve(urlUser);
      return;
    }

    // If Telegram widget is not loaded, reject after timeout
    setTimeout(() => {
      reject(new Error('Telegram authentication timeout'));
    }, 30000);
  });
}

/**
 * Authenticate with backend using Telegram user data
 */
export async function authenticateWithBackend(telegramUser: TelegramUser): Promise<any> {
  // Use relative URL to work in both browser and Telegram Web App
  const API_URL = typeof window !== 'undefined' ? window.location.origin : '';

  const response = await fetch(`${API_URL}/api/auth/telegram`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(telegramUser),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Authentication failed');
  }

  return response.json();
}

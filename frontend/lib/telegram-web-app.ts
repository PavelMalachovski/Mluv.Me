/**
 * Telegram Web App integration
 * Docs: https://core.telegram.org/bots/webapps
 */

export interface TelegramWebAppUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  photo_url?: string;
}

export interface TelegramWebAppThemeParams {
  bg_color?: string;
  text_color?: string;
  hint_color?: string;
  link_color?: string;
  button_color?: string;
  button_text_color?: string;
  secondary_bg_color?: string;
}

export interface TelegramMainButton {
  text: string;
  color: string;
  textColor: string;
  isVisible: boolean;
  isActive: boolean;
  isProgressVisible: boolean;
  setText: (text: string) => void;
  onClick: (callback: () => void) => void;
  offClick: (callback: () => void) => void;
  show: () => void;
  hide: () => void;
  enable: () => void;
  disable: () => void;
  showProgress: (leaveActive?: boolean) => void;
  hideProgress: () => void;
}

export interface TelegramBackButton {
  isVisible: boolean;
  onClick: (callback: () => void) => void;
  offClick: (callback: () => void) => void;
  show: () => void;
  hide: () => void;
}

export interface TelegramWebApp {
  initData: string;
  initDataUnsafe: {
    query_id?: string;
    user?: TelegramWebAppUser;
    receiver?: TelegramWebAppUser;
    chat?: any;
    start_param?: string;
    auth_date?: number;
    hash?: string;
  };
  version: string;
  platform: string;
  colorScheme: 'light' | 'dark';
  themeParams: TelegramWebAppThemeParams;
  isExpanded: boolean;
  viewportHeight: number;
  viewportStableHeight: number;
  headerColor: string;
  backgroundColor: string;
  isClosingConfirmationEnabled: boolean;
  MainButton: TelegramMainButton;
  BackButton: TelegramBackButton;
  HapticFeedback: {
    impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
    notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
    selectionChanged: () => void;
  };
  ready: () => void;
  expand: () => void;
  close: () => void;
  enableClosingConfirmation: () => void;
  disableClosingConfirmation: () => void;
  onEvent: (eventType: string, eventHandler: () => void) => void;
  offEvent: (eventType: string, eventHandler: () => void) => void;
  sendData: (data: string) => void;
  openLink: (url: string, options?: { try_instant_view?: boolean }) => void;
  openTelegramLink: (url: string) => void;
  showPopup: (params: {
    title?: string;
    message: string;
    buttons?: Array<{ id?: string; type?: string; text?: string }>;
  }, callback?: (buttonId: string) => void) => void;
  showAlert: (message: string, callback?: () => void) => void;
  showConfirm: (message: string, callback?: (confirmed: boolean) => void) => void;
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp;
    };
  }
}

/**
 * Check if app is running inside Telegram Web App
 */
export function isTelegramWebApp(): boolean {
  if (typeof window === 'undefined') return false;
  return Boolean(window.Telegram?.WebApp);
}

/**
 * Get Telegram Web App instance
 */
export function getTelegramWebApp(): TelegramWebApp | null {
  if (typeof window === 'undefined') return null;
  return window.Telegram?.WebApp || null;
}

/**
 * Get authenticated Telegram user from Web App
 */
export function getTelegramUser(): TelegramWebAppUser | null {
  const webApp = getTelegramWebApp();
  return webApp?.initDataUnsafe?.user || null;
}

/**
 * Get Telegram Web App init data for backend validation
 */
export function getTelegramInitData(): string | null {
  const webApp = getTelegramWebApp();
  return webApp?.initData || null;
}

/**
 * Initialize Telegram Web App
 * Call this early in your app lifecycle
 */
export function initTelegramWebApp(): TelegramWebApp | null {
  const webApp = getTelegramWebApp();

  if (!webApp) {
    console.warn('Telegram Web App is not available. Are you running inside Telegram?');
    return null;
  }

  // Signal that the Web App is ready
  webApp.ready();

  // Expand to full height
  webApp.expand();

  // Enable closing confirmation to prevent accidental exits
  webApp.enableClosingConfirmation();

  console.log('Telegram Web App initialized', {
    version: webApp.version,
    platform: webApp.platform,
    user: webApp.initDataUnsafe.user,
  });

  return webApp;
}

/**
 * Authenticate with backend using Telegram Web App data
 */
export async function authenticateWebApp(): Promise<{
  success: boolean;
  user?: any;
  token?: string;
  error?: string;
}> {
  const initData = getTelegramInitData();

  if (!initData) {
    return {
      success: false,
      error: 'Not running in Telegram Web App',
    };
  }

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  try {
    const response = await fetch(`${API_URL}/api/v1/auth/webapp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ initData }),
    });

    if (!response.ok) {
      const error = await response.json();
      return {
        success: false,
        error: error.detail || 'Authentication failed',
      };
    }

    const data = await response.json();
    return {
      success: true,
      user: data.user,
      token: data.token,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
}

/**
 * Show loading state on Main Button
 */
export function showMainButtonLoading(text: string = 'Loading...') {
  const webApp = getTelegramWebApp();
  if (webApp) {
    webApp.MainButton.setText(text);
    webApp.MainButton.showProgress();
    webApp.MainButton.disable();
  }
}

/**
 * Hide loading state on Main Button
 */
export function hideMainButtonLoading() {
  const webApp = getTelegramWebApp();
  if (webApp) {
    webApp.MainButton.hideProgress();
    webApp.MainButton.enable();
  }
}

/**
 * Setup Main Button
 */
export function setupMainButton(
  text: string,
  onClick: () => void,
  options?: {
    color?: string;
    textColor?: string;
  }
) {
  const webApp = getTelegramWebApp();
  if (!webApp) return;

  webApp.MainButton.setText(text);

  if (options?.color) {
    webApp.MainButton.color = options.color;
  }

  if (options?.textColor) {
    webApp.MainButton.textColor = options.textColor;
  }

  webApp.MainButton.onClick(onClick);
  webApp.MainButton.show();
}

/**
 * Show haptic feedback
 */
export function hapticFeedback(
  type: 'impact' | 'notification' | 'selection',
  style?: 'light' | 'medium' | 'heavy' | 'error' | 'success' | 'warning'
) {
  const webApp = getTelegramWebApp();
  if (!webApp) return;

  if (type === 'impact' && style) {
    webApp.HapticFeedback.impactOccurred(style as any);
  } else if (type === 'notification' && style) {
    webApp.HapticFeedback.notificationOccurred(style as any);
  } else if (type === 'selection') {
    webApp.HapticFeedback.selectionChanged();
  }
}

/**
 * Get theme colors for styling
 */
export function getThemeColors(): TelegramWebAppThemeParams {
  const webApp = getTelegramWebApp();
  return webApp?.themeParams || {
    bg_color: '#ffffff',
    text_color: '#000000',
    hint_color: '#999999',
    link_color: '#3390ec',
    button_color: '#3390ec',
    button_text_color: '#ffffff',
    secondary_bg_color: '#f4f4f5',
  };
}

/**
 * Check if user is premium
 */
export function isPremiumUser(): boolean {
  const user = getTelegramUser();
  return user?.is_premium || false;
}

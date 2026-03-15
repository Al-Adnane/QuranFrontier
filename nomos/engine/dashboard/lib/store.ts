import { create } from 'zustand';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'public' | 'researcher' | 'scholar' | 'admin';
  canApprove: boolean;
  expertise?: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User | null) => void;
  setError: (error: string | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      // Mock login - replace with actual API call
      const mockUser: User = {
        id: 'SCHOL-01',
        name: 'Dr. Ahmed Al-Ansari',
        email: email,
        role: 'scholar',
        canApprove: true,
        expertise: 'Hadith Authentication',
      };

      set({
        user: mockUser,
        isAuthenticated: true,
        isLoading: false,
      });

      // Store token in localStorage
      localStorage.setItem('auth_token', 'mock-token-123');
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Login failed',
        isLoading: false,
      });
    }
  },

  logout: () => {
    set({
      user: null,
      isAuthenticated: false,
    });
    localStorage.removeItem('auth_token');
  },

  setUser: (user: User | null) => {
    set({
      user,
      isAuthenticated: !!user,
    });
  },

  setError: (error: string | null) => {
    set({ error });
  },
}));

// Notifications store for real-time updates
interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  message: string;
  timestamp: Date;
}

interface NotificationState {
  notifications: Notification[];
  addNotification: (type: Notification['type'], message: string) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],

  addNotification: (type: Notification['type'], message: string) => {
    const id = Date.now().toString();
    const notification: Notification = {
      id,
      type,
      message,
      timestamp: new Date(),
    };

    set((state) => ({
      notifications: [...state.notifications, notification],
    }));

    // Auto-remove after 5 seconds
    setTimeout(() => {
      set((state) => ({
        notifications: state.notifications.filter((n) => n.id !== id),
      }));
    }, 5000);
  },

  removeNotification: (id: string) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    }));
  },

  clearNotifications: () => {
    set({ notifications: [] });
  },
}));

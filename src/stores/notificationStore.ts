import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { SafetyLevel } from '@/components/ui/SafetyAlert';

export interface AppNotification {
  id: string;
  level: SafetyLevel;
  title: string;
  message?: string;
  createdAt: string;
  dismissed: boolean;
}

interface NotificationState {
  notifications: AppNotification[];
  publish: (notification: Omit<AppNotification, 'createdAt' | 'dismissed'>) => void;
  dismiss: (id: string) => void;
  clearHistory: () => void;
}

export const useNotificationStore = create<NotificationState>()(
  persist(
    (set) => ({
      notifications: [],
      publish: (notification) =>
        set((state) => ({
          notifications: state.notifications.some((item) => item.id === notification.id)
            ? state.notifications
            : [
                {
                  ...notification,
                  createdAt: new Date().toISOString(),
                  dismissed: false,
                },
                ...state.notifications,
              ].slice(0, 50),
        })),
      dismiss: (id) =>
        set((state) => ({
          notifications: state.notifications.map((item) =>
            item.id === id ? { ...item, dismissed: true } : item,
          ),
        })),
      clearHistory: () => set({ notifications: [] }),
    }),
    { name: 'pharmatrybe-notifications' },
  ),
);

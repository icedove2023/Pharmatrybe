import { create } from 'zustand';
import { UserSettings } from '@/types';
import { settingsApi } from '@/api';

interface SettingsState {
  settings: UserSettings;
  isLoading: boolean;
  loadSettings: () => Promise<void>;
  updateSettings: (newSettings: Partial<UserSettings>) => Promise<void>;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}

const initialSettings: UserSettings = {
  theme: 'light',
  language: 'en-US',
  defaultDosingUnit: 'mg',
  defaultExecutionMode: 'AUTO',
  awareStrictMode: true,
  highRiskAlertThreshold: 85,
  emailNotifications: true,
  autoSaveDrafts: true,
};

export const useSettingsStore = create<SettingsState>((set, get) => ({
  settings: initialSettings,
  isLoading: false,

  loadSettings: async () => {
    set({ isLoading: true });
    try {
      const settings = await settingsApi.getSettings();
      set({ settings, isLoading: false });
      get().setTheme(settings.theme);
    } catch {
      set({ isLoading: false });
    }
  },

  updateSettings: async (newSettings) => {
    const updated = { ...get().settings, ...newSettings };
    set({ settings: updated });
    await settingsApi.saveSettings(updated);
    if (newSettings.theme) {
      get().setTheme(newSettings.theme);
    }
  },

  setTheme: (theme) => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else if (theme === 'light') {
      root.classList.remove('dark');
    } else {
      const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (systemDark) root.classList.add('dark');
      else root.classList.remove('dark');
    }
  },
}));

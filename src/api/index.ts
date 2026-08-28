import { DashboardData, PatientDetails, PatientSummary, HistoryEvent, UserSettings } from '@/types';
import { authApi } from './authApi';
import { adminApi } from './adminApi';
import { recommendationApi } from './recommendationApi';
import { whoApi } from './whoApi';
import { soarApi } from './soarApi';
import { armdApi } from './armdApi';
import { clinicalCasesApi } from './clinicalCasesApi';
import { pipelineApi } from './pipelineApi';
import { pluginGovernanceApi } from './pluginGovernanceApi';
import { professionalsApi } from './professionalsApi';

export { authApi, adminApi, recommendationApi, whoApi, soarApi, armdApi, clinicalCasesApi, pipelineApi, pluginGovernanceApi, professionalsApi };

function unavailable<T>(capability: string): Promise<T> {
  return Promise.reject(new Error(`${capability} is not exposed by the backend.`));
}

export const dashboardApi = {
  getDashboardData: (): Promise<DashboardData> => unavailable('Dashboard aggregates'),
};

export const patientApi = {
  searchPatients: (_query: string): Promise<PatientSummary[]> => unavailable('Patient directory; use clinical cases'),
  getPatientDetails: (_id: string): Promise<PatientDetails> => unavailable('Patient details; use clinical cases'),
  getPatientHistory: (_id: string): Promise<HistoryEvent[]> => unavailable('Patient history; use clinical cases'),
};

const defaultSettings: UserSettings = {
  theme: 'light',
  language: 'en-US',
  defaultDosingUnit: 'mg',
  awareStrictMode: true,
  highRiskAlertThreshold: 85,
  defaultExecutionMode: 'AUTO',
  emailNotifications: true,
  autoSaveDrafts: true,
};

export const settingsApi = {
  getSettings: async (): Promise<UserSettings> => {
    if (typeof window === 'undefined') return defaultSettings;
    const saved = window.localStorage.getItem('pharmatrybe_settings');
    return saved ? JSON.parse(saved) as UserSettings : defaultSettings;
  },
  saveSettings: async (settings: UserSettings): Promise<UserSettings> => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('pharmatrybe_settings', JSON.stringify(settings));
    }
    return settings;
  },
};

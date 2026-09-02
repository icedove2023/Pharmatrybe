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
import { getPatientById, getPatientHistory, searchPatients } from './patientsApi';
import { useAuthStore } from '@/stores/authStore';

export { authApi, adminApi, recommendationApi, whoApi, soarApi, armdApi, clinicalCasesApi, pipelineApi, pluginGovernanceApi, professionalsApi };

function unavailable<T>(capability: string): Promise<T> {
  return Promise.reject(new Error(`${capability} is not exposed by the backend.`));
}

export const dashboardApi = {
  getDashboardData: (): Promise<DashboardData> => unavailable('Dashboard aggregates'),
};

export const patientApi = {
  searchPatients: async (query: string): Promise<PatientSummary[]> => {
    if (!useAuthStore.getState().user) return [];
    try {
      const results = await searchPatients(query);
      return results.map((patient) => ({
        id: patient.id,
        name: patient.name || 'Patient not named',
        dateOfBirth: patient.date_of_birth || '',
        gender: patient.sex || 'Unknown',
        lastActivity: '',
        recordCount: patient.recordCount || 0,
      }));
    } catch {
      return [];
    }
  },
  getPatientDetails: async (id: string): Promise<PatientDetails> => {
    if (!useAuthStore.getState().user) throw new Error('Authentication required.');
    const patient = await getPatientById(id);
    if (!patient) {
      throw new Error('Patient details are not available.');
    }

    const demographics = (patient.demographics ?? {}) as Record<string, unknown>;
    return {
      id: patient.id,
      name: patient.name || 'Patient not named',
      age: Number(demographics.age ?? patient.age ?? 0),
      sex: String(demographics.sex ?? patient.sex ?? 'Unknown'),
      allergies: Array.isArray(demographics.allergies) ? (demographics.allergies as string[]) : (patient.allergies ?? []),
      comorbidities: Array.isArray(demographics.comorbidities) ? (demographics.comorbidities as string[]) : (patient.comorbidities ?? []),
      mrn: String(demographics.mrn ?? patient.hospital_id ?? patient.id),
    };
  },
  getPatientHistory: async (id: string): Promise<HistoryEvent[]> => {
    if (!useAuthStore.getState().user) return [];
    const result = await getPatientHistory(id);
    return Array.isArray(result) ? (result as HistoryEvent[]) : [];
  },
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

import { create } from 'zustand';
import { ClinicalCase, Demographics, Presentation, Laboratory, RiskFactors, ExecutionMode } from '@/types';

const defaultCase: ClinicalCase = {
  demographics: {
    patientId: 'pat-001',
    patientName: 'John Doe',
    age: 68,
    sex: 'Male',
    weight: 75,
    creatinineClearance: 55,
  },
  presentation: {
    primaryDiagnosis: 'Community-Acquired Pneumonia (CAP)',
    infectionSite: 'Lower Respiratory Tract',
    severity: 'Moderate',
    symptoms: ['High Fever (>38.5°C)', 'Productive Cough', 'Dyspnea / Shortness of Breath', 'Pleuritic Chest Pain'],
    vitals: {
      temperature: 38.6,
      heartRate: 98,
      respiratoryRate: 22,
      bloodPressure: '128/82',
      oxygenSaturation: 94,
    },
  },
  laboratory: {
    crp: 45,
    wbc: 13.8,
    creatinine: 1.1,
    egfr: 55,
    procalcitonin: 0.6,
    cultureResult: 'Sputum Gram-positive diplococci (Suspected S. pneumoniae)',
    suspectedPathogen: 'Streptococcus pneumoniae',
  },
  riskFactors: {
    allergies: ['Penicillin (Mild Rash reported 10 yrs ago)'],
    comorbidities: ['Hypertension', 'T2 Diabetes Mellitus'],
    concomitantMedications: ['Lisinopril 10mg QD', 'Metformin 500mg BID'],
    isPregnant: false,
    isLactating: false,
    isImmunocompromised: false,
    priorAntibiotics90Days: false,
    recentHospitalization: false,
  },
  executionMode: 'AUTO',
  pluginSelections: ['soar', 'armd', 'who_knowledge'],
  status: 'Draft',
};

interface ClinicalCaseState {
  caseData: ClinicalCase;
  currentStep: number;
  updateDemographics: (data: Partial<Demographics>) => void;
  updatePresentation: (data: Partial<Presentation>) => void;
  updateLaboratory: (data: Partial<Laboratory>) => void;
  updateRiskFactors: (data: Partial<RiskFactors>) => void;
  setExecutionMode: (mode: ExecutionMode) => void;
  togglePluginSelection: (pluginId: string) => void;
  setCurrentStep: (step: number) => void;
  resetCase: () => void;
  loadPresetCase: (preset: 'cap' | 'uti' | 'ssti') => void;
}

export const useClinicalCaseStore = create<ClinicalCaseState>((set) => ({
  caseData: defaultCase,
  currentStep: 1,

  setCurrentStep: (step) => set({ currentStep: step }),

  updateDemographics: (data) =>
    set((state) => ({
      caseData: {
        ...state.caseData,
        demographics: { ...state.caseData.demographics, ...data },
      },
    })),

  updatePresentation: (data) =>
    set((state) => ({
      caseData: {
        ...state.caseData,
        presentation: { ...state.caseData.presentation, ...data },
      },
    })),

  updateLaboratory: (data) =>
    set((state) => ({
      caseData: {
        ...state.caseData,
        laboratory: { ...state.caseData.laboratory, ...data },
      },
    })),

  updateRiskFactors: (data) =>
    set((state) => ({
      caseData: {
        ...state.caseData,
        riskFactors: { ...state.caseData.riskFactors, ...data },
      },
    })),

  setExecutionMode: (mode) =>
    set((state) => ({
      caseData: {
        ...state.caseData,
        executionMode: mode,
      },
    })),

  togglePluginSelection: (pluginId) =>
    set((state) => {
      const current = state.caseData.pluginSelections || [];
      const updated = current.includes(pluginId)
        ? current.filter((id) => id !== pluginId)
        : [...current, pluginId];
      return {
        caseData: {
          ...state.caseData,
          pluginSelections: updated,
        },
      };
    }),

  resetCase: () => set({ caseData: defaultCase, currentStep: 1 }),

  loadPresetCase: (preset) => {
    if (preset === 'uti') {
      set({
        currentStep: 1,
        caseData: {
          demographics: { patientId: 'pat-002', patientName: 'Jane Smith', age: 45, sex: 'Female', weight: 62, creatinineClearance: 95 },
          presentation: {
            primaryDiagnosis: 'Uncomplicated Acute Cystitis (UTI)',
            infectionSite: 'Urinary Tract (Bladder)',
            severity: 'Non-severe',
            symptoms: ['Dysuria / Burning Sensation', 'Urinary Frequency', 'Suprapubic Pain'],
            vitals: { temperature: 37.1, heartRate: 74, respiratoryRate: 14, bloodPressure: '118/76', oxygenSaturation: 99 },
          },
          laboratory: { wbc: 8.5, crp: 12, egfr: 95, cultureResult: 'Urine Dipstick: Leukocyte Positive, Nitrite Positive', suspectedPathogen: 'Escherichia coli' },
          riskFactors: { allergies: ['Sulfa Drugs (Hives / Rash)'], comorbidities: ['Asthma'], concomitantMedications: ['Albuterol Inhaler PRN'], isPregnant: false, isLactating: false, isImmunocompromised: false, priorAntibiotics90Days: false, recentHospitalization: false },
          executionMode: 'AUTO',
          pluginSelections: ['soar', 'armd', 'who_knowledge'],
        },
      });
    } else if (preset === 'ssti') {
      set({
        currentStep: 1,
        caseData: {
          demographics: { patientId: 'pat-003', patientName: 'Robert Brown', age: 54, sex: 'Male', weight: 88, creatinineClearance: 80 },
          presentation: {
            primaryDiagnosis: 'Non-purulent Cellulitis (SSTI)',
            infectionSite: 'Skin & Soft Tissue (Lower Extremity)',
            severity: 'Moderate',
            symptoms: ['Erythema & Warmth on Lower Leg', 'Localized Tenderness', 'Low Grade Fever'],
            vitals: { temperature: 38.0, heartRate: 82, respiratoryRate: 16, bloodPressure: '135/85', oxygenSaturation: 97 },
          },
          laboratory: { wbc: 11.2, crp: 28, egfr: 80, suspectedPathogen: 'Streptococcus pyogenes' },
          riskFactors: { allergies: [], comorbidities: ['T2 Diabetes'], concomitantMedications: ['Metformin 1000mg BID'], isPregnant: false, isLactating: false, isImmunocompromised: false, priorAntibiotics90Days: false, recentHospitalization: false },
          executionMode: 'AUTO',
          pluginSelections: ['soar', 'armd', 'who_knowledge'],
        },
      });
    } else {
      set({ caseData: defaultCase, currentStep: 1 });
    }
  },
}));

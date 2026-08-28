import { ClinicalCase } from '@/types';
import { apiRequest, unwrapApiData } from './client';

type BackendEnvelope<T> = { data: T };

function uuid(): string {
  return crypto.randomUUID();
}

function toFrontendCase(resource: any): ClinicalCase {
  const payload = resource?.clinical_case || resource;
  return {
    id: payload.case_id || resource?.id,
    demographics: {
      patientId: payload.case_id,
      patientName: payload.user_metadata?.patient_name,
      age: payload.demographics?.age ?? 0,
      sex: payload.demographics?.sex === 'female' ? 'Female' : payload.demographics?.sex === 'male' ? 'Male' : 'Other',
      weight: payload.demographics?.weight,
    },
    presentation: {
      symptoms: payload.presentation?.symptoms || [],
      primaryDiagnosis: payload.presentation?.syndrome || '',
      infectionSite: payload.presentation?.acquisition || '',
      severity: payload.presentation?.severity === 'severe' ? 'Severe' : payload.presentation?.severity === 'moderate' ? 'Moderate' : 'Non-severe',
      vitals: payload.vitals || {},
    },
    laboratory: { ...payload.biomarkers, suspectedPathogen: payload.laboratory?.organism },
    riskFactors: { allergies: [], comorbidities: [], isPregnant: payload.risk_factors?.pregnancy || false, isImmunocompromised: payload.risk_factors?.immunocompromised || false, priorAntibiotics90Days: false, recentHospitalization: payload.armd_inputs?.recent_hospitalization || false },
    status: resource?.status === 'received' ? 'Submitted' : 'Analyzed',
    createdAt: payload.timestamp,
  };
}

function toBackendCase(input: ClinicalCase): Record<string, unknown> {
  return {
    request_id: uuid(),
    case_id: input.id && /^[0-9a-f-]{36}$/i.test(input.id) ? input.id : uuid(),
    timestamp: input.createdAt || new Date().toISOString(),
    schema_version: '1.0.0',
    demographics: { age: input.demographics.age, sex: input.demographics.sex.toLowerCase(), weight: input.demographics.weight },
    presentation: { syndrome: input.presentation.primaryDiagnosis, severity: input.presentation.severity === 'Severe' ? 'severe' : input.presentation.severity === 'Moderate' ? 'moderate' : 'mild', acquisition: 'community', symptoms: input.presentation.symptoms },
    risk_factors: { pregnancy: input.riskFactors.isPregnant, immunocompromised: input.riskFactors.isImmunocompromised },
    laboratory: { organism: input.laboratory.suspectedPathogen, culture_available: Boolean(input.laboratory.cultureResult), susceptibility_available: false },
    vitals: input.presentation.vitals,
    biomarkers: input.laboratory,
    user_metadata: {},
    routing_metadata: { use_soar: true, use_armd: true, use_who: true },
    resistance_status: 'none',
  };
}

export const clinicalCasesApi = {
  async getClinicalCases(): Promise<ClinicalCase[]> {
    const response = await apiRequest<BackendEnvelope<any[]>>('/clinical-cases');
    return unwrapApiData(response).map(toFrontendCase);
  },
  async getClinicalCaseById(caseId: string): Promise<ClinicalCase | null> {
    const response = await apiRequest<BackendEnvelope<any | null>>(`/clinical-cases/${encodeURIComponent(caseId)}`);
    const resource = unwrapApiData(response);
    return resource ? toFrontendCase(resource) : null;
  },
  async submitClinicalCase(caseData: Omit<ClinicalCase, 'id' | 'createdAt' | 'status'>): Promise<ClinicalCase> {
    const response = await apiRequest<any>('/clinical-cases', { method: 'POST', body: JSON.stringify(toBackendCase(caseData as ClinicalCase)) });
    return toFrontendCase(response.data?.clinical_case || response.data);
  },
};
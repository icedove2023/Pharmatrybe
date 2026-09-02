import { apiRequest, unwrapApiData } from './client';

export interface PatientSummary {
  id: string;
  name?: string;
  initiatedBy?: string;
  date_of_birth?: string;
  sex?: string;
  hospital_id?: string;
  age?: number;
  allergies?: string[];
  comorbidities?: string[];
  recordCount?: number;
}

export interface PatientDetail extends PatientSummary {
  demographics?: Record<string, unknown>;
  identifiers?: Array<{ system: string; value: string }>;
}

type ApiEnvelope<T> = { data: T };

export async function getPatientById(patientId: string): Promise<PatientDetail | null> {
  const response = await apiRequest<ApiEnvelope<PatientDetail | null>>(`/patients/${encodeURIComponent(patientId)}`);
  return unwrapApiData(response);
}

export async function searchPatients(query: string): Promise<PatientSummary[]> {
  const suffix = query.trim() ? `?query=${encodeURIComponent(query.trim())}` : '';
  const response = await apiRequest<ApiEnvelope<PatientSummary[]>>(`/patients${suffix}`);
  return unwrapApiData(response);
}

export async function getPatientHistory(patientId: string): Promise<unknown[]> {
  const response = await apiRequest<ApiEnvelope<unknown[]>>(`/patients/${encodeURIComponent(patientId)}/history`);
  return unwrapApiData(response);
}

export async function createApprovedPatientHistory(
  patientId: string,
  payload: {
    recommendation_id: string;
    review_decision: 'APPROVED' | 'MODIFIED';
    selected_antibiotic?: string;
    clinical_notes?: string;
    patient_name?: string;
    demographics?: Record<string, unknown>;
  },
): Promise<unknown> {
  const response = await apiRequest<ApiEnvelope<unknown>>(`/patients/${encodeURIComponent(patientId)}/history`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return unwrapApiData(response);
}

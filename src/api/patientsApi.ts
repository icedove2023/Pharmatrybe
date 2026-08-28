import { apiRequest, unwrapApiData } from './client';
import { ApiClientError } from './client';

export interface PatientSummary {
  id: string;
  name?: string;
  date_of_birth?: string;
  sex?: string;
  hospital_id?: string;
}

export interface PatientDetail extends PatientSummary {
  demographics?: Record<string, unknown>;
  identifiers?: Array<{ system: string; value: string }>;
  // other fields are intentionally left open — the frontend should not assume structure beyond what's returned
}

export async function getPatientById(patientId: string): Promise<PatientDetail | null> {
  void patientId;
  return null;
}

export async function searchPatients(query: string): Promise<PatientSummary[] | null> {
  void query;
  return null;
}

export async function getPatientHistory(patientId: string): Promise<unknown | null> {
  void patientId;
  return null;
}

import { DiseaseSummary, DiseaseDetail, AntimicrobialRecommendation } from '@/types';
import { apiRequest, unwrapApiData } from './client';

type ApiSuccess<T> = { data: T };
type BackendDisease = { disease_id: string; name: string; chapter_title?: string | null; care_level?: string | null; description?: string | null };

function toSummary(disease: BackendDisease): DiseaseSummary {
  return { id: disease.disease_id, name: disease.name, category: disease.chapter_title || 'Not exposed by backend', commonPathogens: [], awareClass: (disease.care_level || 'Access') as DiseaseSummary['awareClass'] };
}

async function getTextItems(path: string): Promise<string[]> {
  const response = await apiRequest<ApiSuccess<Record<string, unknown>[]>>(path);
  return unwrapApiData(response).map((item) => String(item.description || item.message || item.text || item.name || ''));
}

export const whoApi = {
  async getWhoDiseases(): Promise<DiseaseSummary[]> {
    const response = await apiRequest<ApiSuccess<BackendDisease[]>>('/who/diseases');
    return unwrapApiData(response).map(toSummary);
  },
  async getWhoDiseaseById(id: string): Promise<DiseaseDetail | null> {
    const response = await apiRequest<ApiSuccess<BackendDisease | null>>(`/who/diseases/${encodeURIComponent(id)}`);
    const disease = unwrapApiData(response);
    if (!disease) return null;
    return { ...toSummary(disease), overview: disease.description || '', recommendations: [], diagnostics: [], monitoring: [], stewardship: [], referralCriteria: [] };
  },
  async searchWhoDiseases(query: string): Promise<DiseaseSummary[]> {
    const response = await apiRequest<ApiSuccess<BackendDisease[]>>(query.trim() ? `/who/search?q=${encodeURIComponent(query.trim())}` : '/who/diseases');
    return unwrapApiData(response).map(toSummary);
  },
  async getWhoRecommendations(id: string): Promise<AntimicrobialRecommendation[]> {
    const response = await apiRequest<ApiSuccess<Record<string, unknown>[]>>(`/who/recommendations/${encodeURIComponent(id)}`);
    return unwrapApiData(response) as unknown as AntimicrobialRecommendation[];
  },
  async getWhoEvidence(id: string): Promise<{ diseaseId: string; evidenceSummary: string; grades: { drug: string; grade: string }[] } | null> {
    const response = await apiRequest<ApiSuccess<Record<string, unknown>[]>>(`/who/evidence/${encodeURIComponent(id)}`);
    return { diseaseId: id, evidenceSummary: '', grades: unwrapApiData(response).map((item) => ({ drug: String(item.drug_name || item.drug || ''), grade: String(item.evidence_level || item.grade || '') })) };
  },
  async getWhoGuideline(id: string): Promise<{ id: string; name: string; overview: string; awareClass: string } | null> {
    const response = await apiRequest<ApiSuccess<Record<string, unknown> | null>>(`/who/guideline/${encodeURIComponent(id)}`);
    const data = unwrapApiData(response);
    return data ? { id, name: String(data.name || ''), overview: String(data.description || data.overview || ''), awareClass: String(data.care_level || '') } : null;
  },
  async getWhoPathogens(id: string): Promise<string[]> {
    const response = await apiRequest<ApiSuccess<Record<string, unknown>[]>>(`/who/pathogens/${encodeURIComponent(id)}`);
    return unwrapApiData(response).map((item) => String(item.name || item.pathogen_name || item.pathogen || ''));
  },
  getWhoStewardship: (id: string) => getTextItems(`/who/stewardship/${encodeURIComponent(id)}`),
  getWhoMonitoring: (id: string) => getTextItems(`/who/monitoring/${encodeURIComponent(id)}`),
  getWhoDiagnostics: (id: string) => getTextItems(`/who/diagnostics/${encodeURIComponent(id)}`),
  getWhoFollowUp: (id: string) => getTextItems(`/who/follow-up/${encodeURIComponent(id)}`),
  getWhoReferral: (id: string) => getTextItems(`/who/referral/${encodeURIComponent(id)}`),
};
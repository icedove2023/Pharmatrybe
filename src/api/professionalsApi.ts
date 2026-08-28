import { apiRequest } from './client';

export const CANONICAL_ROLES = [
  { code: 'CLINICIAN', label: 'Clinician' },
  { code: 'PHARMACIST', label: 'Pharmacist' },
  { code: 'INFECTIOUS_DISEASE_SPECIALIST', label: 'Infectious Disease Specialist' },
  { code: 'LABORATORY_SCIENTIST', label: 'Laboratory Scientist' },
  { code: 'RESEARCHER', label: 'Researcher' },
  { code: 'HOSPITAL_ADMIN', label: 'Hospital Administrator' },
] as const;

export type CanonicalRoleCode = typeof CANONICAL_ROLES[number]['code'];

export interface ProfessionalInvitationResponse {
  invitation_id: string;
  hospital_id: string;
  role_code: CanonicalRoleCode;
  status: string;
  delivery: string;
}

export interface ProfessionalRecord {
  professional_id: string;
  first_name: string;
  last_name: string;
  professional_type?: string;
  profile_status: string;
  membership_id: string;
  membership_status: string;
  roles: string[];
  joined_at?: string;
}

export interface InvitationRecord {
  invitation_id: string;
  email: string;
  role_code: CanonicalRoleCode | string;
  status: string;
  expires_at: string;
  created_at?: string;
}

export interface InvitationAcceptanceRequest {
  token: string;
  first_name: string;
  last_name: string;
  professional_type?: string;
}

export const professionalsApi = {
  list: async () => (await apiRequest<{ items: ProfessionalRecord[] }>('/professionals')).items,
  listInvitations: async () => (await apiRequest<{ items: InvitationRecord[] }>('/professionals/invitations')).items,
  invite: (email: string, roleCode: CanonicalRoleCode) => apiRequest<ProfessionalInvitationResponse>('/professionals/invite', {
    method: 'POST',
    body: JSON.stringify({ email, role_code: roleCode }),
  }),
  acceptInvitation: (payload: InvitationAcceptanceRequest) => apiRequest<{ membership_id: string; hospital_id: string; status: string }>('/professionals/invitations/accept', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  updateMembership: (professionalId: string, payload: { status?: 'ACTIVE' | 'SUSPENDED' | 'DEACTIVATED'; role_code?: CanonicalRoleCode }) => apiRequest<{ professional_id: string; membership_id: string; status: string; roles: string[] }>(`/professionals/${encodeURIComponent(professionalId)}/membership`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  }),
};

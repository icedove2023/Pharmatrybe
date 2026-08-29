import { User, LoginCredentials, AuthSession, HospitalRegistrationPayload } from '@/types/auth';
import { apiRequest, ApiClientError } from '@/api/client';
import { supabase } from '@/lib/supabase';

const PENDING_HOSPITAL_REGISTRATION = 'pharmatrybe.pending-hospital-registration';

function savePendingRegistration(payload: HospitalRegistrationPayload): void {
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(PENDING_HOSPITAL_REGISTRATION, JSON.stringify({
      hospitalName: payload.hospitalName,
      country: payload.country,
      adminName: payload.adminName,
      adminEmail: payload.adminEmail,
    }));
  }
}

async function completePendingRegistration(email: string): Promise<boolean> {
  if (typeof window === 'undefined') return false;
  const raw = window.localStorage.getItem(PENDING_HOSPITAL_REGISTRATION);
  if (!raw) return false;
  const payload = JSON.parse(raw) as Pick<HospitalRegistrationPayload, 'hospitalName' | 'country' | 'adminName' | 'adminEmail'>;
  if (payload.adminEmail.toLowerCase() !== email.toLowerCase()) return false;
  try {
    await apiRequest<{ id: string; hospital_id: string; status: string }>('/auth/register-hospital', {
      method: 'POST',
      body: JSON.stringify({ hospital_name: payload.hospitalName, country: payload.country, admin_name: payload.adminName }),
    });
  } catch (error) {
    if (error instanceof ApiClientError) {
      throw new AuthError(`Your email is verified, but hospital setup failed: ${error.message}`, error.code === 'ACCOUNT_INACTIVE' ? 'account-inactive' : 'forbidden');
    }
    throw error;
  }
  window.localStorage.removeItem(PENDING_HOSPITAL_REGISTRATION);
  return true;
}

export class AuthError extends Error {
  code?: 'account-inactive' | 'forbidden' | 'invalid-session' | 'verification-required';

  constructor(message: string, code?: AuthError['code']) {
    super(message);
    this.name = 'AuthError';
    this.code = code;
  }
}

function toAuthSession(session: NonNullable<Awaited<ReturnType<typeof supabase.auth.getSession>>['data']['session']>): AuthSession {
  return {
    expiresAt: new Date((session.expires_at || 0) * 1000).toISOString(),
    traceSessionId: session.user.id,
  };
}

async function getApplicationUser(): Promise<User> {
  try {
    return await apiRequest<User>('/auth/me');
  } catch (error) {
    if (error instanceof ApiClientError && error.status === 403) {
      throw new AuthError(error.message, error.code === 'ACCOUNT_INACTIVE' ? 'account-inactive' : 'forbidden');
    }
    throw error;
  }
}

export const authApi = {
  registerHospital: async (payload: HospitalRegistrationPayload): Promise<{ user: User; session: AuthSession } | null> => {
    savePendingRegistration(payload);
    const { data, error } = await supabase.auth.signUp({
      email: payload.adminEmail,
      password: payload.password,
      options: { data: { first_name: payload.adminName } },
    });
    if (error) throw new AuthError(error.message);
    if (!data.session) return null;
    const session = toAuthSession(data.session);
    await completePendingRegistration(data.user?.email || payload.adminEmail);
    return { user: await getApplicationUser(), session };
  },
  login: async (credentials: LoginCredentials): Promise<{ user: User; session: AuthSession }> => {
    const { data, error } = await supabase.auth.signInWithPassword(credentials);
    if (error || !data.session) throw new AuthError(error?.message || 'Authentication failed.');
    await completePendingRegistration(data.user?.email || credentials.email);
    return { user: await getApplicationUser(), session: toAuthSession(data.session) };
  },
  getCurrentSession: async (): Promise<{ user: User; session: AuthSession } | null> => {
    const { data, error } = await supabase.auth.getSession();
    if (error || !data.session) return null;
    return { user: await getApplicationUser(), session: toAuthSession(data.session) };
  },
  logout: async (): Promise<void> => {
    const { error } = await supabase.auth.signOut();
    if (error) throw new AuthError(error.message);
  },
};

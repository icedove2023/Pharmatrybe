import { User, LoginCredentials, AuthSession, HospitalRegistrationPayload } from '@/types/auth';
import { apiRequest, ApiClientError } from '@/api/client';
import { supabase } from '@/lib/supabase';

export class AuthError extends Error {
  code?: 'account-inactive' | 'forbidden' | 'invalid-session';

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
  registerHospital: async (payload: HospitalRegistrationPayload): Promise<{ user: User; session: AuthSession }> => {
    const { data, error } = await supabase.auth.signUp({
      email: payload.adminEmail,
      password: payload.password,
      options: { data: { first_name: payload.adminName } },
    });
    if (error || !data.session) throw new AuthError(error?.message || 'Email verification is required before registration can continue.');
    const session = toAuthSession(data.session);
    await apiRequest<{ id: string; hospital_id: string; status: string }>('/auth/register-hospital', {
      method: 'POST',
      body: JSON.stringify({ hospital_name: payload.hospitalName, country: payload.country, admin_name: payload.adminName }),
    });
    return { user: await getApplicationUser(), session };
  },
  login: async (credentials: LoginCredentials): Promise<{ user: User; session: AuthSession }> => {
    const { data, error } = await supabase.auth.signInWithPassword(credentials);
    if (error || !data.session) throw new AuthError(error?.message || 'Authentication failed.');
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

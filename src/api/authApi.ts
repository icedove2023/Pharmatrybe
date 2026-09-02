import { User, LoginCredentials, AuthSession, HospitalRegistrationPayload } from '@/types/auth';
import { apiRequest, ApiClientError } from '@/api/client';
import { supabase } from '@/lib/supabase';

const PENDING_HOSPITAL_REGISTRATION = 'pending_hospital_registration';

type PendingHospitalRegistration = Pick<
  HospitalRegistrationPayload,
  'hospitalName' | 'country' | 'adminName' | 'adminEmail' | 'adminPhone' | 'adminProfessionalNumber'
>;

function getBrowserStorage(): Storage | null {
  const storageTarget = typeof window !== 'undefined' ? window : globalThis;
  try {
    return storageTarget.localStorage ?? null;
  } catch {
    return null;
  }
}

function serializePendingRegistration(payload: HospitalRegistrationPayload): PendingHospitalRegistration {
  return {
    hospitalName: payload.hospitalName,
    country: payload.country,
    adminName: payload.adminName,
    adminEmail: payload.adminEmail,
    adminPhone: payload.adminPhone,
    adminProfessionalNumber: payload.adminProfessionalNumber,
  };
}

function parsePendingRegistration(value: unknown): PendingHospitalRegistration | null {
  if (typeof value !== 'string') return null;

  try {
    const payload = JSON.parse(value) as Partial<PendingHospitalRegistration>;
    if (!payload || typeof payload !== 'object') {
      throw new Error('Pending hospital registration payload is invalid');
    }
    if (!payload.adminEmail || !payload.hospitalName || !payload.adminName || !payload.country) {
      throw new Error('Pending hospital registration payload is incomplete');
    }
    return payload as PendingHospitalRegistration;
  } catch {
    return null;
  }
}

function readPendingRegistrationFromMetadata(userMetadata?: Record<string, unknown> | null): PendingHospitalRegistration | null {
  if (!userMetadata) return null;
  const raw = userMetadata[PENDING_HOSPITAL_REGISTRATION];
  return parsePendingRegistration(raw);
}

function readPendingRegistrationFromStorage(): PendingHospitalRegistration | null {
  const storage = getBrowserStorage();
  if (!storage) return null;
  const raw = storage.getItem(PENDING_HOSPITAL_REGISTRATION);
  return parsePendingRegistration(raw);
}

function writePendingRegistrationToStorage(payload: PendingHospitalRegistration): void {
  const storage = getBrowserStorage();
  if (!storage) return;
  storage.setItem(PENDING_HOSPITAL_REGISTRATION, JSON.stringify(payload));
}

function clearPendingRegistrationFromStorage(): void {
  const storage = getBrowserStorage();
  if (!storage) return;
  storage.removeItem(PENDING_HOSPITAL_REGISTRATION);
}

async function clearPendingRegistrationForSession(session: Pick<NonNullable<Awaited<ReturnType<typeof supabase.auth.getSession>>['data']['session']>, 'user'> | null): Promise<void> {
  clearPendingRegistrationFromStorage();

  if (session?.user) {
    const userMetadata = (session.user as typeof session.user & { user_metadata?: Record<string, unknown> | null })?.user_metadata;
    if (userMetadata && typeof userMetadata === 'object') {
      delete userMetadata[PENDING_HOSPITAL_REGISTRATION];
    }

    try {
      await supabase.auth.updateUser({ data: { [PENDING_HOSPITAL_REGISTRATION]: null } });
    } catch {
      // Swallow update-user failures; the registration itself has already succeeded.
    }
  }
}

async function completePendingRegistration(email: string, session: Pick<NonNullable<Awaited<ReturnType<typeof supabase.auth.getSession>>['data']['session']>, 'user'> | null = null): Promise<boolean> {
  const metadataPayload = session ? readPendingRegistrationFromMetadata(session.user?.user_metadata) : null;
  const storedPayload = metadataPayload ?? readPendingRegistrationFromStorage();
  const payload = storedPayload;
  if (!payload) return false;
  if (!payload.adminEmail || payload.adminEmail.toLowerCase() !== email.toLowerCase()) return false;

  try {
    await apiRequest<{ id: string; hospital_id: string; status: string }>('/auth/register-hospital', {
      method: 'POST',
      body: JSON.stringify({
        hospital_name: payload.hospitalName,
        country: payload.country,
        admin_name: payload.adminName,
        admin_phone: payload.adminPhone,
        admin_professional_number: payload.adminProfessionalNumber,
      }),
    });
    await clearPendingRegistrationForSession(session);
    return true;
  } catch (error) {
    if (error instanceof ApiClientError) {
      if (error.status === 409) {
        await clearPendingRegistrationForSession(session);
        return true;
      }
      const detailMsg = error.details && typeof error.details === 'object'
        ? (error.details as any).message || error.message
        : error.message;
      throw new AuthError(
        `Your email is verified, but hospital setup failed: ${detailMsg}`,
        error.code === 'ACCOUNT_INACTIVE' ? 'account-inactive' : 'verification-required'
      );
    }
    throw error;
  }
}

async function completePendingRegistrationForSession(session: Pick<NonNullable<Awaited<ReturnType<typeof supabase.auth.getSession>>['data']['session']>, 'user'> | null): Promise<void> {
  const email = session?.user?.email;
  if (!email) return;
  await completePendingRegistration(email, session);
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
    const pendingRegistration = serializePendingRegistration(payload);
    writePendingRegistrationToStorage(pendingRegistration);
    const { data, error } = await supabase.auth.signUp({
      email: payload.adminEmail,
      password: payload.password,
      options: {
        data: {
          first_name: payload.adminName,
          [PENDING_HOSPITAL_REGISTRATION]: JSON.stringify(pendingRegistration),
        },
      },
    });
    if (error) throw new AuthError(error.message);
    if (!data.session) return null;
    const session = toAuthSession(data.session);
    await completePendingRegistration(data.user?.email || payload.adminEmail, data.session);
    return { user: await getApplicationUser(), session };
  },
  login: async (credentials: LoginCredentials): Promise<{ user: User; session: AuthSession }> => {
    const { data, error } = await supabase.auth.signInWithPassword(credentials);
    if (error || !data.session) throw new AuthError(error?.message || 'Authentication failed.');
    await completePendingRegistrationForSession(data.session);
    return { user: await getApplicationUser(), session: toAuthSession(data.session) };
  },
  getCurrentSession: async (): Promise<{ user: User; session: AuthSession } | null> => {
    const { data, error } = await supabase.auth.getSession();
    if (error || !data.session) return null;
    await completePendingRegistrationForSession(data.session);
    return { user: await getApplicationUser(), session: toAuthSession(data.session) };
  },
  logout: async (): Promise<void> => {
    const { error } = await supabase.auth.signOut();
    if (error) throw new AuthError(error.message);
  },
};

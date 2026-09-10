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
      if (error.code === 'EMAIL_NOT_VERIFIED') {
        // Keep the pending registration in place (both localStorage and user
        // metadata) so it completes automatically once the user confirms
        // their email and signs in again - nothing to clear here.
        throw new AuthError(
          'Please check your Gmail inbox and confirm your email address, then sign in to finish setting up your hospital.',
          'verification-required',
        );
      }
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
  code?: 'account-inactive' | 'email-delivery-failed' | 'forbidden' | 'invalid-session' | 'verification-required';

  constructor(message: string, code?: AuthError['code']) {
    super(message);
    this.name = 'AuthError';
    this.code = code;
  }
}

let hasLoggedSupabaseSignupError = false;

function isConfirmationEmailDeliveryFailure(error: { code?: string; message?: string }): boolean {
  return error.code === 'unexpected_failure'
    || /sending confirmation email/i.test(error.message || '');
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
    // Supabase can create auth.users before the confirmation email send fails;
    // this path must never assume signup failure means no account exists.
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
    if (error) {
      if (import.meta.env.DEV && !hasLoggedSupabaseSignupError) {
        hasLoggedSupabaseSignupError = true;
        console.error('[auth] Supabase signup error:', error);
      }
      if (isConfirmationEmailDeliveryFailure(error)) {
        throw new AuthError(
          'Your hospital account may already exist, but we could not send the confirmation email. Try resending it below, or sign in if you already confirmed it.',
          'email-delivery-failed',
        );
      }
      throw new AuthError(error.message);
    }
    if (!data.session) return null;
    const session = toAuthSession(data.session);
    await completePendingRegistration(data.user?.email || payload.adminEmail, data.session);
    return { user: await getApplicationUser(), session };
  },
  resendConfirmationEmail: async (email: string): Promise<void> => {
    const { error } = await supabase.auth.resend({ type: 'signup', email });
    if (error) throw new AuthError(error.message);
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
  refreshApplicationUser: async (): Promise<User> => getApplicationUser(),
  updateProfile: (payload: {
    firstName?: string;
    lastName?: string;
    phone?: string;
    professionalType?: string;
    licenseNumber?: string;
    dateOfBirth?: string;
  }): Promise<User> => apiRequest<User>('/auth/me', {
    method: 'PATCH',
    body: JSON.stringify({
      first_name: payload.firstName,
      last_name: payload.lastName,
      phone: payload.phone,
      professional_type: payload.professionalType,
      professional_registration_number: payload.licenseNumber,
      date_of_birth: payload.dateOfBirth,
    }),
  }).then(() => getApplicationUser()),
  markPasswordChanged: (): Promise<void> => apiRequest('/auth/me/password-changed', { method: 'POST' }).then(() => undefined),
  requestPasswordReset: async (email: string): Promise<void> => {
    const redirectTo = typeof window !== 'undefined' ? window.location.origin : undefined;
    const { error } = await supabase.auth.resetPasswordForEmail(email, redirectTo ? { redirectTo } : undefined);
    if (error) throw new AuthError(error.message);
  },
  completePasswordReset: async (newPassword: string): Promise<void> => {
    const { error } = await supabase.auth.updateUser({ password: newPassword });
    if (error) throw new AuthError(error.message);
  },
};

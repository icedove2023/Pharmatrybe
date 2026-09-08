import { create } from 'zustand';
import { User, LoginCredentials, UserRole, AuthSession, HospitalRegistrationPayload, BackendPermissionCode } from '@/types/auth';
import { authApi, AuthError } from '@/api/authApi';
import { supabase } from '@/lib/supabase';
import type { QueryClient } from '@tanstack/react-query';
import { setSessionInvalidationHandler } from '@/api/client';

export type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated' | 'session-expired' | 'session-invalid' | 'account-inactive' | 'forbidden' | 'password-recovery';

let activeQueryClient: QueryClient | null = null;

interface AuthState {
  user: User | null;
  session: AuthSession | null;
  status: AuthStatus;
  error: string | null;
  isAuthenticating: boolean;

  // Core Actions
  initialize: (queryClient?: QueryClient) => Promise<() => void>;
  login: (credentials: LoginCredentials) => Promise<void>;
  registerHospital: (payload: HospitalRegistrationPayload) => Promise<boolean>;
  logout: () => Promise<void>;
  switchRole: (role: UserRole) => Promise<void>;
  clearError: () => void;
  refreshUser: () => Promise<void>;

  // RBAC Selectors
  hasPermission: (permission: keyof User['permissions']) => boolean;
  can: (permission: BackendPermissionCode) => boolean;
  canAccessRoute: (route: string) => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  session: null,
  status: 'loading',
  error: null,
  isAuthenticating: false,

  initialize: async (queryClient) => {
    activeQueryClient = queryClient || null;
    const identityKey = (user: User | null) => user
      ? [user.id, user.professionalId, user.membershipId, user.hospitalId].join(':')
      : null;
    const clearApplicationSession = (status: AuthStatus = 'unauthenticated') => {
      queryClient?.clear();
      set({ status, user: null, session: null, error: null, isAuthenticating: false });
    };
    setSessionInvalidationHandler(() => clearApplicationSession('session-expired'));
    const { data: listener } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === 'PASSWORD_RECOVERY') {
        // A password-recovery link was just consumed: block on the reset-password
        // screen instead of resolving the application user, since the account may
        // not have completed setup yet and the person hasn't proven a new password.
        set({ status: 'password-recovery', error: null, isAuthenticating: false });
        return;
      }
      if (event === 'SIGNED_OUT' || !session) {
        clearApplicationSession(event === 'SIGNED_OUT' ? 'unauthenticated' : 'session-expired');
      } else if (event === 'TOKEN_REFRESHED') {
        void authApi.getCurrentSession().then((activeSession) => {
          if (activeSession) {
            if (identityKey(get().user) !== identityKey(activeSession.user)) queryClient?.clear();
            set({ user: activeSession.user, session: activeSession.session, status: 'authenticated', error: null });
          } else {
            clearApplicationSession('session-expired');
          }
        }).catch((err) => {
          // Surface hospital setup errors instead of silently invalidating session
          if (err instanceof AuthError && err.code === 'account-inactive') {
            clearApplicationSession('account-inactive');
          } else if (err instanceof AuthError && err.code === 'forbidden') {
            set({ error: err.message, status: 'forbidden' });
          } else {
            clearApplicationSession('session-invalid');
          }
        });
      } else if (event === 'SIGNED_IN' || event === 'INITIAL_SESSION' || event === 'USER_UPDATED') {
        queryClient?.clear();
        void authApi.getCurrentSession().then((activeSession) => {
          if (activeSession) {
            set({ user: activeSession.user, session: activeSession.session, status: 'authenticated', error: null });
          } else {
            clearApplicationSession();
          }
        }).catch((err) => {
          // Surface hospital setup errors instead of silently invalidating session
          if (err instanceof AuthError && err.code === 'account-inactive') {
            clearApplicationSession('account-inactive');
          } else if (err instanceof AuthError && err.code === 'forbidden') {
            set({ error: err.message, status: 'forbidden' });
          } else {
            clearApplicationSession('session-invalid');
          }
        });
      }
    });
    try {
      const activeSession = await authApi.getCurrentSession();
      if (activeSession) {
        set({
          user: activeSession.user,
          session: activeSession.session,
          status: 'authenticated',
          error: null,
        });
      } else {
        // No fabricated auto-login: an unauthenticated visitor sees the
        // landing/sign-in flow, not a silently-created clinician session.
        set({ status: 'unauthenticated', user: null, session: null, error: null });
        
      }
    } catch (error) {
      clearApplicationSession(error instanceof AuthError && error.code === 'account-inactive' ? 'account-inactive' : 'session-invalid');
    }
    return () => listener.subscription.unsubscribe();
  },

  login: async (credentials: LoginCredentials) => {
    set({ isAuthenticating: true, error: null });
    try {
      const { user, session } = await authApi.login(credentials);
      set({
        user,
        session,
        status: 'authenticated',
        isAuthenticating: false,
        error: null,
      });
    } catch (err: any) {
      set({
        error: err instanceof AuthError ? err.message : (err?.message || 'Authentication failed. Please verify credentials.'),
        isAuthenticating: false,
        status: err instanceof AuthError && err.code === 'account-inactive'
          ? 'account-inactive'
          : err instanceof AuthError && err.code === 'forbidden'
            ? 'forbidden'
            : 'session-invalid',
      });
      throw err;
    }
  },

  registerHospital: async (payload: HospitalRegistrationPayload) => {
    set({ isAuthenticating: true, error: null });
    try {
      const result = await authApi.registerHospital(payload);
      if (!result) {
        set({ isAuthenticating: false, status: 'unauthenticated', error: null });
        return false;
      }
      const { user, session } = result;
      set({
        user,
        session,
        status: 'authenticated',
        isAuthenticating: false,
        error: null,
      });
      return true;
    } catch (err: any) {
      set({
        error: err instanceof AuthError ? err.message : (err?.message || 'Registration failed. Please try again.'),
        isAuthenticating: false,
        status: 'unauthenticated',
      });
      throw err;
    }
  },

  logout: async () => {
    await authApi.logout();
    activeQueryClient?.clear();
    set({
      user: null,
      session: null,
      status: 'unauthenticated',
      error: null,
      isAuthenticating: false,
    });
  },

  switchRole: async (role: UserRole) => {
    void role;
    set({ isAuthenticating: false, error: 'Role changes are managed by the backend.' });
  },

  clearError: () => set({ error: null }),

  refreshUser: async () => {
    try {
      const user = await authApi.refreshApplicationUser();
      set({ user, status: 'authenticated', error: null });
    } catch (err) {
      if (err instanceof AuthError && err.code === 'account-inactive') {
        set({ status: 'account-inactive', user: null });
      }
    }
  },

  hasPermission: (permission: keyof User['permissions']) => {
    const user = get().user;
    if (!user) return false;
    return !!user.permissions[permission];
  },

  can: (permission: BackendPermissionCode) => {
    const user = get().user;
    return !!user?.permissionCodes.includes(permission);
  },

  canAccessRoute: (route: string) => {
    const user = get().user;
    if (!user) return false;

    if (route === 'admin') {
      return user.permissionCodes.includes('professionals:manage');
    }
    if (route === 'assessment') {
      return user.permissionCodes.includes('cases:create');
    }
    if (route === 'recommendation') {
      return user.permissionCodes.includes('recommendations:view');
    }
    return true; // General access for dashboard, knowledge, etc.
  },
}));

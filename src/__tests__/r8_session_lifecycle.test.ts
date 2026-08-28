import { QueryClient } from '@tanstack/react-query';

export async function runR8SessionLifecycleTests() {
  const results: { name: string; passed: boolean; details?: string }[] = [];
  const assert = (condition: boolean, name: string, details?: string) => results.push({ name, passed: condition, details: condition ? undefined : details });

  const [{ supabase }, authApiModule, clientModule, storeModule] = await Promise.all([
    import('../lib/supabase'),
    import('../api/authApi'),
    import('../api/client'),
    import('../stores/authStore'),
  ]);
  const { authApi, AuthError } = authApiModule;
  const { apiRequest, setSessionInvalidationHandler, ApiClientError } = clientModule;
  const { useAuthStore } = storeModule;

  const originalAuth = { ...supabase.auth };
  const originalFetch = globalThis.fetch;
  const session = { access_token: 'access-a', refresh_token: 'refresh-a', expires_at: 200, user: { id: 'auth-a', email: 'a@example.com' } } as Record<string, any>;
  const user = {
    id: 'auth-a',
    professionalId: 'professional-a',
    membershipId: 'membership-a',
    hospitalId: 'hospital-a',
    name: 'Ada',
    email: 'a@example.com',
    role: 'Admin',
    organization: 'Hospital A',
    department: '',
    permissions: {},
    roles: ['HOSPITAL_ADMIN'],
    permissionCodes: ['professionals:manage'],
  } as any;
  let authListener: ((event: string, session: unknown) => void) | undefined;
  let queryClient: QueryClient;
  const cleanups: Array<() => void> = [];

  const restore = () => {
    cleanups.forEach((cleanup) => cleanup());
    Object.assign(supabase.auth, originalAuth);
    globalThis.fetch = originalFetch;
    setSessionInvalidationHandler(null);
  };

  try {
    (supabase.auth as any).onAuthStateChange = (callback: typeof authListener) => {
      authListener = callback;
      return { data: { subscription: { unsubscribe: () => { authListener = undefined; } } } };
    };
    (authApi as any).getCurrentSession = async () => ({ user, session: { expiresAt: new Date(200000).toISOString(), traceSessionId: 'auth-a' } });
    (supabase.auth as any).getSession = async () => ({ data: { session }, error: null });
    queryClient = new QueryClient();
    queryClient.setQueryData(['protected'], { patient: 'private' });
    useAuthStore.setState({ user: null, session: null, status: 'loading', error: null, isAuthenticating: false });
    cleanups.push(await useAuthStore.getState().initialize(queryClient));
    assert(useAuthStore.getState().status === 'authenticated', 'R8 runtime: valid session restoration authenticates');
    assert(useAuthStore.getState().user?.id === 'auth-a', 'R8 runtime: restoration resolves backend application identity');
    assert(useAuthStore.getState().user?.professionalId === 'professional-a', '10D: professional identity comes from backend identity');
    assert(useAuthStore.getState().user?.membershipId === 'membership-a', '10D: membership identity comes from backend identity');
    assert(useAuthStore.getState().user?.hospitalId === 'hospital-a', '10D: hospital identity comes from backend identity');
    assert(useAuthStore.getState().can('professionals:manage'), 'R8 runtime: capabilities use backend permission codes');
    assert(!useAuthStore.getState().can('plugins:configure'), '10D: absent backend permission denies capability');

    cleanups.shift()?.();
    (authApi as any).getCurrentSession = async () => null;
    useAuthStore.setState({ status: 'loading', user, session: { expiresAt: new Date(200000).toISOString(), traceSessionId: 'auth-a' }, error: null, isAuthenticating: false });
    cleanups.push(await useAuthStore.getState().initialize(queryClient));
    assert(useAuthStore.getState().status === 'unauthenticated', 'R8 runtime: no provider session fails closed');

    (authApi as any).getCurrentSession = async () => ({ user, session: { expiresAt: new Date(200000).toISOString(), traceSessionId: 'auth-a' } });
    authListener?.('SIGNED_IN', session);
    await new Promise((resolve) => setTimeout(resolve, 0));
    assert(useAuthStore.getState().user?.id === 'auth-a', 'R8 runtime: SIGNED_IN resolves backend identity');

    authListener?.('SIGNED_OUT', null);
    assert(useAuthStore.getState().status === 'unauthenticated', 'R8 runtime: SIGNED_OUT clears auth state');
    assert(queryClient.getQueryData(['protected']) === undefined, 'R8 runtime: SIGNED_OUT clears protected cache');

    queryClient.setQueryData(['protected'], { patient: 'private' });
    useAuthStore.setState({ user, session: { expiresAt: new Date(200000).toISOString(), traceSessionId: 'auth-a' }, status: 'authenticated', error: null, isAuthenticating: false });
    authListener?.('TOKEN_REFRESHED', { ...session, access_token: 'access-b' });
    await new Promise((resolve) => setTimeout(resolve, 0));
    assert(useAuthStore.getState().status === 'authenticated', 'R8 runtime: TOKEN_REFRESHED preserves authenticated state');
    assert(queryClient.getQueryData(['protected']) !== undefined, 'R8 runtime: TOKEN_REFRESHED does not unnecessarily clear cache');

    queryClient.setQueryData(['identity-a'], { patient: 'private-a' });
    (authApi as any).getCurrentSession = async () => ({ user: { ...user, id: 'auth-b' }, session: { expiresAt: new Date(300000).toISOString(), traceSessionId: 'auth-b' } });
    authListener?.('SIGNED_IN', { ...session, user: { id: 'auth-b', email: 'b@example.com' } });
    assert(queryClient.getQueryData(['identity-a']) === undefined, 'R8 runtime: identity replacement clears previous protected cache');
    await new Promise((resolve) => setTimeout(resolve, 0));
    assert(useAuthStore.getState().user?.id === 'auth-b', 'R8 runtime: identity replacement adopts new backend identity');

    let refreshCalls = 0;
    let fetchCalls = 0;
    let releaseRefresh!: () => void;
    const refreshGate = new Promise<void>((resolve) => { releaseRefresh = resolve; });
    (supabase.auth as any).getSession = async () => ({ data: { session: { ...session, access_token: refreshCalls ? 'access-refreshed' : 'access-expired' } }, error: null });
    (supabase.auth as any).refreshSession = async () => {
      refreshCalls += 1;
      await refreshGate;
      return { data: { session: { ...session, access_token: 'access-refreshed' } }, error: null };
    };
    globalThis.fetch = async () => {
      fetchCalls += 1;
      if (fetchCalls <= 2) return new Response(JSON.stringify({ error: { code: 'UNAUTHORIZED', message: 'expired' } }), { status: 401 });
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    };
    const first = apiRequest('/protected');
    const second = apiRequest('/protected');
    await Promise.resolve();
    releaseRefresh();
    await Promise.all([first, second]);
    assert(refreshCalls === 1, 'R8 runtime: concurrent 401 requests share one refresh');
    assert(fetchCalls === 4, 'R8 runtime: each 401 request retries exactly once');

    let invalidations = 0;
    setSessionInvalidationHandler(() => { invalidations += 1; });
    (supabase.auth as any).refreshSession = async () => ({ data: { session: null }, error: new Error('refresh failed') });
    let failureSignOuts = 0;
    (supabase.auth as any).signOut = async () => { failureSignOuts += 1; return { error: null }; };
    globalThis.fetch = async () => new Response(JSON.stringify({ error: { code: 'UNAUTHORIZED', message: 'expired' } }), { status: 401 });
    await apiRequest('/protected').catch(() => undefined);
    assert(invalidations === 1, 'R8 runtime: refresh failure invalidates application session');
    assert(failureSignOuts === 1, 'R8 runtime: refresh failure signs out locally');

    let refreshOnForbidden = 0;
    (supabase.auth as any).refreshSession = async () => { refreshOnForbidden += 1; return { data: { session }, error: null }; };
    globalThis.fetch = async () => new Response(JSON.stringify({ error: { code: 'FORBIDDEN', message: 'denied' } }), { status: 403 });
    await apiRequest('/forbidden').catch((error) => assert(error instanceof ApiClientError && error.status === 403, 'R8 runtime: 403 remains forbidden'));
    assert(refreshOnForbidden === 0, 'R8 runtime: 403 does not refresh');

    (supabase.auth as any).signInWithPassword = async () => ({ data: { session }, error: null });
    globalThis.fetch = async () => new Response(JSON.stringify({ error: { code: 'ACCOUNT_INACTIVE', message: 'inactive' } }), { status: 403 });
    await authApi.login({ email: 'a@example.com', password: 'password' }).catch((error) => assert(error instanceof AuthError && error.code === 'account-inactive', 'R8 runtime: ACCOUNT_INACTIVE maps to account-inactive'));

    globalThis.fetch = async () => new Response(JSON.stringify({ error: { code: 'FORBIDDEN', message: 'denied' } }), { status: 403 });
    await authApi.login({ email: 'a@example.com', password: 'password' }).catch((error) => assert(error instanceof AuthError && error.code === 'forbidden', 'R8 runtime: ordinary 403 maps to forbidden'));

    queryClient.setQueryData(['protected'], { patient: 'private' });
    (authApi as any).logout = async () => undefined;
    await useAuthStore.getState().logout();
    assert(useAuthStore.getState().status === 'unauthenticated', 'R8 runtime: logout clears auth state');
    assert(queryClient.getQueryData(['protected']) === undefined, 'R8 runtime: logout clears protected cache');
  } finally {
    restore();
  }

  return results;
}

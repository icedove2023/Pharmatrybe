/// <reference types="vite/client" />

import { supabase } from '@/lib/supabase';

const viteEnv = (import.meta as ImportMeta & { env?: Record<string, string | undefined> }).env;
const LOCAL_API_BASE_URL = (viteEnv?.VITE_LOCAL_API_BASE_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '');
const VERCEL_API_BASE_URL = (viteEnv?.VITE_VERCEL_API_BASE_URL || viteEnv?.VITE_API_BASE_URL || 'https://pharmatrybe-api.vercel.app/api/v1').replace(/\/$/, '');

function resolveApiBaseUrl(): string {
  const explicitBase = (viteEnv?.VITE_API_BASE_URL || VERCEL_API_BASE_URL).trim();
  if (explicitBase) return explicitBase.replace(/\/$/, '');

  if (typeof window !== 'undefined' && /localhost|127\.0\.0\.1|0\.0\.0\.0/.test(window.location.hostname)) {
    return LOCAL_API_BASE_URL;
  }

  return VERCEL_API_BASE_URL;
}

const API_BASE_URL = resolveApiBaseUrl();

export class ApiClientError extends Error {
  status: number;
  code?: string;
  details?: unknown;

  constructor(message: string, status: number, code?: string, details?: unknown) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}
let refreshPromise: Promise<boolean> | null = null;
let sessionInvalidationHandler: (() => void) | null = null;

export function setSessionInvalidationHandler(handler: (() => void) | null): void {
  sessionInvalidationHandler = handler;
}

async function refreshSessionOnce(): Promise<boolean> {
  if (!refreshPromise) {
    refreshPromise = supabase.auth.refreshSession()
      .then(({ error }) => !error)
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

async function parseResponse(response: Response): Promise<unknown> {
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const body = payload as {
      error?: { code?: string; message?: string; details?: unknown };
      detail?: string | { code?: string; message?: string };
    } | null;
    const error = body?.error;
    const detail = typeof body?.detail === 'string' ? body.detail : body?.detail?.message;
    throw new ApiClientError(
      error?.message || detail || `Request failed with HTTP ${response.status}`,
      response.status,
      error?.code || (typeof body?.detail === 'object' ? body.detail.code : undefined),
      error?.details,
    );
  }
  return payload;
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');

  const request = async () => {
    const { data } = await supabase.auth.getSession();
    if (data.session?.access_token) headers.set('Authorization', `Bearer ${data.session.access_token}`);
    else headers.delete('Authorization');
    return fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  };
  let response = await request();
  if (response.status === 401) {
    if (await refreshSessionOnce()) {
      response = await request();
    } else {
      sessionInvalidationHandler?.();
      await supabase.auth.signOut({ scope: 'local' });
    }
  }
  return parseResponse(response) as Promise<T>;
}

export function unwrapApiData<T>(payload: { data: T }): T {
  return payload.data;
}

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}
/// <reference types="vite/client" />

import { supabase } from '@/lib/supabase';

const viteEnv = (import.meta as ImportMeta & { env?: Record<string, string | undefined> }).env;
const API_BASE_URL = (viteEnv?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '');

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
    const error = (payload as { error?: { code?: string; message?: string; details?: unknown } } | null)?.error;
    throw new ApiClientError(
      error?.message || `Request failed with HTTP ${response.status}`,
      response.status,
      error?.code,
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
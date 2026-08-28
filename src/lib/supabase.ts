import { createClient } from '@supabase/supabase-js';

const viteEnv = (import.meta as ImportMeta & { env?: Record<string, string | undefined> }).env;
const nodeEnv = typeof process !== 'undefined' ? process.env : undefined;
const supabaseUrl = viteEnv?.VITE_SUPABASE_URL || nodeEnv?.VITE_SUPABASE_URL;
const supabaseAnonKey = viteEnv?.VITE_SUPABASE_ANON_KEY || nodeEnv?.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Supabase frontend configuration is required.');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});
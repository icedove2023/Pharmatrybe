import React, { useState } from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { KeyRound, Lock } from 'lucide-react';
import { authApi, AuthError } from '@/api/authApi';
import { useAuthStore } from '@/stores/authStore';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { ClinicalButton } from '@/components/ui/ClinicalButton';

interface SetNewPasswordFormProps {
  /** 'recovery': from a forgot-password email link, no active app session yet.
   *  'forced': an authenticated user (e.g. invited with a temporary password)
   *  who must set their own password before continuing into the app. */
  mode: 'recovery' | 'forced';
  onComplete: () => void;
}

export function SetNewPasswordForm({ mode, onComplete }: SetNewPasswordFormProps) {
  const { logout, refreshUser } = useAuthStore();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const prefersReducedMotion = useReducedMotion();

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setIsSubmitting(true);
    try {
      await authApi.completePasswordReset(password);
      if (mode === 'forced') {
        await authApi.markPasswordChanged();
        await refreshUser();
      }
      onComplete();
    } catch (err) {
      setError(err instanceof AuthError ? err.message : 'Could not update the password. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <motion.div
      initial={prefersReducedMotion ? false : { opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: [0.2, 0.8, 0.2, 1] }}
      className="mx-auto w-full max-w-md space-y-4"
    >
      <div className="space-y-5 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5 shadow-xl sm:p-8">
        <div className="space-y-2 text-center">
          <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-clinical-950)] text-[var(--color-clinical-300)]">
            <KeyRound className="h-5 w-5" aria-hidden="true" />
          </div>
          <h2 className="text-xl font-semibold tracking-tight text-slate-text-primary">
            {mode === 'forced' ? 'Set your own password' : 'Choose a new password'}
          </h2>
          <p className="text-xs text-slate-text-muted">
            {mode === 'forced'
              ? 'You signed in with a temporary password. Set a permanent password to continue.'
              : 'Enter a new password for your PharmaTrybe account.'}
          </p>
        </div>

        {error && <SafetyAlert level="warning" title="Could not set password">{error}</SafetyAlert>}

        <form onSubmit={onSubmit} className="space-y-4 text-xs">
          <div className="space-y-1.5">
            <label className="block font-semibold text-slate-text-secondary">New password</label>
            <div className="relative">
              <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
              <input
                type="password"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="••••••••••••"
                className="focus-clinical w-full rounded-[var(--radius-sm)] border border-slate-border bg-slate-inset py-2.5 pl-10 pr-3.5 text-xs font-medium text-slate-text-primary placeholder-slate-text-muted"
              />
            </div>
          </div>
          <div className="space-y-1.5">
            <label className="block font-semibold text-slate-text-secondary">Confirm new password</label>
            <div className="relative">
              <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                placeholder="••••••••••••"
                className="focus-clinical w-full rounded-[var(--radius-sm)] border border-slate-border bg-slate-inset py-2.5 pl-10 pr-3.5 text-xs font-medium text-slate-text-primary placeholder-slate-text-muted"
              />
            </div>
          </div>

          <ClinicalButton type="submit" variant="primary" size="lg" icon={KeyRound} loading={isSubmitting} className="w-full">
            {isSubmitting ? 'Saving…' : 'Set password'}
          </ClinicalButton>
        </form>

        {mode === 'recovery' && (
          <button
            onClick={() => void logout()}
            className="focus-clinical block w-full text-center text-[11px] font-medium text-slate-text-muted hover:text-slate-text-primary"
          >
            Cancel and sign in a different way
          </button>
        )}
      </div>
    </motion.div>
  );
}

import React, { useState } from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { ArrowLeft, Mail, SendHorizonal } from 'lucide-react';
import { authApi, AuthError } from '@/api/authApi';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { ClinicalButton } from '@/components/ui/ClinicalButton';

interface ForgotPasswordFormProps {
  onBackToLogin: () => void;
}

export function ForgotPasswordForm({ onBackToLogin }: ForgotPasswordFormProps) {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const prefersReducedMotion = useReducedMotion();

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await authApi.requestPasswordReset(email.trim());
      setSent(true);
    } catch (err) {
      setError(err instanceof AuthError ? err.message : 'Could not send the reset email. Please try again.');
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
      <button
        onClick={onBackToLogin}
        className="focus-clinical flex items-center text-xs font-medium text-slate-text-muted hover:text-slate-text-primary"
      >
        <ArrowLeft className="mr-1 h-3.5 w-3.5" aria-hidden="true" /> Back to sign in
      </button>

      <div className="space-y-5 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5 shadow-xl sm:p-8">
        <div className="space-y-2 text-center">
          <h2 className="text-xl font-semibold tracking-tight text-slate-text-primary">Reset your password</h2>
          <p className="text-xs text-slate-text-muted">
            Enter the email address on your PharmaTrybe account and we'll send a link to reset your password.
          </p>
        </div>

        {error && <SafetyAlert level="warning" title="Could not send reset link">{error}</SafetyAlert>}
        {sent && (
          <SafetyAlert level="success" title="Check your email">
            If an account exists for <span className="font-semibold">{email.trim()}</span>, a password reset link has been sent. Follow it to choose a new password.
          </SafetyAlert>
        )}

        {!sent && (
          <form onSubmit={onSubmit} className="space-y-4 text-xs">
            <div className="space-y-1.5">
              <label className="block font-semibold text-slate-text-secondary">Hospital email</label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="you@yourhospital.org"
                  className="focus-clinical w-full rounded-[var(--radius-sm)] border border-slate-border bg-slate-inset py-2.5 pl-10 pr-3.5 text-xs font-medium text-slate-text-primary placeholder-slate-text-muted"
                />
              </div>
            </div>

            <ClinicalButton type="submit" variant="primary" size="lg" icon={SendHorizonal} loading={isSubmitting} className="w-full">
              {isSubmitting ? 'Sending link…' : 'Send reset link'}
            </ClinicalButton>
          </form>
        )}
      </div>
    </motion.div>
  );
}

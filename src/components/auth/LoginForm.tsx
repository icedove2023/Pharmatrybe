import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion, useReducedMotion } from 'motion/react';
import { loginSchema, LoginCredentials } from '@/types/auth';
import { useAuthStore } from '@/stores/authStore';
import {
  Lock, Mail, Eye, EyeOff, ArrowLeft,
} from 'lucide-react';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { ClinicalButton } from '@/components/ui/ClinicalButton';

interface LoginFormProps {
  onSuccess?: () => void;
  onBackToLanding: () => void;
  onSwitchToRegister: () => void;
}

export function LoginForm({ onSuccess, onBackToLanding, onSwitchToRegister }: LoginFormProps) {
  const { login, isAuthenticating, error, clearError } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const prefersReducedMotion = useReducedMotion();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginCredentials>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '', rememberMe: true },
  });

  const onSubmit = async (data: LoginCredentials) => {
    clearError();
    try {
      await login(data);
      onSuccess?.();
    } catch {
      // Error surfaced via store state
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
        onClick={onBackToLanding}
        className="focus-clinical flex items-center text-xs font-medium text-slate-text-muted hover:text-slate-text-primary"
      >
        <ArrowLeft className="mr-1 h-3.5 w-3.5" aria-hidden="true" /> Back
      </button>

      <div className="space-y-5 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5 shadow-xl sm:p-8">
        <div className="space-y-2 text-center">
          <h2 className="text-xl font-semibold tracking-tight text-slate-text-primary">Sign in to PharmaTrybe</h2>
          <p className="text-xs text-slate-text-muted">
            For administrators and hospital staff with a provisioned account.
          </p>
        </div>

        {error && <SafetyAlert level="warning" title="Sign-in error">{error}</SafetyAlert>}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 text-xs">
          <div className="space-y-1.5">
            <label className="block font-semibold text-slate-text-secondary">Hospital email</label>
            <div className="relative">
              <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
              <input
                {...register('email')}
                type="email"
                placeholder="you@yourhospital.org"
                className={`focus-clinical w-full rounded-[var(--radius-sm)] border bg-slate-inset py-2.5 pl-10 pr-3.5 text-xs font-medium text-slate-text-primary placeholder-slate-text-muted ${
                  errors.email ? 'border-[var(--color-safety-critical)]' : 'border-slate-border'
                }`}
              />
            </div>
            {errors.email && <p className="pl-1 text-[11px] font-medium text-[var(--color-safety-critical)]">{errors.email.message}</p>}
          </div>

          <div className="space-y-1.5">
            <label className="block font-semibold text-slate-text-secondary">Password</label>
            <div className="relative">
              <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
              <input
                {...register('password')}
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••••••"
                className={`focus-clinical w-full rounded-[var(--radius-sm)] border bg-slate-inset py-2.5 pl-10 pr-10 text-xs font-medium text-slate-text-primary placeholder-slate-text-muted ${
                  errors.password ? 'border-[var(--color-safety-critical)]' : 'border-slate-border'
                }`}
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                className="focus-clinical absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-text-muted hover:text-slate-text-primary"
              >
                {showPassword ? <EyeOff className="h-4 w-4" aria-hidden="true" /> : <Eye className="h-4 w-4" aria-hidden="true" />}
              </button>
            </div>
            {errors.password && <p className="pl-1 text-[11px] font-medium text-[var(--color-safety-critical)]">{errors.password.message}</p>}
          </div>

          <label className="flex items-center space-x-2 pt-1 text-[11px] text-slate-text-secondary">
            <input type="checkbox" {...register('rememberMe')} className="h-3.5 w-3.5 rounded text-[var(--color-clinical-500)]" />
            <span>Remember this workstation</span>
          </label>

          <ClinicalButton type="submit" variant="primary" size="lg" icon={Lock} loading={isAuthenticating} className="w-full">
            {isAuthenticating ? 'Verifying credentials…' : 'Sign in'}
          </ClinicalButton>
        </form>

        <p className="text-center text-[11px] text-slate-text-muted">
          New hospital?{' '}
          <button onClick={onSwitchToRegister} className="focus-clinical font-semibold text-[var(--color-clinical-500)] hover:underline">
            Register your institution
          </button>
        </p>
      </div>
    </motion.div>
  );
}

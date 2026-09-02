import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion, useReducedMotion } from 'motion/react';
import {
  Building2, User, Mail, Lock, Eye, EyeOff, ArrowLeft, ShieldCheck, Phone, CreditCard,
} from 'lucide-react';
import { hospitalRegistrationSchema, HospitalRegistrationPayload } from '@/types/auth';
import { useAuthStore } from '@/stores/authStore';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { ClinicalButton } from '@/components/ui/ClinicalButton';

interface HospitalRegistrationFormProps {
  onSuccess?: () => void;
  onBackToLanding: () => void;
  onSwitchToSignIn: () => void;
}

const INPUT_CLASSES =
  'focus-clinical w-full rounded-[var(--radius-sm)] border bg-slate-inset py-2.5 pl-10 pr-3.5 text-xs font-medium text-slate-text-primary placeholder-slate-text-muted';

export function HospitalRegistrationForm({ onSuccess, onBackToLanding, onSwitchToSignIn }: HospitalRegistrationFormProps) {
  const { registerHospital, isAuthenticating, error, clearError } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const [verificationPending, setVerificationPending] = useState(false);
  const [verificationEmail, setVerificationEmail] = useState('');
  const prefersReducedMotion = useReducedMotion();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<HospitalRegistrationPayload>({
    resolver: zodResolver(hospitalRegistrationSchema),
    defaultValues: { hospitalName: '', country: '', adminName: '', adminEmail: '', adminPhone: '', adminProfessionalNumber: '', password: '', confirmPassword: '', acceptTerms: undefined },
  });

  const onSubmit = async (data: HospitalRegistrationPayload) => {
    clearError();
    try {
      const completed = await registerHospital(data);
      if (completed) onSuccess?.();
      else {
        setVerificationEmail(data.adminEmail);
        setVerificationPending(true);
      }
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
          <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-clinical-950)] text-[var(--color-clinical-300)]">
            <Building2 className="h-5 w-5" aria-hidden="true" />
          </div>
          <h2 className="text-xl font-semibold tracking-tight text-slate-text-primary">Register your hospital</h2>
          <p className="text-xs text-slate-text-muted">
            Creates your institution's workspace. You'll become the first administrator and can invite clinicians
            and staff afterward.
          </p>
        </div>

        {verificationPending ? (
          <SafetyAlert level="success" title="Check your email">
            We sent a verification link to {verificationEmail}. Open it, then return here and sign in to finish creating your hospital workspace.
          </SafetyAlert>
        ) : error && <SafetyAlert level="warning" title="Registration error">{error}</SafetyAlert>}

        {!verificationPending && <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 text-xs">
          <div className="space-y-1.5">
            <label className="block font-semibold text-slate-text-secondary">Hospital / institution name</label>
            <div className="relative">
              <Building2 className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
              <input {...register('hospitalName')} type="text" placeholder="St. Jude's Clinical Research Hospital" className={`${INPUT_CLASSES} ${errors.hospitalName ? 'border-[var(--color-safety-critical)]' : 'border-slate-border'}`} />
            </div>
            {errors.hospitalName && <p className="pl-1 text-[11px] font-medium text-[var(--color-safety-critical)]">{errors.hospitalName.message}</p>}
          </div>

          <div className="space-y-1.5">
            <label className="block font-semibold text-slate-text-secondary">Country</label>
            <input {...register('country')} type="text" placeholder="Nigeria" className={`focus-clinical w-full rounded-[var(--radius-sm)] border bg-slate-inset px-3.5 py-2.5 text-xs font-medium text-slate-text-primary placeholder-slate-text-muted ${errors.country ? 'border-[var(--color-safety-critical)]' : 'border-slate-border'}`} />
            {errors.country && <p className="pl-1 text-[11px] font-medium text-[var(--color-safety-critical)]">{errors.country.message}</p>}
          </div>

          <div className="space-y-1.5 border-t border-slate-border-subtle pt-4">
            <label className="block font-semibold text-slate-text-secondary">Your full name (first administrator)</label>
            <div className="relative">
              <User className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
              <input {...register('adminName')} type="text" placeholder="Pharm. Jane Okoye" className={`${INPUT_CLASSES} ${errors.adminName ? 'border-[var(--color-safety-critical)]' : 'border-slate-border'}`} />
            </div>
            {errors.adminName && <p className="pl-1 text-[11px] font-medium text-[var(--color-safety-critical)]">{errors.adminName.message}</p>}
          </div>

          <div className="space-y-1.5">
            <label className="block font-semibold text-slate-text-secondary">Work email</label>
            <div className="relative">
              <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
              <input {...register('adminEmail')} type="email" placeholder="admin@yourhospital.org" className={`${INPUT_CLASSES} ${errors.adminEmail ? 'border-[var(--color-safety-critical)]' : 'border-slate-border'}`} />
            </div>
            {errors.adminEmail && <p className="pl-1 text-[11px] font-medium text-[var(--color-safety-critical)]">{errors.adminEmail.message}</p>}
          </div>

          <div className="space-y-1.5">
            <label className="block font-semibold text-slate-text-secondary">Phone number</label>
            <div className="relative">
              <Phone className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
              <input {...register('adminPhone')} type="tel" placeholder="+234 805 000 0000" className={`${INPUT_CLASSES} ${errors.adminPhone ? 'border-[var(--color-safety-critical)]' : 'border-slate-border'}`} />
            </div>
            {errors.adminPhone && <p className="pl-1 text-[11px] font-medium text-[var(--color-safety-critical)]">{errors.adminPhone.message}</p>}
          </div>

          <div className="space-y-1.5">
            <label className="block font-semibold text-slate-text-secondary">Professional registration / license number</label>
            <div className="relative">
              <CreditCard className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
              <input {...register('adminProfessionalNumber')} type="text" placeholder="License or registration number" className={`${INPUT_CLASSES} ${errors.adminProfessionalNumber ? 'border-[var(--color-safety-critical)]' : 'border-slate-border'}`} />
            </div>
            {errors.adminProfessionalNumber && <p className="pl-1 text-[11px] font-medium text-[var(--color-safety-critical)]">{errors.adminProfessionalNumber.message}</p>}
          </div>

          <div className="space-y-1.5">
            <label className="block font-semibold text-slate-text-secondary">Password</label>
            <div className="relative">
              <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
              <input {...register('password')} type={showPassword ? 'text' : 'password'} placeholder="At least 8 characters" className={`${INPUT_CLASSES} pr-10 ${errors.password ? 'border-[var(--color-safety-critical)]' : 'border-slate-border'}`} />
              <button type="button" onClick={() => setShowPassword((v) => !v)} className="focus-clinical absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-text-muted hover:text-slate-text-primary">
                {showPassword ? <EyeOff className="h-4 w-4" aria-hidden="true" /> : <Eye className="h-4 w-4" aria-hidden="true" />}
              </button>
            </div>
            {errors.password && <p className="pl-1 text-[11px] font-medium text-[var(--color-safety-critical)]">{errors.password.message}</p>}
          </div>

          <div className="space-y-1.5">
            <label className="block font-semibold text-slate-text-secondary">Confirm password</label>
            <div className="relative">
              <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
              <input {...register('confirmPassword')} type={showPassword ? 'text' : 'password'} placeholder="Re-enter password" className={`${INPUT_CLASSES} ${errors.confirmPassword ? 'border-[var(--color-safety-critical)]' : 'border-slate-border'}`} />
            </div>
            {errors.confirmPassword && <p className="pl-1 text-[11px] font-medium text-[var(--color-safety-critical)]">{errors.confirmPassword.message}</p>}
          </div>

          <label className="flex items-start space-x-2.5 pt-1 text-[11px] text-slate-text-secondary">
            <input {...register('acceptTerms')} type="checkbox" className="mt-0.5 h-3.5 w-3.5 rounded text-[var(--color-clinical-500)]" />
            <span>
              I confirm I'm authorized to register this institution and accept responsibility for provisioning and
              managing staff accounts within PharmaTrybe.
            </span>
          </label>
          {errors.acceptTerms && <p className="pl-1 text-[11px] font-medium text-[var(--color-safety-critical)]">{errors.acceptTerms.message}</p>}

          <ClinicalButton type="submit" variant="primary" size="lg" icon={ShieldCheck} loading={isAuthenticating} className="w-full">
            {isAuthenticating ? 'Creating workspace…' : 'Create hospital workspace'}
          </ClinicalButton>
        </form>}

        <p className="text-center text-[11px] text-slate-text-muted">
          Already registered?{' '}
          <button onClick={onSwitchToSignIn} className="focus-clinical font-semibold text-[var(--color-clinical-500)] hover:underline">
            Sign in instead
          </button>
        </p>
      </div>
    </motion.div>
  );
}

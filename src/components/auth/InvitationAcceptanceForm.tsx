import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Building2, Lock, Mail, UserCheck } from 'lucide-react';
import { z } from 'zod';
import { supabase } from '@/lib/supabase';
import { professionalsApi } from '@/api/professionalsApi';
import { useAuthStore } from '@/stores/authStore';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { ClinicalButton } from '@/components/ui/ClinicalButton';

const invitationSchema = z.object({
  email: z.string().email('Enter a valid invited email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  firstName: z.string().min(1, 'First name is required'),
  lastName: z.string().min(1, 'Last name is required'),
  professionalType: z.string().optional(),
});

type InvitationFormValues = z.infer<typeof invitationSchema>;

interface InvitationAcceptanceFormProps {
  token: string;
}

export function InvitationAcceptanceForm({ token: _token }: InvitationAcceptanceFormProps) {
  const user = useAuthStore((state) => state.user);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<InvitationFormValues>({
    resolver: zodResolver(invitationSchema),
    defaultValues: { email: user?.email || '', password: '', firstName: '', lastName: '', professionalType: '' },
  });

  const onSubmit = async (values: InvitationFormValues) => {
    setError(null);
    setMessage(null);
    try {
      const { data: sessionData } = await supabase.auth.getSession();
      const activeUser = user || sessionData.session?.user;
      if (!activeUser) throw new Error('Authentication is required to accept this invitation.');
      if (!user) {
        const { error: passwordError } = await supabase.auth.updateUser({ password: values.password });
        if (passwordError) throw passwordError;
      }
      await professionalsApi.acceptInvitation({
        first_name: values.firstName,
        last_name: values.lastName,
        professional_type: values.professionalType || undefined,
      });
      setMessage('Your hospital membership is active. You can now sign in to PharmaTrybe.');
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Invitation acceptance failed.');
    }
  };

  return (
    <div className="mx-auto w-full max-w-md space-y-5 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5 shadow-xl sm:p-8">
      <div className="space-y-2 text-center">
        <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-clinical-950)] text-[var(--color-clinical-300)]"><Building2 className="h-5 w-5" aria-hidden="true" /></div>
        <h1 className="text-xl font-semibold text-slate-text-primary">Join your hospital</h1>
        <p className="text-xs text-slate-text-muted">Accept the invitation using the email address it was sent to.</p>
      </div>
      {message && <SafetyAlert level="success" title="Invitation update">{message}</SafetyAlert>}
      {error && <SafetyAlert level="warning" title="Invitation error">{error}</SafetyAlert>}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 text-xs">
        {!user && <div><label className="font-semibold text-slate-text-secondary">Invited email</label><div className="relative mt-1"><Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" /><input {...register('email')} type="email" className="w-full rounded-md border border-slate-border bg-slate-inset py-2.5 pl-10 pr-3 text-slate-text-primary" /></div>{errors.email && <p className="text-[11px] text-[var(--color-safety-critical)]">{errors.email.message}</p>}</div>}
        {!user && <div><label className="font-semibold text-slate-text-secondary">Create password</label><div className="relative mt-1"><Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" /><input {...register('password')} type="password" className="w-full rounded-md border border-slate-border bg-slate-inset py-2.5 pl-10 pr-3 text-slate-text-primary" /></div>{errors.password && <p className="text-[11px] text-[var(--color-safety-critical)]">{errors.password.message}</p>}</div>}
        <div className="grid grid-cols-2 gap-3"><label className="font-semibold text-slate-text-secondary">First name<input {...register('firstName')} className="mt-1 w-full rounded-md border border-slate-border bg-slate-inset px-3 py-2.5 text-slate-text-primary" />{errors.firstName && <p className="text-[11px] text-[var(--color-safety-critical)]">{errors.firstName.message}</p>}</label><label className="font-semibold text-slate-text-secondary">Last name<input {...register('lastName')} className="mt-1 w-full rounded-md border border-slate-border bg-slate-inset px-3 py-2.5 text-slate-text-primary" />{errors.lastName && <p className="text-[11px] text-[var(--color-safety-critical)]">{errors.lastName.message}</p>}</label></div>
        <label className="font-semibold text-slate-text-secondary">Professional type<span className="block mt-1 text-[11px] font-normal text-slate-text-muted">Optional, for example Pharmacist or Laboratory Scientist</span><input {...register('professionalType')} className="mt-1 w-full rounded-md border border-slate-border bg-slate-inset px-3 py-2.5 text-slate-text-primary" /></label>
        <ClinicalButton type="submit" variant="primary" size="lg" icon={UserCheck} loading={isSubmitting} className="w-full">Accept invitation</ClinicalButton>
      </form>
    </div>
  );
}
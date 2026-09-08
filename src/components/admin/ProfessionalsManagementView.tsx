import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Clock3, Copy, Check, KeyRound, MailPlus, RefreshCw, ShieldCheck, Users } from 'lucide-react';
import { professionalsApi, CANONICAL_ROLES, CanonicalRoleCode } from '@/api/professionalsApi';
import { ClinicalButton } from '@/components/ui/ClinicalButton';
import { SafetyAlert } from '@/components/ui/SafetyAlert';

export function ProfessionalsManagementView() {
  const queryClient = useQueryClient();
  const professionals = useQuery({ queryKey: ['professionals'], queryFn: professionalsApi.list });
  const invitations = useQuery({ queryKey: ['professional-invitations'], queryFn: professionalsApi.listInvitations });
  const [email, setEmail] = useState('');
  const [roleCode, setRoleCode] = useState<CanonicalRoleCode>('CLINICIAN');
  const [success, setSuccess] = useState<string | null>(null);
  const [invitedCredential, setInvitedCredential] = useState<{ email: string; temporaryPassword: string } | null>(null);
  const [copied, setCopied] = useState(false);
  const invite = useMutation({
    mutationFn: () => professionalsApi.invite(email.trim().toLowerCase(), roleCode),
    onSuccess: (result) => {
      const invitedEmail = email.trim().toLowerCase();
      setSuccess(`Invitation created for ${invitedEmail} with the ${result.role_code} role.`);
      setInvitedCredential({ email: invitedEmail, temporaryPassword: result.temporary_password });
      setCopied(false);
      setEmail('');
      void queryClient.invalidateQueries({ queryKey: ['professional-invitations'] });
    },
  });
  const membership = useMutation({
    mutationFn: ({ professionalId, status, role_code }: { professionalId: string; status?: 'ACTIVE' | 'SUSPENDED' | 'DEACTIVATED'; role_code?: CanonicalRoleCode }) => professionalsApi.updateMembership(professionalId, { status, role_code }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['professionals'] });
      setSuccess('Professional membership updated.');
    },
  });

  return (
    <div className="space-y-6" id="admin-professionals">
      <div className="flex flex-col justify-between gap-4 rounded-lg border border-[var(--color-safety-info-border)] bg-gradient-to-r from-blue-50 to-slate-50 p-6 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center gap-2"><Users className="h-5 w-5 text-[var(--color-safety-info)]" aria-hidden="true" /><h1 className="text-xl font-semibold text-slate-text-primary">Professionals</h1><span className="rounded-full border border-[var(--color-safety-info-border)] bg-white px-2 py-0.5 text-[10px] font-semibold text-[var(--color-safety-info)]">Admin only</span></div>
          <p className="mt-1 max-w-2xl text-xs text-slate-text-secondary">Invite professionals into this hospital. Role assignment and membership activation remain server-authoritative.</p>
        </div>
        <div className="flex items-center gap-2 text-[11px] font-medium text-slate-text-secondary"><ShieldCheck className="h-4 w-4 text-[var(--color-safety-success)]" />Hospital-scoped access</div>
      </div>

      {success && <SafetyAlert level="success" title="Invitation created"><p>{success}</p><p className="mt-1 text-[11px]">Delivery is queued by the backend. The invitation token is never displayed in the browser.</p></SafetyAlert>}

      {invitedCredential && (
        <div className="rounded-lg border border-[var(--color-safety-warning-border)] bg-[var(--color-safety-warning-bg)] p-5">
          <div className="flex items-start gap-3">
            <KeyRound className="mt-0.5 h-5 w-5 shrink-0 text-[var(--color-safety-warning)]" aria-hidden="true" />
            <div className="min-w-0 flex-1">
              <h3 className="text-sm font-semibold text-slate-text-primary">Temporary password — shown once</h3>
              <p className="mt-1 text-xs text-slate-text-secondary">
                Share this with <span className="font-semibold">{invitedCredential.email}</span> through a secure channel (not email in plain text, unless you've configured Supabase's invite email template to include it automatically — see note below). They'll sign in at the normal login page with this password and be required to set their own immediately.
              </p>
              <div className="mt-3 flex items-center gap-2">
                <code className="num-clinical flex-1 truncate rounded-md border border-slate-border bg-white px-3 py-2 text-xs font-semibold text-slate-text-primary">
                  {invitedCredential.temporaryPassword}
                </code>
                <ClinicalButton
                  type="button"
                  variant="secondary"
                  size="sm"
                  icon={copied ? Check : Copy}
                  onClick={() => {
                    void navigator.clipboard.writeText(invitedCredential.temporaryPassword);
                    setCopied(true);
                    setTimeout(() => setCopied(false), 2000);
                  }}
                >
                  {copied ? 'Copied' : 'Copy'}
                </ClinicalButton>
              </div>
              <p className="mt-2 text-[11px] text-slate-text-muted">
                This password will not be shown again after you leave this page. If lost, an admin can trigger a password reset instead.
              </p>
            </div>
          </div>
        </div>
      )}

      {(invite.isError || membership.isError) && <SafetyAlert level="critical" title="RBAC action could not be completed">{((invite.error || membership.error) as Error).message}</SafetyAlert>}

      <section className="rounded-lg border border-slate-border bg-white p-6">
        <div className="flex items-start gap-3 border-b border-slate-border pb-4"><MailPlus className="mt-0.5 h-5 w-5 text-[var(--color-safety-info)]" aria-hidden="true" /><div><h2 className="text-base font-semibold text-slate-text-primary">Invite a professional</h2><p className="mt-1 text-xs text-slate-text-muted">The recipient must authenticate with the invited email before accepting membership.</p></div></div>
        <form className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2" onSubmit={(event) => { event.preventDefault(); setSuccess(null); invite.mutate(); }}>
          <label className="text-xs font-semibold text-slate-text-secondary">Professional email<input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="name@hospital.org" className="mt-1 w-full rounded-md border border-slate-border px-3 py-2 text-xs font-normal text-slate-text-primary focus:border-[var(--color-safety-info-border)] focus:outline-none focus:ring-2 focus:ring-[var(--color-safety-info-border)]" /></label>
          <label className="text-xs font-semibold text-slate-text-secondary">Role<select value={roleCode} onChange={(event) => setRoleCode(event.target.value as CanonicalRoleCode)} className="mt-1 w-full rounded-md border border-slate-border bg-white px-3 py-2 text-xs font-normal text-slate-text-primary focus:border-[var(--color-safety-info-border)] focus:outline-none focus:ring-2 focus:ring-[var(--color-safety-info-border)]">{CANONICAL_ROLES.map((role) => <option key={role.code} value={role.code}>{role.label}</option>)}</select></label>
          <div className="md:col-span-2 flex items-start gap-2 rounded-md border border-slate-border bg-slate-inset p-3 text-[11px] text-slate-text-secondary"><Clock3 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-text-muted" /><span>Invitations expire according to the backend policy. Duplicate pending invitations are rejected by the server.</span></div>
          <div className="md:col-span-2 flex justify-end"><ClinicalButton type="submit" variant="primary" icon={MailPlus} loading={invite.isPending}>Send invitation</ClinicalButton></div>
        </form>
      </section>

      <section className="rounded-lg border border-slate-border bg-white p-6">
        <div className="flex items-center justify-between gap-3"><div><h2 className="text-sm font-semibold text-slate-text-primary">Professional directory</h2><p className="mt-1 text-xs text-slate-text-secondary">Hospital-scoped members and their backend-derived roles.</p></div><ClinicalButton variant="ghost" size="sm" icon={RefreshCw} loading={professionals.isFetching} onClick={() => void professionals.refetch()}>Refresh</ClinicalButton></div>
        {professionals.isError ? <p className="mt-4 rounded-md border border-[var(--color-safety-critical-border)] bg-[var(--color-safety-critical-bg)] p-3 text-xs text-[var(--color-safety-critical)]">{(professionals.error as Error).message}</p> : professionals.isLoading ? <p className="mt-4 text-xs text-slate-text-muted">Loading professionals...</p> : professionals.data?.length ? <div className="mt-4 overflow-x-auto"><table className="w-full min-w-[640px] text-left text-xs"><thead className="border-b border-slate-border text-[10px] uppercase tracking-wide text-slate-text-muted"><tr><th className="px-3 py-2">Professional</th><th className="px-3 py-2">Type</th><th className="px-3 py-2">Roles</th><th className="px-3 py-2">Membership</th><th className="px-3 py-2">Actions</th></tr></thead><tbody className="divide-y divide-slate-border">{professionals.data.map((professional) => <tr key={professional.professional_id}><td className="px-3 py-3 font-semibold text-slate-text-primary">{professional.first_name} {professional.last_name}</td><td className="px-3 py-3 text-slate-text-secondary">{professional.professional_type || 'Not reported'}</td><td className="px-3 py-3 text-slate-text-secondary">{professional.roles.join(', ') || 'No role reported'}</td><td className="px-3 py-3"><span className="rounded-full border border-slate-border bg-slate-inset px-2 py-1 text-[10px] font-semibold text-slate-text-secondary">{professional.membership_status}</span></td><td className="px-3 py-3"><div className="flex flex-wrap gap-1.5"><select aria-label={`Change membership status for ${professional.first_name} ${professional.last_name}`} value={professional.membership_status} onChange={(event) => membership.mutate({ professionalId: professional.professional_id, status: event.target.value as 'ACTIVE' | 'SUSPENDED' | 'DEACTIVATED' })} className="rounded border border-slate-border px-2 py-1 text-[10px] text-slate-text-secondary"><option value="ACTIVE">Active</option><option value="SUSPENDED">Suspend</option><option value="DEACTIVATED">Deactivate</option></select><select aria-label={`Assign role for ${professional.first_name} ${professional.last_name}`} value={professional.roles[0] || ''} onChange={(event) => membership.mutate({ professionalId: professional.professional_id, role_code: event.target.value as CanonicalRoleCode })} className="rounded border border-slate-border px-2 py-1 text-[10px] text-slate-text-secondary"><option value="" disabled>Assign role</option>{CANONICAL_ROLES.map((role) => <option key={role.code} value={role.code}>{role.label}</option>)}</select></div></td></tr>)}</tbody></table></div> : <p className="mt-4 rounded-md border border-dashed border-slate-border bg-slate-inset p-6 text-center text-xs text-slate-text-muted">No professional memberships found for this hospital.</p>}
      </section>

      <section className="rounded-lg border border-slate-border bg-white p-6">
        <h2 className="text-sm font-semibold text-slate-text-primary">Invitation activity</h2>
        <p className="mt-1 text-xs text-slate-text-secondary">Token material is never returned to or displayed by the frontend.</p>
        {invitations.isError ? <p className="mt-4 rounded-md border border-[var(--color-safety-critical-border)] bg-[var(--color-safety-critical-bg)] p-3 text-xs text-[var(--color-safety-critical)]">{(invitations.error as Error).message}</p> : invitations.isLoading ? <p className="mt-4 text-xs text-slate-text-muted">Loading invitations...</p> : invitations.data?.length ? <div className="mt-4 space-y-2">{invitations.data.map((invitation) => <div key={invitation.invitation_id} className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-slate-border bg-slate-inset p-3 text-xs"><span className="font-semibold text-slate-text-primary">{invitation.email}</span><span className="text-slate-text-secondary">{invitation.role_code}</span><span className="rounded-full border border-slate-border bg-white px-2 py-1 text-[10px] font-semibold text-slate-text-secondary">{invitation.status}</span><span className="text-[10px] text-slate-text-muted">Expires {new Date(invitation.expires_at).toLocaleDateString()}</span></div>)}</div> : <p className="mt-4 rounded-md border border-dashed border-slate-border bg-slate-inset p-6 text-center text-xs text-slate-text-muted">No invitations found for this hospital.</p>}
      </section>
    </div>
  );
}

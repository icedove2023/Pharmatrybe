import React from 'react';
import { Building2, Cake, IdCard, Mail, Phone, Settings, ShieldCheck, UserCircle2 } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { RoleBadge } from '@/components/auth/RoleBadge';
import { ClinicalButton } from '@/components/ui/ClinicalButton';

interface ProfileViewProps {
  onNavigateTab?: (tab: string) => void;
}

function InfoRow({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start gap-3 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3.5">
      <Icon className="mt-0.5 h-4 w-4 shrink-0 text-slate-text-muted" aria-hidden="true" />
      <div className="min-w-0">
        <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-text-muted">{label}</p>
        <p className="truncate text-xs font-semibold text-slate-text-primary">{value}</p>
      </div>
    </div>
  );
}

export function ProfileView({ onNavigateTab }: ProfileViewProps) {
  const { user } = useAuthStore();

  if (!user) return null;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex flex-col justify-between gap-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6 md:flex-row md:items-center">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-clinical-700)] text-lg font-bold text-white">
            {user.name.split(' ').map((n) => n[0]).join('')}
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-text-primary">{user.name}</h2>
            <p className="text-xs text-slate-text-muted">{user.email}</p>
            <div className="mt-1"><RoleBadge role={user.role} size="sm" /></div>
          </div>
        </div>
        {onNavigateTab && (
          <ClinicalButton variant="secondary" size="md" icon={Settings} onClick={() => onNavigateTab('settings')} className="shrink-0">
            Edit in Settings
          </ClinicalButton>
        )}
      </div>

      <div className="space-y-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6">
        <h3 className="flex items-center text-sm font-semibold text-slate-text-primary">
          <UserCircle2 className="mr-2 h-4 w-4 text-[var(--color-clinical-400)]" aria-hidden="true" />
          Profile information
        </h3>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <InfoRow icon={Building2} label="Hospital / institution" value={user.organization} />
          <InfoRow icon={ShieldCheck} label="Role" value={user.role} />
          <InfoRow icon={IdCard} label="Professional type" value={user.department || 'Not set'} />
          <InfoRow icon={IdCard} label="Professional / license number" value={user.licenseNumber || 'Not set'} />
          <InfoRow icon={Cake} label="Age" value={typeof user.age === 'number' ? `${user.age} years` : 'Not set'} />
          <InfoRow icon={Phone} label="Phone" value={user.phone || 'Not set'} />
          <InfoRow icon={Mail} label="Email" value={user.email} />
          <InfoRow
            icon={UserCircle2}
            label="Member since"
            value={user.memberSince ? new Date(user.memberSince).toLocaleDateString() : 'Not set'}
          />
        </div>
        <p className="text-[11px] text-slate-text-muted">
          To update any of these details, or to change your password, go to Settings.
        </p>
      </div>
    </div>
  );
}

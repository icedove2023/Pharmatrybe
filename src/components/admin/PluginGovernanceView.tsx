import React, { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { CheckCircle2, ChevronRight, FileUp, Lock, RefreshCw, Shield, ShieldAlert, Upload, X } from 'lucide-react';
import { pluginGovernanceApi, GovernanceStatus, PluginGovernanceRecord } from '@/api/pluginGovernanceApi';
import { useAuthStore } from '@/stores/authStore';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { ClinicalButton } from '@/components/ui/ClinicalButton';
import { cn } from '@/lib/utils';

const statusOrder: GovernanceStatus[] = ['REGISTERED', 'VALIDATING', 'VALIDATED', 'PENDING_APPROVAL', 'APPROVED', 'ACTIVE'];
const statusLabel: Record<string, string> = {
  REGISTERED: 'Registered',
  PENDING_VALIDATION: 'Pending validation',
  SUBMITTED: 'Submitted',
  VALIDATING: 'Validating',
  VALIDATED: 'Validated',
  PENDING_APPROVAL: 'Pending approval',
  APPROVED: 'Approved',
  ACTIVE: 'Active',
  DISABLED: 'Disabled',
  REJECTED: 'Rejected',
  REVOKED: 'Revoked',
  QUARANTINED: 'Quarantined',
};

function statusTone(status: string): string {
  if (status === 'ACTIVE' || status === 'APPROVED' || status === 'VALIDATED') return 'text-[var(--color-safety-success)] bg-[var(--color-safety-success-bg)] border-[var(--color-safety-success-border)]';
  if (status === 'REJECTED' || status === 'REVOKED' || status === 'QUARANTINED') return 'text-[var(--color-safety-critical)] bg-[var(--color-safety-critical-bg)] border-[var(--color-safety-critical-border)]';
  return 'text-[var(--color-safety-warning)] bg-[var(--color-safety-warning-bg)] border-[var(--color-safety-warning-border)]';
}

function canAction(record: PluginGovernanceRecord, action: string): boolean {
  const status = record.status;
  if (action === 'validate') return ['REGISTERED', 'PENDING_VALIDATION', 'PENDING_APPROVAL'].includes(status);
  if (action === 'approve') return status === 'VALIDATED';
  if (action === 'activate') return status === 'APPROVED';
  if (action === 'deactivate') return status === 'ACTIVE';
  if (action === 'reject') return ['REGISTERED', 'PENDING_VALIDATION', 'VALIDATED', 'PENDING_APPROVAL'].includes(status);
  if (action === 'quarantine') return ['ACTIVE', 'DISABLED', 'APPROVED'].includes(status);
  if (action === 'revoke') return ['ACTIVE', 'DISABLED', 'APPROVED'].includes(status);
  return false;
}

function Lifecycle({ status }: { status: string }) {
  const terminal = ['DISABLED', 'REJECTED', 'REVOKED', 'QUARANTINED'].includes(status);
  return (
    <div className="flex flex-wrap items-center gap-1.5" aria-label={`Plugin lifecycle: ${statusLabel[status] || status}`}>
      {statusOrder.map((step, index) => {
        const currentIndex = statusOrder.indexOf(status as GovernanceStatus);
        const complete = currentIndex >= index;
        return (
          <React.Fragment key={step}>
            <span className={cn('inline-flex items-center gap-1 rounded-full border px-2 py-1 text-[10px] font-semibold', complete ? 'border-[var(--color-safety-info-border)] bg-[var(--color-safety-info-bg)] text-[var(--color-safety-info)]' : 'border-slate-border bg-slate-inset text-slate-text-muted')}>
              {complete && <CheckCircle2 className="h-3 w-3" aria-hidden="true" />}
              {statusLabel[step]}
            </span>
            {index < statusOrder.length - 1 && <ChevronRight className="h-3 w-3 text-slate-text-secondary" aria-hidden="true" />}
          </React.Fragment>
        );
      })}
      {terminal && <span className={cn('rounded-full border px-2 py-1 text-[10px] font-semibold', statusTone(status))}>{statusLabel[status] || status}</span>}
    </div>
  );
}

interface UploadFormProps { onClose: () => void; onComplete: () => void; }
function UploadForm({ onClose, onComplete }: UploadFormProps) {
  const [form, setForm] = useState({ pluginId: '', pluginName: '', pluginType: 'prediction' as 'knowledge' | 'prediction', pluginVersion: '', owner: '', publisher: '' });
  const [artifact, setArtifact] = useState<File | null>(null);
  const upload = useMutation({
    mutationFn: () => {
      if (!artifact) throw new Error('Select a plugin ZIP archive.');
      return pluginGovernanceApi.upload({ ...form, artifact });
    },
    onSuccess: () => { onComplete(); onClose(); },
  });
  const update = (key: keyof typeof form, value: string) => setForm((current) => ({ ...current, [key]: value }));
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-inset/35 p-4" role="dialog" aria-modal="true" aria-labelledby="upload-plugin-title">
      <form onSubmit={(event) => { event.preventDefault(); upload.mutate(); }} className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-lg border border-slate-border bg-white p-6 shadow-2xl">
        <div className="flex items-start justify-between gap-4 border-b border-slate-border pb-4">
          <div><p className="text-[10px] font-semibold uppercase tracking-wide text-[var(--color-safety-info)]">Plugin governance</p><h2 id="upload-plugin-title" className="mt-1 text-lg font-semibold text-slate-text-primary">Upload plugin package</h2><p className="mt-1 text-xs text-slate-text-muted">The server inspects the archive, calculates its hash, validates the manifest, and assigns the hospital registration.</p></div>
          <button type="button" onClick={onClose} aria-label="Close upload dialog" className="rounded-md p-1.5 text-slate-text-muted hover:bg-slate-inset-hover"><X className="h-5 w-5" /></button>
        </div>
        <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
          {([['pluginId', 'Plugin ID'], ['pluginName', 'Plugin name'], ['pluginVersion', 'Version'], ['owner', 'Owner'], ['publisher', 'Publisher']] as const).map(([key, label]) => (
            <label key={key} className="text-xs font-semibold text-slate-text-secondary">{label}<input required value={form[key]} onChange={(event) => update(key, event.target.value)} className="mt-1 w-full rounded-md border border-slate-border px-3 py-2 text-xs font-normal text-slate-text-primary focus:border-[var(--color-safety-info-border)] focus:outline-none focus:ring-2 focus:ring-[var(--color-safety-info-border)]" /></label>
          ))}
          <label className="text-xs font-semibold text-slate-text-secondary">Plugin category<select value={form.pluginType} onChange={(event) => update('pluginType', event.target.value)} className="mt-1 w-full rounded-md border border-slate-border px-3 py-2 text-xs font-normal text-slate-text-primary focus:border-[var(--color-safety-info-border)] focus:outline-none focus:ring-2 focus:ring-[var(--color-safety-info-border)]"><option value="prediction">Prediction</option><option value="knowledge">Knowledge</option></select></label>
          <label className="sm:col-span-2 text-xs font-semibold text-slate-text-secondary">Plugin ZIP archive<input required type="file" accept=".zip,application/zip" onChange={(event) => setArtifact(event.target.files?.[0] || null)} className="mt-1 block w-full rounded-md border border-dashed border-slate-border bg-slate-inset px-3 py-3 text-xs font-normal text-slate-text-secondary" /></label>
        </div>
        {upload.isError && <SafetyAlert level="critical" title="Plugin upload failed">{(upload.error as Error).message}</SafetyAlert>}
        <div className="mt-6 flex justify-end gap-2 border-t border-slate-border pt-4"><ClinicalButton type="button" variant="ghost" onClick={onClose}>Cancel</ClinicalButton><ClinicalButton type="submit" variant="primary" loading={upload.isPending} icon={Upload}>Submit for validation</ClinicalButton></div>
      </form>
    </div>
  );
}

export function PluginGovernanceView() {
  const can = useAuthStore((state) => state.can);
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [showUpload, setShowUpload] = useState(false);
  const records = useQuery({ queryKey: ['plugin-governance'], queryFn: pluginGovernanceApi.list });
  const details = useQuery({ queryKey: ['plugin-governance', selectedId], queryFn: () => pluginGovernanceApi.get(selectedId as string), enabled: Boolean(selectedId) });
  const action = useMutation({ mutationFn: ({ pluginId, name }: { pluginId: string; name: Parameters<typeof pluginGovernanceApi.action>[1] }) => pluginGovernanceApi.action(pluginId, name), onSuccess: () => { void queryClient.invalidateQueries({ queryKey: ['plugin-governance'] }); } });
  const filtered = useMemo(() => (records.data || []).filter((record) => `${record.plugin_name} ${record.plugin_id} ${record.plugin_type}`.toLowerCase().includes(query.toLowerCase())), [records.data, query]);

  if (!can('plugins:configure')) return <SafetyAlert level="critical" title="Access restricted">Plugin governance is available only to authorized hospital administrators.</SafetyAlert>;
  return (
    <div className="space-y-6" id="plugin-governance">
      <div className="flex flex-col justify-between gap-4 rounded-lg border border-[var(--color-safety-info-border)] bg-gradient-to-r from-blue-50 to-slate-50 p-6 sm:flex-row sm:items-center">
        <div><div className="flex items-center gap-2"><Shield className="h-5 w-5 text-[var(--color-safety-info)]" /><h1 className="text-xl font-semibold text-slate-text-primary">Plugin governance</h1><span className="rounded-full border border-[var(--color-safety-info-border)] bg-white px-2 py-0.5 text-[10px] font-semibold text-[var(--color-safety-info)]">Admin only</span></div><p className="mt-1 max-w-2xl text-xs text-slate-text-secondary">Register, validate, approve, activate, monitor, and control hospital-scoped plugin packages.</p></div>
        <ClinicalButton variant="primary" icon={FileUp} onClick={() => setShowUpload(true)}>Upload plugin</ClinicalButton>
      </div>
      <div className="flex flex-col gap-3 sm:flex-row"><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search plugin name, ID, or category" className="min-w-0 flex-1 rounded-md border border-slate-border bg-white px-3 py-2 text-xs text-slate-text-primary focus:border-[var(--color-safety-info-border)] focus:outline-none focus:ring-2 focus:ring-[var(--color-safety-info-border)]" /><ClinicalButton variant="outline" icon={RefreshCw} loading={records.isFetching} onClick={() => void records.refetch()}>Refresh registry</ClinicalButton></div>
      {records.isError && <SafetyAlert level="critical" title="Plugin registry unavailable">{(records.error as Error).message}</SafetyAlert>}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <section className="space-y-2 lg:col-span-5"><div className="flex items-center justify-between px-1"><h2 className="text-xs font-semibold uppercase tracking-wide text-slate-text-muted">Hospital registrations</h2><span className="text-[11px] text-slate-text-muted">{filtered.length} shown</span></div>{records.isLoading ? <div className="rounded-lg border border-slate-border bg-white p-8 text-center text-xs text-slate-text-muted">Loading governed plugins...</div> : filtered.length === 0 ? <div className="rounded-lg border border-slate-border bg-white p-8 text-center text-xs text-slate-text-muted">No governed plugin registrations found.</div> : filtered.map((record) => <button type="button" key={record.plugin_id} onClick={() => setSelectedId(record.plugin_id)} className={cn('w-full rounded-lg border bg-white p-4 text-left transition-colors hover:border-[var(--color-safety-info-border)]', selectedId === record.plugin_id ? 'border-[var(--color-safety-info-border)] ring-2 ring-[var(--color-safety-info-border)]' : 'border-slate-border')}><div className="flex items-start justify-between gap-3"><div><h3 className="text-sm font-semibold text-slate-text-primary">{record.plugin_name}</h3><p className="mt-1 text-[11px] text-slate-text-muted">{record.plugin_id} · {record.plugin_type}</p></div><span className={cn('rounded-full border px-2 py-1 text-[10px] font-semibold', statusTone(record.status))}>{statusLabel[record.status] || record.status}</span></div><div className="mt-3 flex items-center justify-between border-t border-slate-border pt-2 text-[10px] text-slate-text-muted"><span>v{record.plugin_version}</span><span>{record.validation_state || 'Validation state unavailable'}</span></div></button>)}</section>
        <section className="lg:col-span-7">{details.isLoading && <div className="rounded-lg border border-slate-border bg-white p-8 text-center text-xs text-slate-text-muted">Loading plugin details...</div>}{details.isError && <SafetyAlert level="critical" title="Plugin details unavailable">{(details.error as Error).message}</SafetyAlert>}{details.data && <div className="space-y-5 rounded-lg border border-slate-border bg-white p-6"><div className="flex items-start justify-between gap-4 border-b border-slate-border pb-4"><div><p className="text-[10px] font-semibold uppercase tracking-wide text-[var(--color-safety-info)]">Governed registration</p><h2 className="mt-1 text-lg font-semibold text-slate-text-primary">{details.data.plugin_name}</h2><p className="mt-1 text-xs text-slate-text-muted">{details.data.plugin_id} · {details.data.plugin_type} · v{details.data.plugin_version}</p></div><span className={cn('rounded-full border px-2.5 py-1 text-xs font-semibold', statusTone(details.data.status))}>{statusLabel[details.data.status] || details.data.status}</span></div><Lifecycle status={details.data.status} /><div className="grid grid-cols-2 gap-3 text-xs sm:grid-cols-4"><div><p className="text-[10px] uppercase text-slate-text-muted">Validation</p><p className="mt-1 font-semibold text-slate-text-primary">{details.data.validation_state || 'Not reported'}</p></div><div><p className="text-[10px] uppercase text-slate-text-muted">Approval</p><p className="mt-1 font-semibold text-slate-text-primary">{details.data.approval_state || 'Not reported'}</p></div><div><p className="text-[10px] uppercase text-slate-text-muted">Trust</p><p className="mt-1 font-semibold text-slate-text-primary">{details.data.trust_level || 'Not reported'}</p></div><div><p className="text-[10px] uppercase text-slate-text-muted">Hospital</p><p className="mt-1 truncate font-semibold text-slate-text-primary" title={details.data.hospital_id}>{details.data.hospital_id || 'Server scoped'}</p></div></div><div><p className="text-[10px] font-semibold uppercase tracking-wide text-slate-text-muted">Capabilities</p><div className="mt-2 flex flex-wrap gap-1.5">{(details.data.capabilities || []).length ? details.data.capabilities?.map((capability) => <span key={capability} className="rounded border border-slate-border bg-slate-inset px-2 py-1 text-[10px] text-slate-text-secondary">{capability}</span>) : <span className="text-xs text-slate-text-muted">No capabilities reported.</span>}</div></div><div className="flex flex-wrap gap-2 border-t border-slate-border pt-4">{(['validate', 'approve', 'activate', 'deactivate', 'reject', 'quarantine', 'revoke'] as const).map((name) => canAction(details.data!, name) && <ClinicalButton key={name} variant={['reject', 'quarantine', 'revoke'].includes(name) ? 'destructive' : 'outline'} size="sm" disabled={action.isPending} onClick={() => action.mutate({ pluginId: details.data!.plugin_id, name })}>{name === 'deactivate' ? 'Disable' : name.charAt(0).toUpperCase() + name.slice(1)}</ClinicalButton>)}</div>{action.isError && <p className="rounded-md border border-[var(--color-safety-critical-border)] bg-[var(--color-safety-critical-bg)] p-3 text-xs text-[var(--color-safety-critical)]">{(action.error as Error).message}</p>}<div className="border-t border-slate-border pt-4"><div className="flex items-center gap-2"><Lock className="h-4 w-4 text-slate-text-muted" /><h3 className="text-xs font-semibold text-slate-text-primary">Immutable governance history</h3></div>{(details.data.audit_events || []).length ? <div className="mt-3 space-y-2">{details.data.audit_events?.map((event, index) => <div key={`${event.action}-${index}`} className="flex justify-between gap-3 rounded-md bg-slate-inset p-3 text-[11px]"><span className="font-semibold text-slate-text-secondary">{event.action}</span><time className="text-slate-text-muted">{new Date(event.created_at).toLocaleString()}</time></div>)}</div> : <p className="mt-2 text-xs text-slate-text-muted">No audit events reported by the backend.</p>}</div></div>}</section>
      </div>
      {showUpload && <UploadForm onClose={() => setShowUpload(false)} onComplete={() => void queryClient.invalidateQueries({ queryKey: ['plugin-governance'] })} />}
    </div>
  );
}

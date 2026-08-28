import React from 'react';
import {
  Stethoscope, CheckCircle2, ChevronRight, Layers, Sparkles, Database,
} from 'lucide-react';
import { ClinicalButton } from '@/components/ui/ClinicalButton';
import { getExternalRegisteredPlugins } from '@/plugins/registry/pluginRegistry';
import { NotificationHistory } from '@/components/common/NotificationCenter';

interface DashboardViewProps {
  onNavigateTab: (tab: string) => void;
}

export function DashboardView({ onNavigateTab }: DashboardViewProps) {
  let recentCasesCount = 0;
  const registeredPluginsCount = getExternalRegisteredPlugins().length;

  return (
    <div className="space-y-6">
      {/* Primary Action — New Case Assessment is the first thing a clinician sees */}
      <div className="flex flex-col justify-between gap-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5 sm:flex-row sm:items-center">
        <div>
          <h2 className="text-lg font-semibold text-slate-text-primary">Clinical dashboard</h2>
          <p className="text-xs text-slate-text-muted">
            {recentCasesCount} recent case{recentCasesCount === 1 ? '' : 's'} · start a new assessment when ready
          </p>
        </div>
        <div className="flex items-center gap-2">
          <ClinicalButton variant="primary" size="md" icon={Sparkles} onClick={() => onNavigateTab('assessment')}>
            New Assessment
          </ClinicalButton>
        </div>
      </div>

      {/* Compact workload metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <button
          type="button"
          onClick={() => onNavigateTab('patients')}
          className="focus-clinical flex items-center justify-between rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-4 text-left transition-colors hover:border-[var(--color-clinical-700)]"
        >
          <div>
            <p className="num-clinical text-xl font-bold text-slate-text-primary">{recentCasesCount}</p>
            <p className="text-[11px] font-medium text-slate-text-muted">Recent case assessments</p>
          </div>
          <Stethoscope className="h-5 w-5 text-[var(--color-clinical-400)]" aria-hidden="true" />
        </button>

        <div className="flex items-center justify-between rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-4">
          <div>
            <p className="num-clinical text-xl font-bold text-slate-text-primary">Access ≥60%</p>
            <p className="text-[11px] font-medium text-slate-text-muted">WHO stewardship target</p>
          </div>
          <CheckCircle2 className="h-5 w-5 text-[var(--color-safety-success)]" aria-hidden="true" />
        </div>

        <button
          type="button"
          onClick={() => onNavigateTab('telemetry')}
          className="focus-clinical flex items-center justify-between rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-4 text-left transition-colors hover:border-[var(--color-clinical-700)]"
        >
          <div>
            <p className="num-clinical text-xl font-bold text-slate-text-primary">{registeredPluginsCount}</p>
            <p className="text-[11px] font-medium text-slate-text-muted">Registered plugins</p>
          </div>
          <Database className="h-5 w-5 text-[var(--color-clinical-400)]" aria-hidden="true" />
        </button>
      </div>

      {/* Recent Prescribing & Clinical Audit Trail */}
      <div className="rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Layers className="h-4 w-4 text-[var(--color-clinical-400)]" aria-hidden="true" />
            <div>
              <h3 className="text-xs font-semibold text-slate-text-primary">Clinical prescribing & audit trail</h3>
              <p className="text-[11px] text-slate-text-muted">Recent case recommendations and clinician review activity</p>
            </div>
          </div>
          <button
            onClick={() => onNavigateTab('patients')}
            className="focus-clinical flex items-center text-xs font-semibold text-[var(--color-clinical-400)] hover:underline"
          >
            <span>View full directory</span>
            <ChevronRight className="ml-1 h-3.5 w-3.5" aria-hidden="true" />
          </button>
        </div>

        <div className="rounded-[var(--radius-md)] border border-dashed border-slate-border p-6 text-center text-xs text-slate-text-muted">
          No recent activity. New case assessments will appear here.
        </div>
      </div>

      <NotificationHistory />
    </div>
  );
}

import React from 'react';
import { AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react';
import { ClinicalWarning } from '@/types';
import { SafetyAlert, SafetyLevel } from '@/components/ui/SafetyAlert';

interface ClinicalWarningsPanelProps {
  warnings: ClinicalWarning[];
}

function severityToLevel(severity: ClinicalWarning['severity']): SafetyLevel {
  if (severity === 'High') return 'critical';
  if (severity === 'Medium') return 'warning';
  return 'info';
}

export function ClinicalWarningsPanel({ warnings }: ClinicalWarningsPanelProps) {
  return (
    <div className="space-y-3 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5">
      <div className="flex items-center justify-between border-b border-slate-border-subtle pb-2">
        <div className="flex items-center space-x-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--color-safety-warning-bg)] text-[var(--color-safety-warning)]">
            <ShieldAlert className="h-4 w-4" aria-hidden="true" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-text-primary">Clinical warnings & safety alerts</h3>
            <p className="text-[11px] text-slate-text-muted">From backend clinical risk & rules evaluation</p>
          </div>
        </div>
        <span className="num-clinical rounded-[var(--radius-xs)] bg-slate-inset px-2 py-0.5 text-[10px] text-slate-text-muted">
          {warnings.length} active {warnings.length === 1 ? 'alert' : 'alerts'}
        </span>
      </div>

      {warnings.length === 0 ? (
        <SafetyAlert level="success" title="No active safety warnings for this candidate">
          The backend returned no triggered clinical risk rules for the current prescription candidate.
        </SafetyAlert>
      ) : (
        <div className="space-y-2.5">
          {warnings.map((w) => (
            <div key={w.id}>
              <SafetyAlert
                level={severityToLevel(w.severity)}
                eyebrow={`${w.severity} severity`}
                title={w.title}
              >
                <p className="text-[11.5px] leading-relaxed">{w.details}</p>
                {w.ruleSource && (
                  <span className="num-clinical mt-1.5 inline-block rounded-[var(--radius-xs)] border border-current/20 bg-black/15 px-2 py-0.5 text-[10px] opacity-80">
                    Source: {w.ruleSource}
                  </span>
                )}
              </SafetyAlert>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

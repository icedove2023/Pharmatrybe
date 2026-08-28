import React from 'react';
import { Layers, CheckCircle2, AlertTriangle, Ban, HelpCircle } from 'lucide-react';
import { ExplainabilityDriver } from '@/types';
import { StatusBadge, BadgeTone } from '@/components/ui/StatusBadge';
import { cn } from '@/lib/utils';

interface EvidenceRankingPanelProps {
  drivers?: ExplainabilityDriver[];
}

function impactConfig(impact: string): { tone: BadgeTone; icon: React.ElementType } {
  const norm = (impact || '').toLowerCase();
  if (norm.includes('support') || norm.includes('positive')) return { tone: 'success', icon: CheckCircle2 };
  if (norm.includes('caution') || norm.includes('restrict')) return { tone: 'warning', icon: AlertTriangle };
  if (norm.includes('contraindicate') || norm.includes('negative')) return { tone: 'critical', icon: Ban };
  return { tone: 'neutral', icon: HelpCircle };
}

function sourceDotColor(source: string) {
  const s = (source || '').toLowerCase();
  if (s.includes('who') || s.includes('guideline')) return 'bg-[var(--color-clinical-400)]';
  if (s.includes('surveillance') || s.includes('soar')) return 'bg-[var(--color-safety-success-bg)]';
  if (s.includes('prediction') || s.includes('armd') || s.includes('engine')) return 'bg-[var(--color-safety-info-bg)]';
  if (s.includes('rule') || s.includes('clinical')) return 'bg-[var(--color-safety-warning-bg)]';
  if (s.includes('stewardship') || s.includes('policy')) return 'bg-[var(--color-safety-success-bg)]';
  return 'bg-[var(--color-clinical-400)]';
}

export function EvidenceRankingPanel({ drivers }: EvidenceRankingPanelProps) {
  if (!drivers || drivers.length === 0) {
    return (
      <div className="space-y-3 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6">
        <div className="flex items-center space-x-2">
          <Layers className="h-4 w-4 text-[var(--color-clinical-400)]" aria-hidden="true" />
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-text-secondary">Ranked evidence drivers</h3>
        </div>
        <div className="rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-4 text-xs italic text-slate-text-muted">
          No ranked evidence drivers returned by the CDSS backend for this case.
        </div>
      </div>
    );
  }

  const sortedDrivers = [...drivers].sort((a, b) => (b.weight || 0) - (a.weight || 0));

  return (
    <div className="space-y-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-border-subtle pb-3">
        <div className="flex items-center space-x-2">
          <Layers className="h-4 w-4 text-[var(--color-clinical-400)]" aria-hidden="true" />
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-text-primary">Ranked evidence drivers</h3>
        </div>
        <span className="num-clinical rounded-[var(--radius-sm)] border border-slate-border-subtle bg-slate-inset px-2 py-0.5 text-[10px] text-slate-text-muted">
          {sortedDrivers.length} drivers, sorted by weight
        </span>
      </div>

      <div className="grid grid-cols-1 gap-3.5 md:grid-cols-2">
        {sortedDrivers.map((driver, idx) => {
          const cfg = impactConfig(driver.impact);
          return (
            <div
              key={`${driver.source}-${idx}`}
              className="space-y-2.5 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-4 transition-colors duration-[var(--duration-fast)] hover:border-[var(--color-clinical-700)]"
            >
              <div className="flex items-center justify-between gap-2">
                <span className="flex items-center text-xs font-semibold text-slate-text-primary">
                  <span className={cn('mr-2 h-2 w-2 shrink-0 rounded-full', sourceDotColor(driver.source))} />
                  <span>{driver.source}</span>
                </span>
                <StatusBadge tone={cfg.tone} icon={cfg.icon}>
                  {driver.impact}{typeof driver.weight === 'number' ? ` (${Math.round(driver.weight * 100)}%)` : ''}
                </StatusBadge>
              </div>

              <p className="text-xs leading-relaxed text-slate-text-secondary">{driver.evidence}</p>

              <div className="flex items-center justify-between border-t border-slate-border-subtle pt-2 text-[10px] text-slate-text-muted">
                <span>
                  {driver.affected_drug ? (
                    <span>Target regimen: <strong className="font-medium text-slate-text-secondary">{driver.affected_drug}</strong></span>
                  ) : (
                    <span>General safety / guideline criterion</span>
                  )}
                </span>
                {typeof driver.weight === 'number' && (
                  <span className="num-clinical font-semibold text-slate-text-secondary">Weight: {driver.weight.toFixed(2)}</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

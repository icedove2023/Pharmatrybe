import React, { useState } from 'react';
import {
  ShieldCheck, AlertTriangle, AlertOctagon, CheckCircle2, Info, ChevronDown, ChevronUp,
} from 'lucide-react';
import { ClinicalRuleResult } from '@/types';
import { StatusBadge, BadgeTone } from '@/components/ui/StatusBadge';
import { cn } from '@/lib/utils';

interface ClinicalSafetyMatrixProps {
  rules: ClinicalRuleResult[];
}

type FilterStatus = 'ALL' | 'TRIGGERED_ONLY' | 'PASSED_ONLY';

const STATUS_CONFIG: Record<ClinicalRuleResult['status'], { tone: BadgeTone; icon: React.ElementType; label: string }> = {
  PASSED: { tone: 'success', icon: CheckCircle2, label: 'Passed' },
  TRIGGERED: { tone: 'critical', icon: AlertOctagon, label: 'Triggered' },
  WARNING: { tone: 'warning', icon: AlertTriangle, label: 'Warning' },
  NOT_EVALUATED: { tone: 'neutral', icon: Info, label: 'Not evaluated' },
} as any;

const SEVERITY_TONE: Record<ClinicalRuleResult['severity'], BadgeTone> = {
  CRITICAL: 'critical',
  HIGH: 'warning',
  MEDIUM: 'warning',
  LOW: 'neutral',
} as any;

export function ClinicalSafetyMatrix({ rules }: ClinicalSafetyMatrixProps) {
  const [filter, setFilter] = useState<FilterStatus>('ALL');
  const [expandedRuleIds, setExpandedRuleIds] = useState<Record<string, boolean>>({});

  const toggleExpand = (ruleId: string) => {
    setExpandedRuleIds((prev) => ({ ...prev, [ruleId]: !prev[ruleId] }));
  };

  const filteredRules = rules.filter((r) => {
    if (filter === 'TRIGGERED_ONLY') return r.status === 'TRIGGERED' || r.status === 'WARNING';
    if (filter === 'PASSED_ONLY') return r.status === 'PASSED';
    return true;
  });

  const triggeredCount = rules.filter((r) => r.status === 'TRIGGERED' || r.status === 'WARNING').length;
  const passedCount = rules.filter((r) => r.status === 'PASSED').length;

  return (
    <div className="space-y-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5">
      {/* Header with Title & Filter Controls */}
      <div className="flex flex-col justify-between gap-3 border-b border-slate-border-subtle pb-3 sm:flex-row sm:items-center">
        <div className="flex items-center space-x-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--color-safety-success-bg)] text-[var(--color-safety-success)]">
            <ShieldCheck className="h-4 w-4" aria-hidden="true" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-text-primary">Clinical safety rules evaluation</h3>
            <p className="text-[11px] text-slate-text-muted">Deterministic safety evaluation (inbuilt Clinical Rules Engine)</p>
          </div>
        </div>

        {/* Filter Toggle Pills */}
        <div role="tablist" aria-label="Filter safety rules" className="flex items-center space-x-1 self-start rounded-[var(--radius-md)] bg-slate-inset p-1 text-xs font-semibold sm:self-auto">
          <button
            role="tab"
            aria-selected={filter === 'ALL'}
            onClick={() => setFilter('ALL')}
            className={cn(
              'focus-clinical rounded-[var(--radius-sm)] px-3 py-1 transition-colors duration-[var(--duration-fast)]',
              filter === 'ALL' ? 'bg-slate-surface text-slate-text-primary' : 'text-slate-text-muted hover:text-slate-text-primary',
            )}
          >
            All ({rules.length})
          </button>
          <button
            role="tab"
            aria-selected={filter === 'TRIGGERED_ONLY'}
            onClick={() => setFilter('TRIGGERED_ONLY')}
            className={cn(
              'focus-clinical flex items-center space-x-1 rounded-[var(--radius-sm)] px-3 py-1 transition-colors duration-[var(--duration-fast)]',
              filter === 'TRIGGERED_ONLY' ? 'bg-[var(--color-safety-critical)] text-white' : 'text-slate-text-muted hover:text-slate-text-primary',
            )}
          >
            <span>Triggered / warnings</span>
            {triggeredCount > 0 && (
              <span className="ml-1 rounded-full bg-white/90 px-1.5 py-0.2 text-[10px] font-bold text-[var(--color-safety-critical)]">
                {triggeredCount}
              </span>
            )}
          </button>
          <button
            role="tab"
            aria-selected={filter === 'PASSED_ONLY'}
            onClick={() => setFilter('PASSED_ONLY')}
            className={cn(
              'focus-clinical rounded-[var(--radius-sm)] px-3 py-1 transition-colors duration-[var(--duration-fast)]',
              filter === 'PASSED_ONLY' ? 'bg-slate-surface text-[var(--color-safety-success)]' : 'text-slate-text-muted hover:text-slate-text-primary',
            )}
          >
            Passed ({passedCount})
          </button>
        </div>
      </div>

      {/* Matrix List */}
      {filteredRules.length === 0 ? (
        <div className="rounded-[var(--radius-md)] border border-dashed border-slate-border p-8 text-center text-xs text-slate-text-muted">
          No clinical safety rules match the selected filter.
        </div>
      ) : (
        <div className="space-y-2.5">
          {filteredRules.map((rule) => {
            const isExpanded = !!expandedRuleIds[rule.rule_id];
            const isTriggered = rule.status === 'TRIGGERED' || rule.status === 'WARNING';
            const statusCfg = STATUS_CONFIG[rule.status] ?? STATUS_CONFIG.NOT_EVALUATED;
            const borderTone = isTriggered
              ? rule.severity === 'CRITICAL' || rule.severity === 'HIGH'
                ? 'border-[var(--color-safety-critical-border)] bg-[var(--color-safety-critical-bg)]/40'
                : 'border-[var(--color-safety-warning-border)] bg-[var(--color-safety-warning-bg)]/40'
              : 'border-slate-border-subtle bg-slate-inset';

            return (
              <div key={rule.rule_id} className={cn('rounded-[var(--radius-md)] border', borderTone)}>
                <button
                  type="button"
                  onClick={() => toggleExpand(rule.rule_id)}
                  aria-expanded={isExpanded}
                  className="focus-clinical flex w-full flex-col gap-3 p-3.5 text-left md:flex-row md:items-center md:justify-between"
                >
                  <div className="flex items-start space-x-3 sm:items-center">
                    <div className="mt-0.5 shrink-0 sm:mt-0">
                      <StatusBadge tone={statusCfg.tone} icon={statusCfg.icon}>{statusCfg.label}</StatusBadge>
                    </div>
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-semibold text-slate-text-primary">{rule.rule_name} safety rule</span>
                        <span className="num-clinical rounded border border-slate-border-subtle bg-slate-canvas px-1.5 py-0.5 text-[10px] text-slate-text-muted">
                          {rule.rule_id}
                        </span>
                        <StatusBadge tone={SEVERITY_TONE[rule.severity] ?? 'neutral'}>{rule.severity}</StatusBadge>
                      </div>
                      <p className="mt-1 text-xs leading-snug text-slate-text-secondary">{rule.message}</p>
                    </div>
                  </div>

                  <div className="flex shrink-0 items-center justify-between space-x-3 border-t border-slate-border-subtle pt-2 md:justify-end md:border-t-0 md:pt-0">
                    {rule.affected_drugs && rule.affected_drugs.length > 0 && (
                      <div className="flex items-center space-x-1 text-[11px] text-slate-text-muted">
                        <span className="font-medium">Affected:</span>
                        <span className="num-clinical rounded border border-slate-border-subtle bg-slate-canvas px-2 py-0.5 text-[10px] text-slate-text-secondary">
                          {rule.affected_drugs.join(', ')}
                        </span>
                      </div>
                    )}
                    {isExpanded ? <ChevronUp className="h-4 w-4 text-slate-text-muted" aria-hidden="true" /> : <ChevronDown className="h-4 w-4 text-slate-text-muted" aria-hidden="true" />}
                  </div>
                </button>

                {isExpanded && (
                  <div className="space-y-2 border-t border-slate-border-subtle px-4 pb-3.5 pt-2.5 text-xs">
                    {rule.dosage_notes || rule.adjustment_notes ? (
                      <div>
                        <span className="mb-0.5 block font-semibold text-slate-text-primary">
                          Actionable clinical guidance & dosage notes
                        </span>
                        <p className="num-clinical rounded-[var(--radius-sm)] bg-slate-canvas p-2.5 text-[11px] text-slate-text-secondary">
                          {rule.dosage_notes || rule.adjustment_notes}
                        </p>
                      </div>
                    ) : (
                      <p className="text-[11px] italic text-slate-text-muted">
                        No supplementary dose adjustment notes required for this rule evaluation.
                      </p>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

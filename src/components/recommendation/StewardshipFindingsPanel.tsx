import React from 'react';
import { ShieldCheck, AlertCircle, FileCheck, CheckCircle2 } from 'lucide-react';
import { StewardshipFinding } from '@/types';

interface StewardshipFindingsPanelProps {
  findings: StewardshipFinding[];
}

export function StewardshipFindingsPanel({ findings }: StewardshipFindingsPanelProps) {
  if (!findings || findings.length === 0) {
    return (
      <div className="p-5 rounded-[var(--radius-lg)] bg-slate-surface border border-slate-border space-y-2">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-4 h-4 text-[var(--color-safety-success)]" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-text-primary">
            Antimicrobial Stewardship Policy & Formulary Guidance
          </h3>
        </div>
        <p className="text-xs text-slate-text-muted italic p-3 bg-slate-inset rounded-[var(--radius-md)] border border-slate-border-subtle">
          No stewardship findings recorded.
        </p>
      </div>
    );
  }

  return (
    <div className="p-5 rounded-[var(--radius-lg)] bg-slate-surface border border-slate-border space-y-4">
      <div className="flex items-center justify-between border-b border-slate-border-subtle pb-3">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-4 h-4 text-[var(--color-safety-success)]" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-text-primary">
            Antimicrobial Stewardship Policy & Formulary Evaluation
          </h3>
        </div>
        <span className="text-[10px] num-clinical text-slate-text-muted bg-slate-inset px-2 py-0.5 rounded border border-slate-border-subtle">
          Engine: pt-stewardship-v1.0
        </span>
      </div>

      <div className="space-y-3">
        {findings.map((f, idx) => (
          <div
            key={`${f.title || f.category}-${idx}`}
            className="p-4 rounded-[var(--radius-md)] bg-slate-inset border border-slate-border-subtle space-y-2.5"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="font-semibold text-xs text-slate-text-primary">
                {f.title || 'Stewardship Recommendation'}
              </span>
              {f.score !== undefined && (
                <span className="text-[11px] num-clinical font-semibold text-[var(--color-safety-success)] bg-[var(--color-safety-success-bg)] px-2 py-0.5 rounded border border-[var(--color-safety-success-border)]">
                  Stewardship Score: {f.score}/100
                </span>
              )}
            </div>

            {f.finding && (
              <p className="text-xs text-slate-text-secondary">
                {f.finding}
              </p>
            )}

            {f.notes && f.notes.length > 0 && (
              <ul className="space-y-1.5 pt-1">
                {f.notes.map((note, noteIdx) => (
                  <li key={noteIdx} className="text-xs text-slate-text-secondary flex items-start space-x-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[var(--color-safety-success)] shrink-0 mt-0.5" />
                    <span>{note}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

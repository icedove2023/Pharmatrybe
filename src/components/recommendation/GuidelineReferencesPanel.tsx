import React from 'react';
import { BookOpen, ExternalLink, ShieldCheck, AlertTriangle } from 'lucide-react';
import { GuidelineReference } from '@/types';

interface GuidelineReferencesPanelProps {
  references: GuidelineReference[];
}

export function GuidelineReferencesPanel({ references }: GuidelineReferencesPanelProps) {
  if (!references || references.length === 0) {
    return (
      <div className="p-5 rounded-[var(--radius-lg)] bg-slate-surface border border-slate-border space-y-2">
        <div className="flex items-center space-x-2">
          <BookOpen className="w-4 h-4 text-[var(--color-safety-success)]" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-text-primary">
            Authoritative Guideline Concordance
          </h3>
        </div>
        <p className="text-xs text-slate-text-muted italic p-3 bg-slate-inset rounded-[var(--radius-md)] border border-slate-border-subtle">
          No guideline references recorded.
        </p>
      </div>
    );
  }

  return (
    <div className="p-5 rounded-[var(--radius-lg)] bg-slate-surface border border-slate-border space-y-4">
      <div className="flex items-center justify-between border-b border-slate-border-subtle pb-3">
        <div className="flex items-center space-x-2">
          <BookOpen className="w-4 h-4 text-[var(--color-safety-success)]" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-text-primary">
            Authoritative Clinical Guidelines & Evidence Concordance
          </h3>
        </div>
        <span className="text-[10px] num-clinical text-slate-text-muted bg-slate-inset px-2 py-0.5 rounded border border-slate-border-subtle">
          {references.length} Sources Evaluated
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {references.map((ref, idx) => (
          <div
            key={`${ref.guideline_name}-${idx}`}
            className="p-3.5 rounded-[var(--radius-md)] bg-slate-inset border border-slate-border-subtle space-y-2 flex flex-col justify-between"
          >
            <div className="space-y-1.5">
              <div className="flex items-start justify-between gap-2">
                <span className="font-semibold text-xs text-slate-text-primary leading-snug">
                  {ref.guideline_name}
                </span>
                {ref.evidence_level && (
                  <span className="shrink-0 px-2 py-0.5 text-[10px] font-semibold rounded bg-[var(--color-safety-success-bg)] text-[var(--color-safety-success)] border border-[var(--color-safety-success-border)]">
                    Level {ref.evidence_level}
                  </span>
                )}
              </div>

              {ref.recommendations && (
                <p className="text-xs text-slate-text-secondary leading-relaxed font-sans">
                  {ref.recommendations}
                </p>
              )}

              {ref.contraindications && ref.contraindications.length > 0 && (
                <div className="pt-1 text-[11px] text-[var(--color-safety-critical)] flex items-center space-x-1">
                  <AlertTriangle className="w-3 h-3 shrink-0" />
                  <span>Contraindications: {ref.contraindications.join(', ')}</span>
                </div>
              )}
            </div>

            {ref.url && (
              <div className="pt-2 border-t border-slate-border-subtle">
                <a
                  href={ref.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-[11px] text-[var(--color-clinical-400)] hover:underline flex items-center space-x-1"
                >
                  <span>View Official Guideline Documentation</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

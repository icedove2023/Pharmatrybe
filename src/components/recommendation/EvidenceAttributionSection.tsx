import React from 'react';
import { GitCommit, Cpu, Database, BookOpen, Layers } from 'lucide-react';
import { EvidenceAttribution } from '@/types';

interface EvidenceAttributionSectionProps {
  evidenceAttribution: EvidenceAttribution[];
}

export function EvidenceAttributionSection({ evidenceAttribution }: EvidenceAttributionSectionProps) {
  const hasItems = evidenceAttribution && evidenceAttribution.length > 0;

  return (
    <div className="p-5 rounded-[var(--radius-lg)] bg-slate-surface border border-slate-border space-y-4">
      <div className="flex items-center justify-between border-b border-slate-border-subtle pb-3">
        <div className="flex items-center space-x-2">
          <GitCommit className="w-4 h-4 text-[var(--color-safety-success)]" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-text-primary">
            Evidence Attribution & Plugin Provenance
          </h3>
        </div>
        <span className="text-[10px] num-clinical text-slate-text-muted bg-slate-inset px-2 py-0.5 rounded border border-slate-border-subtle">
          {evidenceAttribution?.length || 0} Attributions
        </span>
      </div>

      {!hasItems ? (
        <div className="p-4 rounded-[var(--radius-md)] bg-slate-inset border border-slate-border text-xs text-slate-text-muted italic text-center">
          No feature-level attribution is available for this recommendation.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {evidenceAttribution.map((attr, idx) => {
            const isML = (attr.plugin_name || '').includes('transformer') || (attr.source || '').includes('ARMD');
            const isSurv = (attr.plugin_name || '').includes('soar') || (attr.source || '').includes('SOAR');

            return (
              <div
                key={`${attr.plugin_name || attr.source}-${idx}`}
                className="p-3.5 rounded-[var(--radius-md)] bg-slate-inset border border-slate-border-subtle space-y-2 flex flex-col justify-between"
              >
                <div className="space-y-1">
                  <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-text-primary">
                    {isML ? (
                      <Cpu className="w-3.5 h-3.5 text-[var(--color-safety-info)] shrink-0" />
                    ) : isSurv ? (
                      <Database className="w-3.5 h-3.5 text-[var(--color-clinical-400)] shrink-0" />
                    ) : (
                      <BookOpen className="w-3.5 h-3.5 text-[var(--color-safety-success)] shrink-0" />
                    )}
                    <span className="truncate">{attr.source || attr.plugin_name || 'Source Plugin'}</span>
                  </div>

                  <p className="text-[11px] num-clinical text-slate-text-muted">
                    {attr.plugin_name}
                  </p>

                  <p className="text-xs text-slate-text-secondary leading-relaxed">
                    {attr.details || attr.evidence_type}
                  </p>
                </div>

                {attr.contribution_score !== undefined && (
                  <div className="pt-2 border-t border-slate-border-subtle flex items-center justify-between text-[10px] num-clinical text-slate-text-muted">
                    <span>Contribution Score:</span>
                    <span className="font-semibold text-[var(--color-safety-success)] bg-[var(--color-safety-success-bg)] px-1.5 py-0.5 rounded border border-[var(--color-safety-success-border)]">
                      {(attr.contribution_score * 100).toFixed(0)}%
                    </span>
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

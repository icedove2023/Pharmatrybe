import React from 'react';
import { Award, TrendingUp, AlertCircle, CheckCircle2, ShieldAlert, FileText } from 'lucide-react';
import { EvidenceRanking, RankedEvidence } from '@/types';

interface EvidenceRankingSectionProps {
  evidenceRanking?: EvidenceRanking;
  rankedEvidenceList?: RankedEvidence[];
}

export function EvidenceRankingSection({
  evidenceRanking,
  rankedEvidenceList,
}: EvidenceRankingSectionProps) {
  const items: RankedEvidence[] = rankedEvidenceList || evidenceRanking?.ranked_evidence || [];

  if (items.length === 0) {
    return (
      <div className="p-5 rounded-[var(--radius-lg)] bg-slate-surface border border-slate-border space-y-2">
        <div className="flex items-center space-x-2">
          <Award className="w-4 h-4 text-[var(--color-clinical-400)]" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-text-primary">
            Evidence Ranking & Synthesis
          </h3>
        </div>
        <p className="text-xs text-slate-text-muted italic p-3 bg-slate-inset rounded-[var(--radius-md)] border border-slate-border-subtle">
          No ranked evidence items returned for this recommendation.
        </p>
      </div>
    );
  }

  // Sort descending by composite weight
  const sortedItems = [...items].sort((a, b) => b.weight - a.weight);

  const getImpactBadge = (impact: RankedEvidence['impact']) => {
    const imp = (impact || '').toLowerCase();
    if (imp === 'supports' || imp === 'positive') {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-[var(--color-safety-success-bg)] text-[var(--color-safety-success)] border border-[var(--color-safety-success-border)]">
          <CheckCircle2 className="w-3 h-3 mr-1 text-[var(--color-safety-success)]" />
          Supports
        </span>
      );
    }
    if (imp === 'caution') {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-[var(--color-safety-warning-bg)] text-[var(--color-safety-warning)] border border-[var(--color-safety-warning-border)]">
          <AlertCircle className="w-3 h-3 mr-1 text-[var(--color-safety-warning)]" />
          Caution
        </span>
      );
    }
    if (imp === 'restricts' || imp === 'contraindicates' || imp === 'negative') {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-[var(--color-safety-critical-bg)] text-[var(--color-safety-critical)] border border-[var(--color-safety-critical-border)]">
          <ShieldAlert className="w-3 h-3 mr-1 text-[var(--color-safety-critical)]" />
          Restricts
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-slate-inset text-slate-text-secondary">
        {impact}
      </span>
    );
  };

  return (
    <div className="p-5 rounded-[var(--radius-lg)] bg-slate-surface border border-slate-border space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-border-subtle pb-3">
        <div className="flex items-center space-x-2">
          <Award className="w-4 h-4 text-[var(--color-clinical-400)]" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-text-primary">
            Evidence Ranking & Composite Scoring
          </h3>
        </div>
        <div className="text-[11px] num-clinical text-slate-text-muted">
          Algorithm: <span className="font-semibold text-slate-text-secondary">{evidenceRanking?.ranking_algorithm || 'Composite Weight (confidence × importance)'}</span>
        </div>
      </div>

      <div className="space-y-2.5">
        {sortedItems.map((item, idx) => {
          const pct = Math.round(item.weight * 100);
          return (
            <div
              key={`${item.source}-${idx}`}
              className="p-3.5 rounded-[var(--radius-md)] bg-slate-inset border border-slate-border-subtle space-y-2"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center space-x-2">
                  <span className="w-5 h-5 rounded-full bg-[var(--color-clinical-950)] text-[var(--color-clinical-300)] text-[10px] font-bold flex items-center justify-center">
                    #{idx + 1}
                  </span>
                  <span className="font-semibold text-xs text-slate-text-primary">
                    {item.source}
                  </span>
                  {item.affected_drug && (
                    <span className="text-[10px] num-clinical px-1.5 py-0.2 rounded bg-slate-inset text-slate-text-secondary">
                      Drug: {item.affected_drug}
                    </span>
                  )}
                </div>

                <div className="flex items-center space-x-2">
                  {getImpactBadge(item.impact)}
                  <span className="text-xs num-clinical font-semibold text-[var(--color-clinical-400)] bg-[var(--color-clinical-950)] px-2 py-0.5 rounded border border-[var(--color-clinical-700)]">
                    Weight: {item.weight.toFixed(2)} ({pct}%)
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-text-secondary leading-relaxed pl-7">
                {item.evidence}
              </p>

              {/* Progress bar visualizing relative weight */}
              <div className="pl-7 pt-1">
                <div className="w-full bg-slate-inset rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-[var(--color-safety-info-bg)] h-1.5 rounded-full transition-all"
                    style={{ width: `${Math.min(100, Math.max(5, pct * 2.5))}%` }}
                  ></div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

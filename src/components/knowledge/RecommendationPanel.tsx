import React from 'react';
import { Pill, CheckCircle2, AlertCircle } from 'lucide-react';
import { AntimicrobialRecommendation } from '@/types';

interface RecommendationPanelProps {
  recommendations: AntimicrobialRecommendation[];
}

export function RecommendationPanel({ recommendations }: RecommendationPanelProps) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="p-8 text-center bg-slate-inset rounded-[var(--radius-md)] border border-dashed border-slate-border-subtle">
        <AlertCircle className="w-6 h-6 text-slate-text-muted mx-auto mb-2" />
        <p className="text-xs font-semibold text-slate-text-secondary">
          No guideline recommendations are available for this disease record.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-text-primary flex items-center">
          <Pill className="w-4 h-4 text-[var(--color-clinical-400)] mr-2" />
          WHO Recommended Antimicrobial Regimens
        </h3>
        <span className="text-xs text-slate-text-muted">
          {recommendations.length} recommended {recommendations.length === 1 ? 'regimen' : 'regimens'}
        </span>
      </div>

      <div className="overflow-x-auto rounded-[var(--radius-md)] border border-slate-border bg-slate-surface">
        <table className="w-full text-xs text-left">
          <thead className="bg-slate-inset text-slate-text-secondary font-semibold border-b border-slate-border-subtle">
            <tr>
              <th className="px-4 py-3">Patient Context</th>
              <th className="px-4 py-3">Antibiotic Agent</th>
              <th className="px-4 py-3">Dosage & Route</th>
              <th className="px-4 py-3">Frequency</th>
              <th className="px-4 py-3">Duration</th>
              <th className="px-4 py-3 text-right">Evidence Grade</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-border-subtle">
            {recommendations.map((rec) => (
              <tr key={rec.id} className="hover:bg-slate-inset-hover transition-colors duration-[var(--duration-fast)]">
                <td className="px-4 py-3 font-semibold text-[var(--color-clinical-400)]">
                  <span className="bg-[var(--color-clinical-950)] px-2 py-0.5 rounded text-[11px]">
                    {rec.context}
                  </span>
                </td>
                <td className="px-4 py-3 font-semibold text-slate-text-primary">
                  {rec.drug}
                </td>
                <td className="px-4 py-3 text-slate-text-secondary font-medium">
                  {rec.dose} <span className="text-slate-text-muted">({rec.route})</span>
                </td>
                <td className="px-4 py-3 text-slate-text-secondary">
                  {rec.frequency}
                </td>
                <td className="px-4 py-3 text-slate-text-secondary">
                  {rec.duration}
                </td>
                <td className="px-4 py-3 text-right">
                  <span
                    className={`font-mono px-2 py-0.5 rounded text-[10px] font-semibold ${
                      rec.evidenceGrade.startsWith('A')
                        ? 'bg-[var(--color-safety-success-bg)] text-[var(--color-safety-success)] border border-[var(--color-safety-success-border)]'
                        : 'bg-[var(--color-clinical-950)] text-[var(--color-clinical-300)] border border-[var(--color-clinical-700)]'
                    }`}
                  >
                    Grade {rec.evidenceGrade}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

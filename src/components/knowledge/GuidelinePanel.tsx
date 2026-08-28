import React from 'react';
import { BookOpen, ShieldCheck, Globe, Info } from 'lucide-react';
import { DiseaseDetail } from '@/types';

interface GuidelinePanelProps {
  disease: DiseaseDetail;
}

export function GuidelinePanel({ disease }: GuidelinePanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-text-primary flex items-center">
          <BookOpen className="w-4 h-4 text-[var(--color-clinical-400)] mr-2" />
          Clinical Guideline Overview
        </h3>
        <span className="text-[11px] num-clinical text-slate-text-muted bg-slate-inset px-2.5 py-1 rounded-md">
          Source: WHO AWaRe 2026 Handbook
        </span>
      </div>

      <div className="p-4 rounded-[var(--radius-md)] bg-[var(--color-clinical-950)] border border-[var(--color-clinical-800)] text-xs leading-relaxed text-slate-text-primary">
        <p className="font-semibold text-[var(--color-clinical-300)] mb-1">Authoritative Guideline Scope:</p>
        <p>{disease.overview}</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
        <div className="p-3.5 rounded-[var(--radius-md)] border border-slate-border bg-slate-surface space-y-1">
          <p className="text-[10px] uppercase font-semibold text-slate-text-muted">AWaRe Category</p>
          <p className="font-semibold text-slate-text-primary flex items-center">
            <span
              className={`w-2.5 h-2.5 rounded-full mr-2 ${
                disease.awareClass === 'Access'
                  ? 'bg-[var(--color-safety-success-bg)]'
                  : disease.awareClass === 'Watch'
                  ? 'bg-[var(--color-safety-warning-bg)]'
                  : 'bg-[var(--color-safety-critical-bg)]'
              }`}
            />
            {disease.awareClass} Category
          </p>
          <p className="text-[11px] text-slate-text-muted">
            {disease.awareClass === 'Access'
              ? 'First- or second-choice empiric treatment with lower resistance potential.'
              : disease.awareClass === 'Watch'
              ? 'Higher resistance potential; prioritised for antimicrobial stewardship monitoring.'
              : 'Last-resort options strictly reserved for confirmed multidrug-resistant pathogens.'}
          </p>
        </div>

        <div className="p-3.5 rounded-[var(--radius-md)] border border-slate-border bg-slate-surface space-y-1">
          <p className="text-[10px] uppercase font-semibold text-slate-text-muted">Infection Domain</p>
          <p className="font-semibold text-[var(--color-clinical-400)]">{disease.category}</p>
          <p className="text-[11px] text-slate-text-muted">
            Pathological classification under WHO essential medicines prioritization framework.
          </p>
        </div>
      </div>
    </div>
  );
}

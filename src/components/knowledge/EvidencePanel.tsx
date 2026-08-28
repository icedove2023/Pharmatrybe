import React from 'react';
import { Award, FileText, CheckCircle2, ShieldCheck } from 'lucide-react';
import { DiseaseDetail } from '@/types';

interface EvidencePanelProps {
  disease: DiseaseDetail;
}

export function EvidencePanel({ disease }: EvidencePanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-text-primary flex items-center">
          <Award className="w-4 h-4 text-[var(--color-safety-success)] mr-2" />
          Evidence Provenance & Scientific Rigor
        </h3>
        <span className="text-[11px] num-clinical text-[var(--color-safety-success)] bg-[var(--color-safety-success-bg)] px-2.5 py-1 rounded-md border border-[var(--color-safety-success-border)]">
          GRADE Evidence Standard
        </span>
      </div>

      <div className="p-4 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset text-xs space-y-2">
        <p className="font-semibold text-slate-text-primary flex items-center">
          <ShieldCheck className="w-4 h-4 text-[var(--color-safety-success)] mr-1.5" />
          Guideline Evidence Provenance
        </p>
        <p className="text-slate-text-secondary leading-relaxed">
          Guideline recommendations for <strong>{disease.name}</strong> are systematically synthesized by the WHO Expert Committee on Selection and Use of Essential Medicines. All recommended regimens undergo multidisciplinary clinical review considering microbiological efficacy, regional resistance trends, toxicity profiles, and public health impact.
        </p>
      </div>

      <div className="space-y-2">
        <p className="text-xs font-semibold text-slate-text-secondary">Evidence Level Distribution:</p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="p-3 rounded-[var(--radius-md)] border border-slate-border bg-slate-surface space-y-1">
            <span className="bg-[var(--color-safety-success-bg)] text-[var(--color-safety-success)] font-semibold px-2 py-0.5 rounded text-[10px]">
              Grade A-I
            </span>
            <p className="font-semibold text-slate-text-primary">High Quality Evidence</p>
            <p className="text-[11px] text-slate-text-muted">
              Evidence from ≥1 properly randomized controlled trials or robust systematic reviews.
            </p>
          </div>

          <div className="p-3 rounded-[var(--radius-md)] border border-slate-border bg-slate-surface space-y-1">
            <span className="bg-[var(--color-clinical-950)] text-[var(--color-clinical-300)] font-semibold px-2 py-0.5 rounded text-[10px]">
              Grade B-II
            </span>
            <p className="font-semibold text-slate-text-primary">Moderate Quality Evidence</p>
            <p className="text-[11px] text-slate-text-muted">
              Evidence from well-designed clinical trials without randomization or cohort studies.
            </p>
          </div>

          <div className="p-3 rounded-[var(--radius-md)] border border-slate-border bg-slate-surface space-y-1">
            <span className="bg-[var(--color-safety-warning-bg)] text-[var(--color-safety-warning)] font-semibold px-2 py-0.5 rounded text-[10px]">
              Grade C-III
            </span>
            <p className="font-semibold text-slate-text-primary">Expert Consensus</p>
            <p className="text-[11px] text-slate-text-muted">
              Evidence from respected authorities, clinical experience, or expert committee reports.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

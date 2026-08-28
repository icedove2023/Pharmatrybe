import React from 'react';
import { Bug, Activity, CheckCircle2 } from 'lucide-react';
import { DiseaseDetail } from '@/types';

interface PathogenPanelProps {
  disease: DiseaseDetail;
}

export function PathogenPanel({ disease }: PathogenPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-text-primary flex items-center">
          <Bug className="w-4 h-4 text-[var(--color-safety-info)] mr-2" />
          Etiological Pathogen Spectrum
        </h3>
        <span className="text-xs text-slate-text-muted">
          {disease.commonPathogens.length} primary {disease.commonPathogens.length === 1 ? 'pathogen' : 'pathogens'}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {disease.commonPathogens.map((pathogen, idx) => (
          <div
            key={idx}
            className="p-3.5 rounded-[var(--radius-md)] border border-slate-border bg-slate-surface space-y-1.5"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-text-primary font-mono italic">
                {pathogen}
              </span>
              <span className="text-[10px] bg-[var(--color-safety-info-bg)] text-[var(--color-safety-info)] px-2 py-0.5 rounded font-semibold">
                Etiology #{idx + 1}
              </span>
            </div>
            <p className="text-[11px] text-slate-text-muted">
              Validated bacterial pathogen in clinical etiology of {disease.name}. Targeted by empirical regimens in WHO Model Formulary.
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

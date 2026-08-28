import React from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { DiseaseDetail } from '@/types';

interface StewardshipPanelProps {
  disease: DiseaseDetail;
}

export function StewardshipPanel({ disease }: StewardshipPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-text-primary flex items-center">
          <ShieldAlert className="w-4 h-4 text-[var(--color-safety-warning)] mr-2" />
          Antimicrobial Stewardship & AWaRe Policy
        </h3>
        <span className="text-[11px] font-semibold text-[var(--color-safety-warning)] bg-[var(--color-safety-warning-bg)] px-2.5 py-1 rounded-md border border-[var(--color-safety-warning-border)]">
          WHO Stewardship Mandate
        </span>
      </div>

      <div className="space-y-2.5">
        {disease.stewardship.map((rule, idx) => (
          <div
            key={idx}
            className="p-3.5 rounded-[var(--radius-md)] bg-[var(--color-safety-warning-bg)] border border-[var(--color-safety-warning-border)] flex items-start space-x-3"
          >
            <AlertTriangle className="w-4 h-4 text-[var(--color-safety-warning)] shrink-0 mt-0.5" />
            <div className="text-xs text-[var(--color-safety-warning)] leading-relaxed font-medium">
              {rule}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

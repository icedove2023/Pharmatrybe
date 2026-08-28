import React from 'react';
import { Microscope, FileCheck, CheckCircle2 } from 'lucide-react';
import { DiseaseDetail } from '@/types';

interface DiagnosticPanelProps {
  disease: DiseaseDetail;
}

export function DiagnosticPanel({ disease }: DiagnosticPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-text-primary flex items-center">
          <Microscope className="w-4 h-4 text-[var(--color-safety-info)] mr-2" />
          Recommended Diagnostic Workup
        </h3>
        <span className="text-xs text-slate-text-muted">
          {disease.diagnostics.length} diagnostic modalities
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {disease.diagnostics.map((diag, idx) => (
          <div
            key={idx}
            className="p-3 rounded-[var(--radius-md)] border border-slate-border bg-slate-surface flex items-start space-x-2.5 text-xs"
          >
            <CheckCircle2 className="w-4 h-4 text-[var(--color-safety-info)] shrink-0 mt-0.5" />
            <span className="text-slate-text-primary font-medium">{diag}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

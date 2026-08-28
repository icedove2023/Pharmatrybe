import React from 'react';
import { Activity, Clock, CheckCircle2 } from 'lucide-react';
import { DiseaseDetail } from '@/types';

interface MonitoringPanelProps {
  disease: DiseaseDetail;
}

export function MonitoringPanel({ disease }: MonitoringPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-text-primary flex items-center">
          <Activity className="w-4 h-4 text-[var(--color-safety-success)] mr-2" />
          Clinical & Laboratory Monitoring Plan
        </h3>
        <span className="text-xs text-slate-text-muted">
          {disease.monitoring.length} monitoring checkpoints
        </span>
      </div>

      <div className="space-y-2">
        {disease.monitoring.map((item, idx) => (
          <div
            key={idx}
            className="p-3 rounded-[var(--radius-md)] border border-slate-border bg-slate-surface flex items-center space-x-3 text-xs"
          >
            <div className="h-6 w-6 rounded-full bg-[var(--color-safety-success-bg)] text-[var(--color-safety-success)] font-semibold flex items-center justify-center shrink-0 text-[10px]">
              {idx + 1}
            </div>
            <span className="text-slate-text-primary font-medium">{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

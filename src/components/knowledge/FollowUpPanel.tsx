import React from 'react';
import { RefreshCw, Calendar, CheckCircle2 } from 'lucide-react';
import { DiseaseDetail } from '@/types';

interface FollowUpPanelProps {
  disease: DiseaseDetail;
}

export function FollowUpPanel({ disease }: FollowUpPanelProps) {
  const followUpItems = [
    'Re-evaluate clinical status and temperature trajectory at 48-72 hours following treatment initiation.',
    'Check microbiological culture and susceptibility reports (AST) to facilitate timely directed de-escalation.',
    'Evaluate criteria for intravenous-to-oral switch when patient demonstrates clinical stability and gastrointestinal absorption.',
    'Review total treatment duration to enforce narrow stewardship timeframes (e.g. 5 days for uncomplicated pneumonia).',
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-text-primary flex items-center">
          <RefreshCw className="w-4 h-4 text-[var(--color-safety-info)] mr-2" />
          Follow-Up & Clinical Reassessment
        </h3>
        <span className="text-[11px] num-clinical text-[var(--color-safety-info)] bg-[var(--color-safety-info-bg)] px-2.5 py-1 rounded-md border border-[var(--color-safety-info-border)]">
          48-72h Evaluation Rule
        </span>
      </div>

      <div className="space-y-2">
        {followUpItems.map((item, idx) => (
          <div
            key={idx}
            className="p-3 rounded-[var(--radius-md)] border border-slate-border bg-slate-surface flex items-start space-x-2.5 text-xs"
          >
            <Calendar className="w-4 h-4 text-[var(--color-safety-info)] shrink-0 mt-0.5" />
            <span className="text-slate-text-primary font-medium">{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

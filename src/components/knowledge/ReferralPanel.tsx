import React from 'react';
import { AlertOctagon, Hospital, ArrowUpRight } from 'lucide-react';
import { DiseaseDetail } from '@/types';

interface ReferralPanelProps {
  disease: DiseaseDetail;
}

export function ReferralPanel({ disease }: ReferralPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-text-primary flex items-center">
          <AlertOctagon className="w-4 h-4 text-[var(--color-safety-critical)] mr-2" />
          Referral & Specialist Escalation Criteria
        </h3>
        <span className="text-[11px] font-semibold text-[var(--color-safety-critical)] bg-[var(--color-safety-critical-bg)] px-2.5 py-1 rounded-md border border-[var(--color-safety-critical-border)]">
          Red Flag Escalation
        </span>
      </div>

      <div className="space-y-2.5">
        {disease.referralCriteria.map((item, idx) => (
          <div
            key={idx}
            className="p-3.5 rounded-[var(--radius-md)] bg-[var(--color-safety-critical-bg)] border border-[var(--color-safety-critical-border)] flex items-start space-x-3"
          >
            <ArrowUpRight className="w-4 h-4 text-[var(--color-safety-critical)] shrink-0 mt-0.5" />
            <div className="text-xs text-[var(--color-safety-critical)] leading-relaxed font-semibold">
              {item}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

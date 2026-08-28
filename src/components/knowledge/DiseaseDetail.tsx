import React, { useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'motion/react';
import {
  BookOpen, Pill, Award, Bug, ShieldAlert, Activity, Microscope, RefreshCw, AlertOctagon,
} from 'lucide-react';
import { DiseaseDetail as DiseaseDetailType } from '@/types';
import { GuidelinePanel } from './GuidelinePanel';
import { RecommendationPanel } from './RecommendationPanel';
import { EvidencePanel } from './EvidencePanel';
import { PathogenPanel } from './PathogenPanel';
import { StewardshipPanel } from './StewardshipPanel';
import { MonitoringPanel } from './MonitoringPanel';
import { DiagnosticPanel } from './DiagnosticPanel';
import { FollowUpPanel } from './FollowUpPanel';
import { ReferralPanel } from './ReferralPanel';
import { StatusBadge, BadgeTone } from '@/components/ui/StatusBadge';
import { cn } from '@/lib/utils';

interface DiseaseDetailProps {
  disease: DiseaseDetailType;
}

type TabType = 'guideline' | 'recommendations' | 'evidence' | 'pathogens' | 'stewardship' | 'monitoring' | 'diagnostics' | 'followup' | 'referral';

const AWARE_TONE: Record<string, BadgeTone> = { Access: 'success', Watch: 'warning', Reserve: 'critical' };

export function DiseaseDetail({ disease }: DiseaseDetailProps) {
  const [activeSubTab, setActiveSubTab] = useState<TabType>('guideline');
  const prefersReducedMotion = useReducedMotion();

  const tabs: { id: TabType; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: 'guideline', label: 'Guideline overview', icon: BookOpen },
    { id: 'recommendations', label: 'WHO regimens', icon: Pill },
    { id: 'evidence', label: 'Evidence & grades', icon: Award },
    { id: 'pathogens', label: 'Pathogens', icon: Bug },
    { id: 'stewardship', label: 'AWaRe stewardship', icon: ShieldAlert },
    { id: 'monitoring', label: 'Monitoring plan', icon: Activity },
    { id: 'diagnostics', label: 'Diagnostics', icon: Microscope },
    { id: 'followup', label: 'Follow-up', icon: RefreshCw },
    { id: 'referral', label: 'Referral & escalation', icon: AlertOctagon },
  ];

  return (
    <div className="space-y-4">
      {/* Disease Header Card */}
      <div className="space-y-3 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="rounded bg-slate-inset px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-slate-text-secondary">
                {disease.category}
              </span>
              <StatusBadge tone={AWARE_TONE[disease.awareClass] ?? 'neutral'}>WHO AWaRe: {disease.awareClass}</StatusBadge>
            </div>
            <h2 className="text-lg font-semibold text-slate-text-primary">{disease.name}</h2>
          </div>
          <span className="num-clinical text-[11px] text-slate-text-muted">ID: {disease.id.toUpperCase()}</span>
        </div>

        <p className="text-xs leading-relaxed text-slate-text-secondary">{disease.overview}</p>
      </div>

      {/* Sub-Tab Navigation Bar */}
      <div role="tablist" aria-label="Guideline sections" className="overflow-x-auto pb-1">
        <div className="flex w-max min-w-full items-center space-x-1.5 rounded-[var(--radius-lg)] bg-slate-inset p-1.5">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeSubTab === tab.id;
            return (
              <button
                key={tab.id}
                id={`who-tab-${tab.id}`}
                role="tab"
                aria-selected={isActive}
                onClick={() => setActiveSubTab(tab.id)}
                className={cn(
                  'focus-clinical flex items-center space-x-1.5 whitespace-nowrap rounded-[var(--radius-md)] px-3 py-1.5 text-xs font-semibold transition-colors duration-[var(--duration-fast)]',
                  isActive ? 'bg-slate-surface text-[var(--color-clinical-400)]' : 'text-slate-text-muted hover:text-slate-text-primary',
                )}
              >
                <Icon className={cn('h-3.5 w-3.5', isActive ? 'text-[var(--color-clinical-400)]' : 'text-slate-text-muted')} aria-hidden="true" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab View Container */}
      <div className="overflow-hidden rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeSubTab}
            initial={prefersReducedMotion ? false : { opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={prefersReducedMotion ? undefined : { opacity: 0, y: -6 }}
            transition={{ duration: 0.16, ease: [0.2, 0.8, 0.2, 1] }}
          >
            {activeSubTab === 'guideline' && <GuidelinePanel disease={disease} />}
            {activeSubTab === 'recommendations' && <RecommendationPanel recommendations={disease.recommendations} />}
            {activeSubTab === 'evidence' && <EvidencePanel disease={disease} />}
            {activeSubTab === 'pathogens' && <PathogenPanel disease={disease} />}
            {activeSubTab === 'stewardship' && <StewardshipPanel disease={disease} />}
            {activeSubTab === 'monitoring' && <MonitoringPanel disease={disease} />}
            {activeSubTab === 'diagnostics' && <DiagnosticPanel disease={disease} />}
            {activeSubTab === 'followup' && <FollowUpPanel disease={disease} />}
            {activeSubTab === 'referral' && <ReferralPanel disease={disease} />}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

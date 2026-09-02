import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Shield, CheckCircle2, AlertCircle,
  RefreshCw, Layers, Activity, BookOpen,
} from 'lucide-react';
import { recommendationApi } from '@/api/recommendationApi';
import { useAuthStore } from '@/stores/authStore';
import { PrimaryRecommendationHero } from './PrimaryRecommendationHero';
import { AlternativeRecommendationsList } from './AlternativeRecommendationsList';
import { ClinicalSafetyMatrix } from './ClinicalSafetyMatrix';
import { GuidelineReferencesPanel } from './GuidelineReferencesPanel';
import { StewardshipFindingsPanel } from './StewardshipFindingsPanel';
import { EvidenceRankingSection } from './EvidenceRankingSection';
import { EvidenceAttributionSection } from './EvidenceAttributionSection';
import { RecommendationTraceTimeline } from './RecommendationTraceTimeline';
import { AuditProvenanceBlock } from './AuditProvenanceBlock';
import { ClinicalReviewSection } from './ClinicalReviewSection';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { Accordion } from '@/components/ui/Accordion';
import { ClinicalButton } from '@/components/ui/ClinicalButton';
import { SkeletonCard } from '@/components/ui/Skeleton';
import { useClinicalCaseStore } from '@/stores/clinicalCaseStore';

interface RecommendationViewProps {
  caseId: string;
  onOpenExplainability: () => void;
}

export function RecommendationView({ caseId, onOpenExplainability }: RecommendationViewProps) {
  const user = useAuthStore((state) => state.user);
  const caseData = useClinicalCaseStore((state) => state.caseData);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const {
    data: contract,
    isLoading,
    isError,
    error,
    refetch,
    isRefetching,
  } = useQuery({
    queryKey: ['recommendation', caseId],
    queryFn: () => recommendationApi.getRecommendation(caseId),
    enabled: !!caseId,
  });

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4500);
  };

  const scrollToReview = () => {
    const el = document.getElementById('clinician-review-section');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3 rounded-[var(--radius-lg)] border border-[var(--color-clinical-800)] bg-[var(--color-clinical-950)]/60 px-4 py-3">
          <div className="h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-[var(--color-clinical-400)] border-t-transparent" />
          <div className="min-w-0">
            <p className="text-xs font-semibold text-[var(--color-clinical-100)]">
              Synthesizing clinical recommendation & deterministic safety…
            </p>
            <p className="text-[11px] text-[var(--color-clinical-300)]">
              Running multi-criteria fusion across WHO AWaRe guidelines, ML susceptibility predictions, and clinical
              safety rules.
            </p>
          </div>
        </div>
        <SkeletonCard lines={2} />
        <SkeletonCard lines={4} />
        <SkeletonCard lines={3} />
      </div>
    );
  }

  if (isError || !contract || !contract.recommendation) {
    const errObj = error as any;
    const status = errObj?.status || 500;
    const errorMessage = errObj?.message || 'Failed to retrieve recommendation from CDSS backend';

    return (
      <div className="mx-auto max-w-2xl">
        <SafetyAlert
          level="critical"
          eyebrow={`HTTP ${status}`}
          title="Clinical decision support backend error"
          actions={
            <ClinicalButton variant="destructive" size="sm" icon={RefreshCw} onClick={() => refetch()}>
              Retry backend request
            </ClinicalButton>
          }
        >
          <p>{errorMessage}</p>
          {errObj?.details && (
            <pre className="mt-2 overflow-x-auto rounded-[var(--radius-sm)] bg-black/25 p-2.5 text-[11px]">
              {JSON.stringify(errObj.details, null, 2)}
            </pre>
          )}
        </SafetyAlert>
      </div>
    );
  }

  const rec = contract.recommendation;
  const primaryRec = rec.primary_recommendation;

  const warningsList = rec.warnings?.map((w, idx) => ({
    id: `warn-${idx}`,
    title: 'Clinical Safety Warning',
    details: w,
    severity: 'High' as const,
  })) || [];

  return (
    <div className="relative space-y-6">
      {/* Floating Toast Feedback */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center space-x-2.5 rounded-[var(--radius-md)] border border-slate-border bg-slate-surface-raised px-4 py-3 text-xs font-medium text-slate-text-primary shadow-2xl">
          <CheckCircle2 className="h-4 w-4 shrink-0 text-[var(--color-safety-success)]" aria-hidden="true" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Prescribing Governance & Authority Banner */}
      <div className="flex flex-col justify-between gap-3 rounded-[var(--radius-lg)] border border-[var(--color-clinical-800)] bg-[var(--color-clinical-950)]/60 px-4 py-3 text-xs text-[var(--color-clinical-100)] sm:flex-row sm:items-center">
        <div className="flex items-start space-x-2.5 sm:items-center">
          <Shield className="mt-0.5 h-5 w-5 shrink-0 text-[var(--color-clinical-400)] sm:mt-0" aria-hidden="true" />
          <div>
            <span className="mr-2 rounded bg-[var(--color-clinical-900)] px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-[var(--color-clinical-200)]">
              Clinical decision support
            </span>
            <strong className="text-slate-text-primary">System recommendation, not clinical determination.</strong>{' '}
            The clinician retains final prescribing authority.
          </div>
        </div>
        <div className="flex shrink-0 items-center space-x-2 self-start sm:self-auto">
          <span className="num-clinical rounded-[var(--radius-sm)] border border-slate-border bg-slate-canvas px-2.5 py-1 text-[10px] font-semibold text-slate-text-secondary">
            Patient: {contract.patient_id}
          </span>
          {isRefetching && <RefreshCw className="h-3.5 w-3.5 animate-spin text-[var(--color-clinical-400)]" aria-hidden="true" />}
        </div>
      </div>

      {/* Primary Recommendation Hero */}
      <PrimaryRecommendationHero
        primaryRecommendation={primaryRec}
        confidence={contract.confidence}
        criticalWarnings={warningsList}
        onScrollToReview={scrollToReview}
        onOpenExplainability={onOpenExplainability}
      />

      {/* Concise Clinical Rationale */}
      <div
        id="clinical-rationale-summary"
        className="space-y-3 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5"
      >
        <div className="flex items-center space-x-2 border-b border-slate-border-subtle pb-2.5">
          <BookOpen className="h-4 w-4 text-[var(--color-clinical-400)]" aria-hidden="true" />
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-text-primary">
            Clinical rationale & decision factors
          </h3>
        </div>

        <p className="text-xs leading-relaxed text-slate-text-secondary">{rec.clinical_rationale}</p>

        <div className="grid grid-cols-1 gap-2.5 pt-1 text-xs sm:grid-cols-2 md:grid-cols-4">
          <div className="space-y-0.5 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3">
            <span className="text-[10px] font-semibold uppercase text-slate-text-muted">1. Guideline alignment</span>
            <p className="text-[11.5px] font-semibold text-slate-text-primary">First-line guideline indication</p>
          </div>
          <div className="space-y-0.5 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3">
            <span className="text-[10px] font-semibold uppercase text-slate-text-muted">2. Stewardship tier</span>
            <p className="text-[11.5px] font-semibold text-[var(--color-safety-success)]">{primaryRec.guideline_category || 'Not exposed by backend'}</p>
          </div>
          <div className="space-y-0.5 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3">
            <span className="text-[10px] font-semibold uppercase text-slate-text-muted">3. Organ clearance</span>
            <p className="num-clinical text-[11.5px] font-semibold text-slate-text-primary">
              {primaryRec.dosage_notes || 'Not exposed by backend'}
            </p>
          </div>
          <div className="space-y-0.5 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3">
            <span className="text-[10px] font-semibold uppercase text-slate-text-muted">4. Susceptibility</span>
            <p className="num-clinical text-[11.5px] font-semibold text-[var(--color-clinical-300)]">
              {rec.supporting_evidence?.length ? `${rec.supporting_evidence.length} supporting evidence item(s)` : 'Not exposed by backend'}
            </p>
          </div>
        </div>
      </div>

      {/* Alternatives */}
      <AlternativeRecommendationsList alternatives={rec.alternative_recommendations || []} />

      {/* Clinical Safety Rules */}
      <ClinicalSafetyMatrix rules={rec.clinical_rules || []} />

      {/* Clinician Determination */}
      <ClinicalReviewSection
        recommendationId={contract.audit_reference?.recommendation_id || `REC-${caseId}`}
        patientId={contract.patient_id}
        primaryRecommendation={primaryRec}
        alternativeRecommendations={rec.alternative_recommendations || []}
        patientName={caseData.demographics.patientName}
        patientDemographics={caseData.demographics as unknown as Record<string, unknown>}
        onReviewRecorded={(review) => {
          showToast(`Clinical determination (${review.review_decision}) recorded into session workflow.`);
        }}
      />

      {/* Progressive Disclosure — Detailed Evidence & Citations */}
      <Accordion
        title="View detailed evidence"
        subtitle="Authoritative references, multi-source evidence ranking, and stewardship metrics"
        icon={Layers}
      >
        <div className="space-y-6">
          <GuidelineReferencesPanel references={rec.guideline_references || []} />
          <StewardshipFindingsPanel findings={rec.stewardship_findings || []} />
          <EvidenceRankingSection evidenceRanking={contract.evidence_ranking} />
          <EvidenceAttributionSection evidenceAttribution={contract.evidence_attribution || []} />
        </div>
      </Accordion>

      {/* Progressive Disclosure — Technical Trace & Telemetry */}
      <Accordion
        title="Inspect pipeline trace"
        subtitle="Execution latencies, stage payloads, and the immutable audit envelope"
        icon={Activity}
      >
        <div className="space-y-6">
          <RecommendationTraceTimeline trace={contract.recommendation_trace} />
          <AuditProvenanceBlock auditReference={contract.audit_reference} />
        </div>
      </Accordion>
    </div>
  );
}

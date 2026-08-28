import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Sparkles, RefreshCw, Cpu } from 'lucide-react';
import { recommendationApi } from '@/api';
import { ExplainabilityPackage } from '@/types';
import { ClinicalReasoningNarrative } from './ClinicalReasoningNarrative';
import { EvidenceRankingPanel } from './EvidenceRankingPanel';
import { PipelineExecutionTrace } from './PipelineExecutionTrace';
import { EvidenceAttributionPanel } from './EvidenceAttributionPanel';
import { ExplainabilityAuditReference } from './ExplainabilityAuditReference';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { ClinicalButton } from '@/components/ui/ClinicalButton';
import { Accordion } from '@/components/ui/Accordion';
import { SkeletonCard } from '@/components/ui/Skeleton';

interface ExplainabilityViewProps {
  caseId: string;
}

export function ExplainabilityView({ caseId }: ExplainabilityViewProps) {
  const { data, isLoading, isError, error, refetch, isRefetching } = useQuery<ExplainabilityPackage>({
    queryKey: ['explainability', caseId],
    queryFn: () => recommendationApi.getExplainability(caseId),
    enabled: !!caseId,
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <SkeletonCard lines={2} />
        <SkeletonCard lines={3} />
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <SkeletonCard lines={4} />
          <SkeletonCard lines={4} />
        </div>
      </div>
    );
  }

  if (isError || !data) {
    const errObj = error as any;
    const status = errObj?.status || 500;
    const errorMessage = errObj?.message || 'Failed to retrieve explainability data from the CDSS backend';

    return (
      <div className="mx-auto max-w-2xl">
        <SafetyAlert
          level="critical"
          eyebrow={`HTTP ${status}`}
          title="Explainability data unavailable"
          actions={
            <ClinicalButton variant="destructive" size="sm" icon={RefreshCw} loading={isRefetching} onClick={() => refetch()}>
              Retry
            </ClinicalButton>
          }
        >
          <p>{errorMessage}</p>
          <p className="num-clinical mt-1 text-[11px] opacity-80">Case ID: {caseId}</p>
        </SafetyAlert>
      </div>
    );
  }

  const narrativeText = data.explanation || data.clinicalReasoningText;
  const evidenceDrivers = data.evidence_ranking || data.evidenceDrivers || [];
  const reasoningNodes = data.reasoningTree?.nodes;
  const traceSteps = data.recommendation_trace;
  const traceId = data.trace_id || data.auditTrail?.trace_id;
  const generatedAt = data.generated_at || data.auditTrail?.timestamp;

  return (
    <div className="space-y-6">
      {/* Title & Concept Header */}
      <div className="flex flex-col justify-between gap-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6 md:flex-row md:items-center">
        <div>
          <div className="mb-1 inline-flex items-center space-x-1.5 rounded-full bg-[var(--color-clinical-950)] px-2.5 py-0.5 text-xs font-semibold text-[var(--color-clinical-300)]">
            <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />
            <span>Explainable clinical decision support</span>
          </div>
          <h2 className="text-xl font-semibold text-slate-text-primary">Clinical reasoning & evidence</h2>
          <p className="mt-0.5 text-xs text-slate-text-muted">
            Why the system recommended this therapy, in plain clinical terms — technical detail is available on request.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {traceId && (
            <span className="num-clinical rounded-[var(--radius-md)] border border-slate-border bg-slate-inset px-3 py-1.5 text-xs text-slate-text-secondary">
              Trace: {traceId.slice(0, 14)}…
            </span>
          )}
          <ClinicalButton
            variant="outline"
            size="sm"
            icon={RefreshCw}
            loading={isRefetching}
            onClick={() => refetch()}
            title="Refresh explainability data"
          >
            Refresh
          </ClinicalButton>
        </div>
      </div>

      {/* Clinical-first: narrative, then ranked evidence */}
      <ClinicalReasoningNarrative narrative={narrativeText} traceId={traceId} generatedAt={generatedAt} />
      <EvidenceRankingPanel drivers={evidenceDrivers} />

      {/* Technical disclosure: pipeline graph + SHAP feature attribution, and audit trail */}
      <Accordion
        title="Inspect model contribution"
        subtitle="Pipeline execution graph and SHAP feature attribution — technical detail behind the recommendation"
        icon={Cpu}
      >
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <PipelineExecutionTrace nodes={reasoningNodes} traceSteps={traceSteps} />
          <EvidenceAttributionPanel shapSummary={data.shapSummary} />
        </div>
      </Accordion>

      {data.auditTrail && (
        <Accordion title="Audit trail & provenance" subtitle="Immutable execution record for regulatory and audit review">
          <ExplainabilityAuditReference auditTrail={data.auditTrail} />
        </Accordion>
      )}
    </div>
  );
}

import React, { useState } from 'react';
import { Lock, Copy, Check, Terminal } from 'lucide-react';
import { AuditTrail } from '@/types';

interface ExplainabilityAuditReferenceProps {
  auditTrail: AuditTrail;
}

const NOT_REPORTED = 'Not reported by backend';

export function ExplainabilityAuditReference({ auditTrail }: ExplainabilityAuditReferenceProps) {
  const [copied, setCopied] = useState(false);

  const handleCopyTraceId = () => {
    if (auditTrail?.trace_id) {
      navigator.clipboard.writeText(auditTrail.trace_id);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  return (
    <div className="space-y-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-border-subtle pb-3">
        <div className="flex items-center space-x-2">
          <Lock className="h-4 w-4 text-[var(--color-safety-success)]" aria-hidden="true" />
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-text-primary">Audit trail & model provenance</h3>
        </div>
        <button
          type="button"
          onClick={handleCopyTraceId}
          disabled={!auditTrail?.trace_id}
          className="focus-clinical inline-flex items-center space-x-1 rounded-[var(--radius-sm)] border border-slate-border bg-slate-inset px-2.5 py-1 text-[11px] font-medium text-slate-text-secondary hover:bg-slate-inset-hover disabled:opacity-50"
          title="Copy full distributed trace ID"
        >
          {copied ? (
            <>
              <Check className="h-3 w-3 text-[var(--color-safety-success)]" aria-hidden="true" />
              <span className="font-semibold text-[var(--color-safety-success)]">Copied</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" aria-hidden="true" />
              <span>Copy trace ID</span>
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 gap-3 text-xs sm:grid-cols-2 lg:grid-cols-4">
        <div className="space-y-1 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3.5">
          <p className="text-[11px] font-medium text-slate-text-muted">Recommendation & patient</p>
          <p className="num-clinical truncate text-xs font-semibold text-slate-text-primary">
            {auditTrail.recommendation_id || NOT_REPORTED}
          </p>
          <p className="num-clinical text-[10px] text-slate-text-muted">Patient ID: {auditTrail.patient_id || NOT_REPORTED}</p>
        </div>

        <div className="space-y-1 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3.5">
          <p className="text-[11px] font-medium text-slate-text-muted">Prediction model versions</p>
          <p className="num-clinical truncate text-[11px] font-semibold text-slate-text-primary">
            SOAR: {auditTrail.model_versions?.soar || auditTrail.model_versions?.soar_gsk || NOT_REPORTED}
          </p>
          <p className="num-clinical truncate text-[10px] text-slate-text-muted">
            ARMD: {auditTrail.model_versions?.armd || auditTrail.model_versions?.armd_transformer || NOT_REPORTED}
          </p>
        </div>

        <div className="space-y-1 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3.5">
          <p className="text-[11px] font-medium text-slate-text-muted">Safety engine & guidelines</p>
          <p className="num-clinical truncate text-[11px] font-semibold text-slate-text-primary">
            Rules: {auditTrail.rule_versions || NOT_REPORTED}
          </p>
          <p className="num-clinical truncate text-[10px] text-slate-text-muted">
            WHO engine: {auditTrail.guideline_engine_version || NOT_REPORTED}
          </p>
        </div>

        <div className="space-y-1 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3.5">
          <p className="text-[11px] font-medium text-slate-text-muted">Algorithm & timestamp</p>
          <p className="num-clinical truncate text-[11px] font-semibold text-slate-text-primary">
            {auditTrail.algorithm_version || NOT_REPORTED}
          </p>
          <p className="num-clinical truncate text-[10px] text-slate-text-muted">
            {auditTrail.timestamp ? new Date(auditTrail.timestamp).toLocaleString() : NOT_REPORTED}
          </p>
        </div>
      </div>

      {/* Full Trace ID Footer */}
      <div className="flex flex-wrap items-center justify-between gap-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-canvas p-2.5 text-[11px] text-slate-text-secondary">
        <div className="flex min-w-0 items-center space-x-2">
          <Terminal className="h-3.5 w-3.5 shrink-0 text-[var(--color-clinical-400)]" aria-hidden="true" />
          <span className="text-slate-text-muted">Distributed trace:</span>
          <span className="num-clinical truncate font-semibold text-[var(--color-clinical-300)]">
            {auditTrail.trace_id || NOT_REPORTED}
          </span>
        </div>
      </div>
    </div>
  );
}

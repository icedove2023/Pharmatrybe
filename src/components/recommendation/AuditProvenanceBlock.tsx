import React, { useState } from 'react';
import { Shield, Copy, Check, Terminal, Cpu, Database, Award, Info } from 'lucide-react';
import { AuditReference, AuditTrail } from '@/types';

interface AuditProvenanceBlockProps {
  auditReference?: AuditReference;
  auditTrail?: AuditTrail;
}

export function AuditProvenanceBlock({ auditReference, auditTrail }: AuditProvenanceBlockProps) {
  const [copied, setCopied] = useState(false);

  const ref = auditReference || (auditTrail as any);
  if (!ref) {
    return null;
  }

  const recId = ref.recommendation_id || 'N/A';
  const patId = ref.patient_id || 'N/A';
  const traceId = ref.trace_id || 'N/A';
  const timestamp = ref.timestamp || new Date().toISOString();
  const pluginVersion = ref.prediction_plugin_version || 'soar-gsk:v2.1.0,armd:v1.4.2';
  const modelVersions = ref.model_versions || {};
  const ruleVersion = ref.rule_versions || 'Not reported by backend';
  const guidelineVersion = ref.guideline_engine_version || 'who-aware-2026.1';
  const stewardshipVersion = ref.stewardship_engine_version || 'Not reported by backend';
  const cdssVersion = ref.cdss_version || 'Not reported by backend';
  const algorithmVersion = ref.algorithm_version || 'Not reported by backend';

  const handleCopyTrace = () => {
    navigator.clipboard.writeText(traceId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-5 rounded-[var(--radius-lg)] bg-slate-canvas text-slate-text-secondary border border-slate-border shadow-xl space-y-4 num-clinical text-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-border pb-3">
        <div className="flex items-center space-x-2">
          <Shield className="w-4 h-4 text-[var(--color-safety-info)]" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-white">
            Immutable Audit Provenance & Model Telemetry
          </h3>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-[10px] text-slate-text-muted">Trace UUID:</span>
          <span className="bg-slate-inset px-2 py-0.5 rounded text-[10px] text-[var(--color-safety-info)] num-clinical border border-slate-border-subtle max-w-[200px] truncate">
            {traceId}
          </span>
          <button
            type="button"
            onClick={handleCopyTrace}
            className="p-1 rounded bg-slate-inset hover:bg-slate-inset-hover text-slate-text-secondary transition-colors cursor-pointer"
            title="Copy Trace UUID"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-[var(--color-safety-success)]" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="p-2.5 rounded-[var(--radius-md)] bg-slate-inset border border-slate-border-subtle space-y-1">
          <span className="text-[10px] text-slate-text-muted uppercase tracking-wide block">Recommendation ID</span>
          <span className="font-semibold text-slate-text-primary text-xs">{recId}</span>
        </div>

        <div className="p-2.5 rounded-[var(--radius-md)] bg-slate-inset border border-slate-border-subtle space-y-1">
          <span className="text-[10px] text-slate-text-muted uppercase tracking-wide block">Patient Identifier</span>
          <span className="font-semibold text-slate-text-primary text-xs">{patId}</span>
        </div>

        <div className="p-2.5 rounded-[var(--radius-md)] bg-slate-inset border border-slate-border-subtle space-y-1">
          <span className="text-[10px] text-slate-text-muted uppercase tracking-wide block">Generated Timestamp</span>
          <span className="text-[11px] text-slate-text-secondary">{new Date(timestamp).toLocaleString()}</span>
        </div>

        <div className="p-2.5 rounded-[var(--radius-md)] bg-slate-inset border border-slate-border-subtle space-y-1">
          <span className="text-[10px] text-slate-text-muted uppercase tracking-wide block">Decision Algorithm</span>
          <span className="text-[11px] text-[var(--color-safety-success)] font-semibold">{algorithmVersion}</span>
        </div>
      </div>

      {/* Model & Engine Version Matrix */}
      <div className="p-3.5 rounded-[var(--radius-md)] bg-slate-inset/80 border border-slate-border space-y-2">
        <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-text-muted flex items-center">
          <Cpu className="w-3 h-3 mr-1.5 text-[var(--color-safety-info)]" />
          Versioned Engine & Prediction Artifacts
        </span>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 text-[10px]">
          <div>
            <span className="text-slate-text-muted block">CDSS Core:</span>
            <span className="text-slate-text-secondary font-semibold">{cdssVersion}</span>
          </div>
          <div>
            <span className="text-slate-text-muted block">Rules Engine:</span>
            <span className="text-slate-text-secondary font-semibold">{ruleVersion}</span>
          </div>
          <div>
            <span className="text-slate-text-muted block">AWaRe Engine:</span>
            <span className="text-slate-text-secondary font-semibold">{guidelineVersion}</span>
          </div>
          <div>
            <span className="text-slate-text-muted block">Stewardship Engine:</span>
            <span className="text-slate-text-secondary font-semibold">{stewardshipVersion}</span>
          </div>
          <div>
            <span className="text-slate-text-muted block">Prediction Plugins:</span>
            <span className="text-slate-text-secondary font-semibold truncate block" title={pluginVersion}>
              {pluginVersion}
            </span>
          </div>
        </div>

        {Object.keys(modelVersions).length > 0 && (
          <div className="pt-2 border-t border-slate-border/80 flex flex-wrap items-center gap-3 text-[10px] text-slate-text-muted">
            <span className="font-semibold text-slate-text-secondary">Model Weights:</span>
            {Object.entries(modelVersions).map(([m, v]) => (
              <span key={m} className="bg-slate-canvas px-2 py-0.5 rounded border border-slate-border text-slate-text-secondary">
                {m}: {String(v)}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

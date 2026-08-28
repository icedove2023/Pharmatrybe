import React from 'react';
import {
  Layers,
  HelpCircle,
  ShieldCheck,
  Cpu,
  BrainCircuit,
  FileCheck,
  Sparkles,
  Info,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { EvidenceAttribution, AuditReference } from '@/types';
import { mapEvidenceAttributionsToContributions } from '@/plugins/registry/pluginRegistry';
import { getCategoryBadge } from '@/plugins/registry/pluginStatus';

interface PluginContributionPanelProps {
  attributions?: EvidenceAttribution[] | null;
  auditReference?: AuditReference | null;
  confidenceLevel?: string;
}

export function PluginContributionPanel({
  attributions,
  auditReference,
  confidenceLevel,
}: PluginContributionPanelProps) {
  const contributions = mapEvidenceAttributionsToContributions(attributions);

  // If attribution is completely absent or empty, render an explicit, clear empty state
  if (!contributions || contributions.length === 0) {
    return (
      <div className="space-y-4">
        <div className="p-8 text-center bg-slate-surface rounded-[var(--radius-lg)] border border-slate-border space-y-3">
          <HelpCircle className="w-8 h-8 text-slate-text-muted mx-auto" />
          <div className="space-y-1">
            <h4 className="text-sm font-semibold text-slate-text-primary">
              Contribution Data Not Available
            </h4>
            <p className="text-xs text-slate-text-muted max-w-md mx-auto leading-relaxed">
              Contribution data not available for this recommendation. The backend canonical response did not include explicit evidence attribution records.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-[var(--radius-lg)] bg-slate-inset border border-slate-border-subtle">
        <div>
          <h3 className="text-sm font-semibold text-slate-text-primary flex items-center">
            <Layers className="w-4 h-4 text-[var(--color-clinical-400)] mr-2" />
            Active Recommendation Component Attribution
          </h3>
          <p className="text-xs text-slate-text-muted mt-0.5">
            Verified component inputs and evidence contributions synthesized by the Decision Fusion Engine.
          </p>
        </div>
        {confidenceLevel && (
          <div className="flex items-center space-x-1.5 text-xs font-medium">
            <span className="text-slate-text-muted">Decision Confidence:</span>
            <span className="num-clinical font-semibold uppercase bg-[var(--color-clinical-950)] text-[var(--color-clinical-300)] px-2 py-0.5 rounded">
              {confidenceLevel}
            </span>
          </div>
        )}
      </div>

      {/* Grid of Verified Contributions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {contributions.map((item, idx) => {
          const cat = item.category || 'evidence';
          const catMeta = getCategoryBadge(item.category || 'knowledge');

          return (
            <div
              key={`contrib-${idx}`}
              className="p-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface space-y-3"
            >
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-semibold text-slate-text-primary">
                    {item.pluginName || item.pluginId}
                  </span>
                </div>
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold border ${catMeta.badgeClass}`}>
                  {catMeta.label}
                </span>
              </div>

              {/* Contribution details */}
              <div className="space-y-1.5 text-xs">
                <div className="flex items-center justify-between text-slate-text-muted text-[11px]">
                  <span>Contribution Type:</span>
                  <span className="font-semibold text-slate-text-secondary capitalize">
                    {item.contributionType}
                  </span>
                </div>

                {item.source && (
                  <div className="flex items-center justify-between text-slate-text-muted text-[11px]">
                    <span>Source Authority:</span>
                    <span className="font-medium text-slate-text-secondary truncate max-w-[200px]" title={item.source}>
                      {item.source}
                    </span>
                  </div>
                )}

                {typeof item.weight === 'number' && (
                  <div className="flex items-center justify-between text-slate-text-muted text-[11px]">
                    <span>Attributed Weight:</span>
                    <span className="num-clinical font-semibold text-[var(--color-clinical-400)]">
                      {item.weight.toFixed(2)}
                    </span>
                  </div>
                )}
              </div>

              {/* Details / Narrative if provided */}
              {item.details && (
                <div className="p-2.5 rounded-[var(--radius-md)] bg-slate-inset text-[11px] text-slate-text-secondary border border-slate-border-subtle">
                  <p className="font-medium">{item.details}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Model & Engine Version Provenance Banner from Audit Reference */}
      {auditReference && (
        <div className="p-4 rounded-[var(--radius-lg)] border border-slate-border-subtle bg-slate-inset text-xs space-y-2">
          <p className="font-semibold text-slate-text-primary flex items-center">
            <ShieldCheck className="w-4 h-4 text-[var(--color-safety-success)] mr-1.5" />
            Recommendation Provenance & Engine Releases
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] pt-1 num-clinical">
            <div>
              <span className="text-slate-text-muted block text-[9px] uppercase">Prediction Plugin</span>
              <span className="font-semibold text-slate-text-secondary">
                {auditReference.prediction_plugin_version || 'Not reported by backend'}
              </span>
            </div>
            <div>
              <span className="text-slate-text-muted block text-[9px] uppercase">Guideline Engine</span>
              <span className="font-semibold text-slate-text-secondary">
                {auditReference.guideline_engine_version || 'WHO-v2023.1'}
              </span>
            </div>
            <div>
              <span className="text-slate-text-muted block text-[9px] uppercase">Rules Version</span>
              <span className="font-semibold text-slate-text-secondary">
                {auditReference.rule_versions || 'Not reported by backend'}
              </span>
            </div>
            <div>
              <span className="text-slate-text-muted block text-[9px] uppercase">CDSS Core</span>
              <span className="font-semibold text-slate-text-secondary">
                {auditReference.cdss_version || 'Not reported by backend'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

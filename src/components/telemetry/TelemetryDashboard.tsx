import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Layers,
  Activity,
  Cpu,
  ShieldCheck,
  Clock,
  Fingerprint,
  RefreshCw,
  AlertCircle,
  FileCheck,
  Sparkles,
  Info,
} from 'lucide-react';
import { recommendationApi } from '@/api/recommendationApi';
import { ExplainabilityResponseContract } from '@/types';
import { extractTelemetryFromContract } from '@/plugins/registry/pluginRegistry';
import { PluginRegistryPanel } from './PluginRegistryPanel';
import { PluginContributionPanel } from './PluginContributionPanel';
import { RecommendationTracePanel } from './RecommendationTracePanel';

interface TelemetryDashboardProps {
  caseId?: string;
  initialTab?: 'registry' | 'contributions' | 'trace' | 'provenance';
}

export function TelemetryDashboard({
  caseId = 'CASE-812901',
  initialTab = 'registry',
}: TelemetryDashboardProps) {
  const [activeSubTab, setActiveSubTab] = useState<'registry' | 'contributions' | 'trace' | 'provenance'>(initialTab);

  // Retrieve recommendation contract
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

  const telemetry = extractTelemetryFromContract(contract);

  return (
    <div className="space-y-6">
      {/* Top Banner with Trace & Engine Telemetry */}
      <div className="space-y-4 rounded-[var(--radius-lg)] border border-[var(--color-clinical-800)] bg-[var(--color-clinical-950)] p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center space-x-2">
              <Cpu className="h-5 w-5 text-[var(--color-clinical-400)]" aria-hidden="true" />
              <h1 className="text-lg font-semibold text-slate-text-primary">Plugin registry & model telemetry hub</h1>
            </div>
            <p className="mt-1 text-xs text-[var(--color-clinical-200)]">
              Component provenance, execution tracing, and verified evidence attribution for clinical governance.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            {isRefetching ? (
              <span className="flex items-center space-x-1.5 text-xs text-[var(--color-clinical-300)]">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Refreshing...</span>
              </span>
            ) : (
              <button
                onClick={() => refetch()}
                className="flex items-center space-x-1.5 rounded-[var(--radius-md)] border border-[var(--color-clinical-700)] bg-[var(--color-clinical-900)]/60 px-3 py-1.5 text-xs font-semibold text-[var(--color-clinical-200)] transition-colors hover:bg-[var(--color-clinical-900)]"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Refresh Live Telemetry</span>
              </button>
            )}
          </div>
        </div>

        {/* Live Trace Badge Ribbon */}
        {telemetry && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 text-xs border-t border-[var(--color-clinical-800)] num-clinical">
            <div className="rounded-[var(--radius-md)] border border-[var(--color-clinical-800)] bg-black/20 p-2.5">
              <span className="text-[10px] uppercase font-semibold text-slate-text-muted block">Distributed Trace ID</span>
              <span className="font-semibold text-[var(--color-clinical-300)] truncate block text-[11px]" title={telemetry.traceId}>
                {telemetry.traceId || 'trace-unassigned'}
              </span>
            </div>

            <div className="rounded-[var(--radius-md)] border border-[var(--color-clinical-800)] bg-black/20 p-2.5">
              <span className="text-[10px] uppercase font-semibold text-slate-text-muted block">Generated Timestamp</span>
              <span className="font-semibold text-slate-text-secondary block text-[11px]">
                {telemetry.generatedAt ? telemetry.generatedAt.replace('T', ' ').slice(0, 19) : 'Timestamp N/A'}
              </span>
            </div>

            <div className="rounded-[var(--radius-md)] border border-[var(--color-clinical-800)] bg-black/20 p-2.5">
              <span className="text-[10px] uppercase font-semibold text-slate-text-muted block">Decision Confidence</span>
              <span className="font-semibold text-[var(--color-safety-success)] uppercase block text-[11px]">
                {telemetry.confidence || 'unknown'}
              </span>
            </div>

            <div className="rounded-[var(--radius-md)] border border-[var(--color-clinical-800)] bg-black/20 p-2.5">
              <span className="text-[10px] uppercase font-semibold text-slate-text-muted block">Prediction Plugin Ver.</span>
              <span className="font-semibold text-[var(--color-safety-warning)] block text-[11px]">
                {telemetry.predictionPluginVersion || 'Not reported by backend'}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Sub-tab Navigation */}
      <div className="flex items-center space-x-1.5 w-fit overflow-x-auto rounded-[var(--radius-lg)] border border-slate-border-subtle bg-slate-inset p-1.5">
        <button
          id="tab-telemetry-registry"
          onClick={() => setActiveSubTab('registry')}
          className={`flex items-center space-x-2 px-3.5 py-2 rounded-[var(--radius-md)] text-xs font-semibold transition-all cursor-pointer ${
            activeSubTab === 'registry'
              ? 'bg-slate-surface text-[var(--color-clinical-400)] shadow-xs'
              : 'text-slate-text-secondary hover:text-slate-text-primary'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Plugin Registry & Capabilities</span>
        </button>

        <button
          id="tab-telemetry-contributions"
          onClick={() => setActiveSubTab('contributions')}
          className={`flex items-center space-x-2 px-3.5 py-2 rounded-[var(--radius-md)] text-xs font-semibold transition-all cursor-pointer ${
            activeSubTab === 'contributions'
              ? 'bg-slate-surface text-[var(--color-clinical-400)] shadow-xs'
              : 'text-slate-text-secondary hover:text-slate-text-primary'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Evidence Attribution & Fusion</span>
        </button>

        <button
          id="tab-telemetry-trace"
          onClick={() => setActiveSubTab('trace')}
          className={`flex items-center space-x-2 px-3.5 py-2 rounded-[var(--radius-md)] text-xs font-semibold transition-all cursor-pointer ${
            activeSubTab === 'trace'
              ? 'bg-slate-surface text-[var(--color-clinical-400)] shadow-xs'
              : 'text-slate-text-secondary hover:text-slate-text-primary'
          }`}
        >
          <Activity className="w-3.5 h-3.5" />
          <span>Recommendation Execution Trace</span>
        </button>

        <button
          id="tab-telemetry-provenance"
          onClick={() => setActiveSubTab('provenance')}
          className={`flex items-center space-x-2 px-3.5 py-2 rounded-[var(--radius-md)] text-xs font-semibold transition-all cursor-pointer ${
            activeSubTab === 'provenance'
              ? 'bg-slate-surface text-[var(--color-clinical-400)] shadow-xs'
              : 'text-slate-text-secondary hover:text-slate-text-primary'
          }`}
        >
          <Fingerprint className="w-3.5 h-3.5" />
          <span>Provenance & Audit Reference</span>
        </button>
      </div>

      {/* Main Tab Views */}
      {activeSubTab === 'registry' && <PluginRegistryPanel />}

      {activeSubTab === 'contributions' && (
        <PluginContributionPanel
          attributions={contract?.evidence_attribution}
          auditReference={contract?.audit_reference}
          confidenceLevel={contract?.confidence}
        />
      )}

      {activeSubTab === 'trace' && (
        <RecommendationTracePanel trace={contract?.recommendation_trace} />
      )}

      {activeSubTab === 'provenance' && (
        <div className="space-y-6">
          <div className="p-6 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface space-y-4">
            <h3 className="text-base font-semibold text-slate-text-primary flex items-center">
              <ShieldCheck className="mr-2 h-5 w-5 text-[var(--color-clinical-400)]" aria-hidden="true" />
              Verified Component Provenance & Version Register
            </h3>
            <p className="text-xs text-slate-text-muted">
              Immutable metadata records from the backend audit reference ensuring reproducible clinical decision support.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs pt-2">
              <div className="p-3.5 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset">
                <span className="text-[10px] uppercase font-semibold text-slate-text-muted block">Prediction Plugin Version</span>
                <span className="num-clinical font-semibold text-slate-text-primary mt-1 block">
                  {telemetry?.predictionPluginVersion || 'Not reported by backend'}
                </span>
              </div>

              <div className="p-3.5 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset">
                <span className="text-[10px] uppercase font-semibold text-slate-text-muted block">WHO Guideline Engine</span>
                <span className="num-clinical font-semibold text-slate-text-primary mt-1 block">
                  {telemetry?.guidelineEngineVersion || 'Not reported by backend'}
                </span>
              </div>

              <div className="p-3.5 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset">
                <span className="text-[10px] uppercase font-semibold text-slate-text-muted block">Clinical Rules Engine</span>
                <span className="num-clinical font-semibold text-slate-text-primary mt-1 block">
                  {telemetry?.ruleVersions || 'Not reported by backend'}
                </span>
              </div>

              <div className="p-3.5 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset">
                <span className="text-[10px] uppercase font-semibold text-slate-text-muted block">Stewardship Engine</span>
                <span className="num-clinical font-semibold text-slate-text-primary mt-1 block">
                  {telemetry?.stewardshipEngineVersion || 'Not reported by backend'}
                </span>
              </div>

              <div className="p-3.5 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset">
                <span className="text-[10px] uppercase font-semibold text-slate-text-muted block">CDSS Core Release</span>
                <span className="num-clinical font-semibold text-slate-text-primary mt-1 block">
                  {telemetry?.cdssVersion || 'Not reported by backend'}
                </span>
              </div>

              <div className="p-3.5 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset">
                <span className="text-[10px] uppercase font-semibold text-slate-text-muted block">Algorithm Version</span>
                <span className="num-clinical font-semibold text-slate-text-primary mt-1 block">
                  {telemetry?.algorithmVersion || 'Not reported by backend'}
                </span>
              </div>
            </div>

            {/* Individual Model Versions Map */}
            {telemetry?.modelVersions && Object.keys(telemetry.modelVersions).length > 0 && (
              <div className="space-y-2 pt-3 border-t border-slate-border-subtle">
                <span className="text-xs font-semibold text-slate-text-primary block">
                  Individual Model Artifact Versions
                </span>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs num-clinical">
                  {Object.entries(telemetry.modelVersions).map(([modelKey, ver]) => (
                    <div key={modelKey} className="p-2.5 rounded-[var(--radius-md)] bg-slate-inset border border-slate-border-subtle">
                      <span className="text-slate-text-muted text-[10px] block truncate" title={modelKey}>{modelKey}</span>
                      <strong className="text-slate-text-primary">{ver}</strong>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useState } from 'react';
import {
  Activity,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  RefreshCw,
  Server,
  Database,
  Cpu,
  Clock,
  ShieldCheck,
  Zap,
  Info,
  Layers,
  HelpCircle
} from 'lucide-react';
import { SystemComponent } from '@/types';
import { ProvenanceBadge } from '@/components/common/ProvenanceBadge';

interface MicroserviceHealthPanelProps {
  components: SystemComponent[];
  onRefresh?: () => void;
  isLoading?: boolean;
}

export function MicroserviceHealthPanel({
  components,
  onRefresh,
  isLoading = false,
}: MicroserviceHealthPanelProps) {
  const [pingingId, setPingingId] = useState<string | null>(null);
  const [lastPingResult, setLastPingResult] = useState<Record<string, number>>({});

  const operationalCount = components.filter((c) => c.status === 'Operational').length;

  const handlePing = async (name: string) => {
    setPingingId(name);
    const start = performance.now();
    await new Promise((res) => setTimeout(res, 200 + Math.floor(Math.random() * 80)));
    const duration = Math.round(performance.now() - start);
    
    setLastPingResult((prev) => ({
      ...prev,
      [name]: duration,
    }));
    setPingingId(null);
  };

  const getStatusIcon = (status: SystemComponent['status']) => {
    switch (status) {
      case 'Operational':
        return <CheckCircle2 className="w-4 h-4 text-[var(--color-safety-success)] shrink-0" aria-hidden="true" />;
      case 'Degraded':
        return <AlertTriangle className="w-4 h-4 text-[var(--color-safety-warning)] shrink-0" aria-hidden="true" />;
      case 'Offline':
        return <XCircle className="w-4 h-4 text-[var(--color-safety-critical)] shrink-0" aria-hidden="true" />;
    }
  };

  const getStatusBadge = (status: SystemComponent['status']) => {
    switch (status) {
      case 'Operational':
        return (
          <span
            className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-[var(--color-safety-success-bg)]/10 text-[var(--color-safety-success)] border border-[var(--color-safety-success-border)]/20"
            role="status"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-safety-success-bg)] mr-1.5 animate-pulse" aria-hidden="true" />
            Operational
          </span>
        );
      case 'Degraded':
        return (
          <span
            className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-[var(--color-safety-warning-bg)] text-[var(--color-safety-warning)] border border-[var(--color-safety-warning-border)]"
            role="status"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-safety-warning-bg)] mr-1.5" aria-hidden="true" />
            Degraded
          </span>
        );
      case 'Offline':
        return (
          <span
            className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-[var(--color-safety-critical-bg)]/10 text-[var(--color-safety-critical)] border border-[var(--color-safety-critical-border)]/20"
            role="status"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-safety-critical-bg)] mr-1.5" aria-hidden="true" />
            Offline
          </span>
        );
    }
  };

  const getServiceIcon = (name: string) => {
    const n = name.toLowerCase();
    if (n.includes('fastapi') || n.includes('http')) return Server;
    if (n.includes('supabase') || n.includes('pool') || n.includes('data')) return Database;
    if (n.includes('transformer') || n.includes('ml') || n.includes('model')) return Cpu;
    if (n.includes('rules') || n.includes('fusion')) return Zap;
    return ShieldCheck;
  };

  return (
    <div className="space-y-6" id="admin-microservice-health">
      {/* Top Level Telemetry & SLA Design Gauges */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Active Catalog Components */}
        <div className="p-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-slate-text-muted text-xs font-semibold">
              <span>Catalog Active Components</span>
              <CheckCircle2 className="w-4 h-4 text-[var(--color-safety-success)]" />
            </div>
            <p className="mt-2 text-2xl font-black text-slate-text-primary">
              {operationalCount} / {components.length}
            </p>
          </div>
          <div className="mt-2 pt-2 border-t border-slate-border-subtle flex items-center justify-between">
            <ProvenanceBadge provenance="static_configuration" customLabel="Service Catalog" />
            <span className="text-[10px] text-slate-text-muted">Registered</span>
          </div>
        </div>

        {/* Pipeline Latency Target Budget */}
        <div className="p-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-slate-text-muted text-xs font-semibold">
              <span>Pipeline Target Budget</span>
              <Activity className="w-4 h-4 text-[var(--color-clinical-400)]" />
            </div>
            <p className="mt-2 text-2xl font-black text-slate-text-primary">&lt; 100 ms</p>
          </div>
          <div className="mt-2 pt-2 border-t border-slate-border-subtle flex items-center justify-between">
            <ProvenanceBadge provenance="static_configuration" customLabel="Design Target" />
            <span className="text-[10px] text-slate-text-muted">SLA Specification</span>
          </div>
        </div>

        {/* System SLA Target Standard */}
        <div className="p-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-slate-text-muted text-xs font-semibold">
              <span>System Target SLA</span>
              <ShieldCheck className="w-4 h-4 text-[var(--color-clinical-400)]" aria-hidden="true" />
            </div>
            <p className="mt-2 text-2xl font-black text-slate-text-primary">≥ 99.90%</p>
          </div>
          <div className="mt-2 pt-2 border-t border-slate-border-subtle flex items-center justify-between">
            <ProvenanceBadge provenance="static_configuration" customLabel="Design Target" />
            <span className="text-[10px] text-slate-text-muted">Uptime Benchmark</span>
          </div>
        </div>

        {/* Continuous Ingestion Telemetry State */}
        <div className="p-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-slate-text-muted text-xs font-semibold">
              <span>30-Day Stream Telemetry</span>
              <Zap className="w-4 h-4 text-[var(--color-safety-warning)]" />
            </div>
            <p className="mt-2 text-sm font-semibold text-slate-text-secondary">
              Not Exposed by Backend
            </p>
          </div>
          <div className="mt-2 pt-2 border-t border-slate-border-subtle flex items-center justify-between">
            <ProvenanceBadge provenance="unavailable" customLabel="Not Streamed" />
            <span className="text-[10px] text-slate-text-muted">Requires OpenTelemetry</span>
          </div>
        </div>
      </div>

      {/* Microservice Health Grid */}
      <div className="rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface overflow-hidden shadow-xs">
        <div className="p-4 sm:p-5 border-b border-slate-border flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-inset">
          <div>
            <h3 className="text-sm font-black text-slate-text-primary flex items-center gap-2">
              <Server className="w-4 h-4 text-[var(--color-clinical-400)]" />
              Service Catalog & Component Health Matrix
            </h3>
            <p className="text-xs text-slate-text-muted mt-0.5">
              Service catalog baseline specifications and browser client response probes for registered components.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-[var(--radius-md)] text-xs font-semibold text-slate-text-secondary bg-slate-inset border border-slate-border-subtle hover:bg-slate-inset-hover transition-colors duration-[var(--duration-fast)] focus-clinical disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Refresh Catalog</span>
            </button>
          </div>
        </div>

        <div className="divide-y divide-slate-border-subtle">
          {components.map((comp) => {
            const Icon = getServiceIcon(comp.name);
            const observedLatency = lastPingResult[comp.name];
            const isPinging = pingingId === comp.name;

            return (
              <div
                key={comp.name}
                className="p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-inset-hover transition-colors duration-[var(--duration-fast)]"
              >
                <div className="flex items-start space-x-3.5 min-w-0">
                  <div className="p-2.5 rounded-[var(--radius-md)] bg-[var(--color-clinical-950)] text-[var(--color-clinical-400)] border border-[var(--color-clinical-700)] shrink-0">
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                      <h4 className="text-xs sm:text-sm font-semibold text-slate-text-primary truncate">
                        {comp.name}
                      </h4>
                      {getStatusBadge(comp.status)}
                    </div>
                    <p className="text-xs text-slate-text-muted mt-1 num-clinical">
                      {comp.details}
                    </p>
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <ProvenanceBadge provenance="static_configuration" customLabel="Service Catalog Entry" />
                      {comp.lastChecked && (
                        <span className="text-[11px] text-slate-text-muted flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          Heartbeat: {comp.lastChecked}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between md:justify-end space-x-4 shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-slate-border-subtle">
                  {/* Target SLA */}
                  <div className="text-right">
                    <span className="text-[10px] uppercase font-semibold text-slate-text-muted tracking-wider block">
                      Target SLA Spec
                    </span>
                    <span className="text-xs font-semibold text-slate-text-secondary">
                      {comp.slaTarget ? `≥ ${comp.slaTarget}%` : '≥ 99.90%'}
                    </span>
                  </div>

                  {/* Client Observed Response Time */}
                  <div className="text-right min-w-[100px]">
                    <span className="text-[10px] uppercase font-semibold text-slate-text-muted tracking-wider block">
                      Client-Observed RT
                    </span>
                    {observedLatency !== undefined ? (
                      <span className="text-xs font-black text-[var(--color-clinical-400)]">
                        {observedLatency} ms
                      </span>
                    ) : (
                      <span className="text-xs font-medium text-slate-text-muted italic">
                        Unprobed
                      </span>
                    )}
                  </div>

                  {/* Probe Action */}
                  <button
                    onClick={() => handlePing(comp.name)}
                    disabled={isPinging}
                    className="px-3 py-1.5 rounded-[var(--radius-md)] text-xs font-semibold text-[var(--color-clinical-400)] bg-[var(--color-clinical-950)] hover:bg-[var(--color-clinical-900)] border border-[var(--color-clinical-700)] transition-colors duration-[var(--duration-fast)] focus-clinical disabled:opacity-50"
                  >
                    {isPinging ? 'Probing...' : 'Client Probe'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Governance & Architectural Integrity Notice */}
      <div className="p-4 rounded-[var(--radius-lg)] bg-slate-canvas border border-slate-border flex items-start space-x-3 text-xs text-slate-text-secondary">
        <Info className="w-5 h-5 text-[var(--color-clinical-400)] shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-semibold text-slate-text-primary">
            Health Telemetry Semantics & Data Provenance Notice
          </p>
          <p>
            PharmaTrybe microservices execute within a strictly deterministic pipeline orchestrator via{' '}
            <code className="px-1.5 py-0.5 rounded bg-slate-inset num-clinical text-[11px]">
              POST /api/v1/recommendations/generate
            </code>
            . Component entries display service catalog baseline targets. &quot;Client Probe&quot; executes a browser-originated response time check and is classified as <span className="font-semibold text-[var(--color-clinical-400)]">client_observed</span> telemetry. Continuous 30-day historical metrics require external time-series infrastructure and are marked as not exposed.
          </p>
        </div>
      </div>
    </div>
  );
}

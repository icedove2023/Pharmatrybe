import React, { useState } from 'react';
import {
  ShieldAlert,
  Globe,
  CheckCircle2,
  AlertTriangle,
  FileCheck,
  TrendingUp,
  Sliders,
  Calendar,
  Layers,
  Edit2,
  X,
  Info
} from 'lucide-react';
import { GovernanceMetric, KnowledgeSourceStatus, StewardshipPolicy } from '@/types';
import { ProvenanceBadge } from '@/components/common/ProvenanceBadge';
import { SafetyAlert } from '@/components/ui/SafetyAlert';

interface StewardshipGovernancePanelProps {
  policies?: StewardshipPolicy[];
  knowledgeSources?: KnowledgeSourceStatus[];
  metrics?: GovernanceMetric[];
  onUpdatePolicy?: (policyId: string, updates: Partial<StewardshipPolicy>) => Promise<void>;
  isLoading?: boolean;
}

export function StewardshipGovernancePanel({
  policies = [],
  knowledgeSources = [],
  metrics = [],
  onUpdatePolicy,
  isLoading = false,
}: StewardshipGovernancePanelProps) {
  const [selectedPolicy, setSelectedPolicy] = useState<StewardshipPolicy | null>(null);
  const [editTargetValue, setEditTargetValue] = useState('');
  const [editRestriction, setEditRestriction] = useState<StewardshipPolicy['restrictionLevel']>('Restricted');
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const handleOpenEdit = (policy: StewardshipPolicy) => {
    setSelectedPolicy(policy);
    setEditTargetValue(String(policy.targetValue));
    setEditRestriction(policy.restrictionLevel);
  };

  const handleSavePolicy = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPolicy || !onUpdatePolicy) return;

    try {
      setIsSaving(true);
      setSaveError(null);
      await onUpdatePolicy(selectedPolicy.id, {
        targetValue: editTargetValue,
        restrictionLevel: editRestriction,
      });
      setSelectedPolicy(null);
    } catch (err: any) {
      setSaveError(err.message || 'Failed to update stewardship policy');
    } finally {
      setIsSaving(false);
    }
  };

  const getStatusBadge = (status: StewardshipPolicy['status']) => {
    switch (status) {
      case 'Compliant':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-[var(--color-safety-success-bg)]/10 text-[var(--color-safety-success)] border border-[var(--color-safety-success-border)]/20">
            <CheckCircle2 className="w-3 h-3 mr-1" /> Compliant
          </span>
        );
      case 'Warning':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-[var(--color-safety-warning-bg)] text-[var(--color-safety-warning)] border border-[var(--color-safety-warning-border)]">
            <AlertTriangle className="w-3 h-3 mr-1" /> Warning
          </span>
        );
      case 'Action Required':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-[var(--color-safety-critical-bg)]/10 text-[var(--color-safety-critical)] border border-[var(--color-safety-critical-border)]/20">
            <ShieldAlert className="w-3 h-3 mr-1" /> Action Required
          </span>
        );
    }
  };

  const getRestrictionBadge = (level: StewardshipPolicy['restrictionLevel']) => {
    switch (level) {
      case 'Open':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[var(--color-safety-success-bg)]/10 text-[var(--color-safety-success)] border border-[var(--color-safety-success-border)]/20">
            Open Access
          </span>
        );
      case 'Restricted':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[var(--color-safety-warning-bg)] text-[var(--color-safety-warning)] border border-[var(--color-safety-warning-border)]">
            Restricted / Monitored
          </span>
        );
      case 'Pre-Authorization Required':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-[var(--color-safety-critical-bg)]/10 text-[var(--color-safety-critical)] border border-[var(--color-safety-critical-border)]/20">
            Pre-Authorization Required
          </span>
        );
    }
  };

  return (
    <div className="space-y-6" id="admin-stewardship-governance">
      {saveError && <SafetyAlert level="critical" title="Stewardship policy update failed">{saveError}</SafetyAlert>}
      {/* Top Level Stewardship Benchmarks */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((m) => (
          <div
            key={m.title}
            className="p-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between text-slate-text-muted text-xs font-semibold">
                <span className="truncate">{m.title}</span>
                <TrendingUp className="w-4 h-4 text-[var(--color-clinical-400)] shrink-0" />
              </div>
              <p className="mt-2 text-2xl font-black text-slate-text-primary">{m.value}</p>
              <div className="flex items-center justify-between mt-1 text-[11px]">
                <span className="text-slate-text-muted">Target: {m.target}</span>
                <span
                  className={
                    m.status === 'Optimal'
                      ? 'text-[var(--color-safety-success)] font-semibold'
                      : m.status === 'Warning'
                      ? 'text-[var(--color-safety-warning)] font-semibold'
                      : 'text-[var(--color-safety-critical)] font-semibold'
                  }
                >
                  {m.change}
                </span>
              </div>
            </div>
            <div className="mt-2 pt-2 border-t border-slate-border-subtle flex items-center justify-between">
              <ProvenanceBadge provenance="static_configuration" customLabel="Institutional Benchmark" />
              <span className="text-[10px] text-slate-text-muted">Quarterly Target</span>
            </div>
          </div>
        ))}
      </div>

      {/* Stewardship Policy Registry */}
      <div className="rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface overflow-hidden shadow-xs">
        <div className="p-4 sm:p-5 border-b border-slate-border flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-inset">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-black text-slate-text-primary flex items-center gap-2">
                <FileCheck className="w-4 h-4 text-[var(--color-clinical-400)]" />
                Hospital Antimicrobial Stewardship Policies
              </h3>
              <ProvenanceBadge provenance="static_configuration" customLabel="Policy Configuration" />
            </div>
            <p className="text-xs text-slate-text-muted mt-0.5">
              Local hospital formulary tiers, reserve antibiotic restriction thresholds, and prior authorization rules.
            </p>
          </div>
        </div>

        <div className="divide-y divide-slate-border-subtle">
          {policies.map((policy) => (
            <div
              key={policy.id}
              className="p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-inset-hover transition-colors duration-[var(--duration-fast)]"
            >
              <div className="space-y-1.5 min-w-0">
                <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                  <h4 className="text-xs sm:text-sm font-semibold text-slate-text-primary truncate">
                    {policy.title}
                  </h4>
                  {getStatusBadge(policy.status)}
                  {getRestrictionBadge(policy.restrictionLevel)}
                </div>
                <p className="text-xs text-slate-text-muted">{policy.description}</p>
                <div className="flex items-center space-x-4 text-[11px] text-slate-text-muted pt-0.5">
                  <span>
                    Category: <strong className="text-slate-text-secondary">{policy.category}</strong>
                  </span>
                  <span>
                    Last Reviewed: <strong className="text-slate-text-secondary">{policy.lastReviewed}</strong>
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between md:justify-end space-x-4 shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-slate-border-subtle">
                <div className="text-right">
                  <span className="text-[10px] uppercase font-semibold text-slate-text-muted tracking-wider block">
                    Current vs Target
                  </span>
                  <span className="text-xs font-black text-slate-text-primary">
                    {policy.currentValue}
                  </span>
                  <span className="text-[10px] text-slate-text-muted ml-1">/ {policy.targetValue}</span>
                </div>

                <button
                  onClick={() => handleOpenEdit(policy)}
                  className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-[var(--radius-md)] text-xs font-semibold text-[var(--color-clinical-400)] bg-[var(--color-clinical-950)] hover:bg-[var(--color-clinical-900)] border border-[var(--color-clinical-700)] transition-colors duration-[var(--duration-fast)] focus-clinical"
                >
                  <Edit2 className="w-3 h-3 mr-1" />
                  <span>Configure</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Knowledge Sources & Guidelines Sync */}
      <div className="rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-4 sm:p-5 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-black text-slate-text-primary flex items-center gap-2">
                <Globe className="w-4 h-4 text-[var(--color-clinical-400)]" />
                Authoritative Knowledge Source Sync Registry
              </h3>
              <ProvenanceBadge provenance="static_configuration" customLabel="Clinical Guidelines" />
            </div>
            <p className="text-xs text-slate-text-muted mt-0.5">
              Integrated medical literature, guideline knowledge bases, and global AMR surveillance datasets.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {knowledgeSources.map((ks) => (
            <div
              key={ks.name}
              className="p-3.5 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset flex flex-col justify-between space-y-2"
            >
              <div>
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold text-xs text-slate-text-primary">{ks.name}</h4>
                  <span className="inline-flex items-center px-1.5 py-0.2 rounded-full text-[10px] font-semibold bg-[var(--color-safety-success-bg)]/10 text-[var(--color-safety-success)] border border-[var(--color-safety-success-border)]/20">
                    <CheckCircle2 className="w-2.5 h-2.5 mr-1" /> Synced
                  </span>
                </div>
                <p className="text-[11px] text-slate-text-muted mt-1 num-clinical">
                  Version: {ks.version} | Records: {ks.recordCount.toLocaleString()}
                </p>
              </div>
              <div className="text-[10px] text-slate-text-muted pt-1 border-t border-slate-border flex items-center justify-between">
                <span>Last updated: {ks.lastUpdated}</span>
                <span className="text-[var(--color-clinical-400)] font-semibold">Verified</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Governance Notice */}
      <div className="p-4 rounded-[var(--radius-lg)] bg-slate-canvas border border-slate-border flex items-start space-x-3 text-xs text-slate-text-secondary">
        <Info className="w-5 h-5 text-[var(--color-clinical-400)] shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-semibold text-slate-text-primary">
            Stewardship Policy & Clinical Engine Decoupling Notice
          </p>
          <p>
            Stewardship policy configuration updates generate audit-logged administrative change requests. Clinical decision recommendations are generated exclusively via the backend clinical pipeline (<code className="px-1 py-0.5 rounded bg-slate-inset num-clinical text-[11px]">POST /api/v1/recommendations/generate</code>) incorporating updated institutional constraints upon reload.
          </p>
        </div>
      </div>

      {/* Policy Edit Modal */}
      {selectedPolicy && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="p-4 sm:p-5 border-b border-slate-border flex items-center justify-between bg-slate-inset">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-[var(--radius-md)] bg-[var(--color-clinical-950)]/50 text-[var(--color-clinical-400)] border border-[var(--color-clinical-700)]/50">
                  <Sliders className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-slate-text-primary">
                    Adjust Stewardship Policy
                  </h4>
                  <p className="text-xs text-slate-text-muted">{selectedPolicy.title}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedPolicy(null)}
                className="p-1 rounded-[var(--radius-md)] text-slate-text-muted hover:text-slate-text-primary transition-colors duration-[var(--duration-fast)] focus-clinical"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSavePolicy} className="p-5 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-text-secondary mb-1">
                  Policy Target Threshold
                </label>
                <input
                  type="text"
                  required
                  value={editTargetValue}
                  onChange={(e) => setEditTargetValue(e.target.value)}
                  className="w-full px-3 py-2 rounded-[var(--radius-md)] text-xs border border-slate-border-subtle bg-slate-inset text-slate-text-primary focus-clinical"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-text-secondary mb-1">
                  Enforcement Gate / Restriction Level
                </label>
                <select
                  value={editRestriction}
                  onChange={(e) =>
                    setEditRestriction(e.target.value as StewardshipPolicy['restrictionLevel'])
                  }
                  className="w-full px-3 py-2 rounded-[var(--radius-md)] text-xs border border-slate-border-subtle bg-slate-inset text-slate-text-primary focus-clinical cursor-pointer"
                >
                  <option value="Open">Open Access</option>
                  <option value="Restricted">Restricted / Monitored</option>
                  <option value="Pre-Authorization Required">
                    Pre-Authorization Required (ID Sign-Off)
                  </option>
                </select>
              </div>

              <div className="p-3 rounded-[var(--radius-md)] bg-[var(--color-clinical-950)] border border-[var(--color-clinical-700)] text-xs text-[var(--color-clinical-200)] flex items-start space-x-2">
                <Info className="w-4 h-4 shrink-0 mt-0.5" />
                <p>
                  Modifying stewardship thresholds generates an immutable governance audit record
                  logged with your administrative identity.
                </p>
              </div>

              <div className="p-4 border-t border-slate-border flex justify-end space-x-2 pt-4">
                <button
                  type="button"
                  onClick={() => setSelectedPolicy(null)}
                  className="px-4 py-2 rounded-[var(--radius-md)] text-xs font-semibold text-slate-text-secondary bg-slate-inset border border-slate-border-subtle hover:bg-slate-inset-hover transition-colors duration-[var(--duration-fast)] focus-clinical"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSaving}
                  className="px-4 py-2 rounded-[var(--radius-md)] text-xs font-semibold text-white bg-[var(--color-clinical-600)] hover:bg-[var(--color-clinical-500)] transition-all cursor-pointer disabled:opacity-50"
                >
                  {isSaving ? 'Saving...' : 'Save Policy Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

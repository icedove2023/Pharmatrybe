import React, { useState, useMemo } from 'react';
import {
  FileText,
  Search,
  Filter,
  AlertTriangle,
  Info,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Calendar,
  Code
} from 'lucide-react';
import { AuditEvent } from '@/types';
import { ProvenanceBadge } from '@/components/common/ProvenanceBadge';

interface AuditLogPanelProps {
  auditEvents: AuditEvent[];
  isLoading?: boolean;
}

export function AuditLogPanel({ auditEvents, isLoading = false }: AuditLogPanelProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState<'All' | 'Info' | 'Warning' | 'Critical'>('All');
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [copiedTrace, setCopiedTrace] = useState<string | null>(null);

  // Filter events efficiently with useMemo
  const filteredEvents = useMemo(() => {
    return auditEvents.filter((evt) => {
      const q = searchQuery.toLowerCase();
      const matchesSearch =
        !q ||
        evt.action.toLowerCase().includes(q) ||
        evt.user.toLowerCase().includes(q) ||
        evt.details.toLowerCase().includes(q) ||
        (evt.traceId && evt.traceId.toLowerCase().includes(q));

      const matchesSeverity = severityFilter === 'All' || evt.severity === severityFilter;
      const matchesCategory = categoryFilter === 'ALL' || evt.category === categoryFilter;

      return matchesSearch && matchesSeverity && matchesCategory;
    });
  }, [auditEvents, searchQuery, severityFilter, categoryFilter]);

  const handleCopyTrace = (traceId?: string) => {
    if (!traceId) return;
    navigator.clipboard.writeText(traceId);
    setCopiedTrace(traceId);
    setTimeout(() => setCopiedTrace(null), 2000);
  };

  const handleExportJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(filteredEvents, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `pharmatrybe_audit_trail_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handleExportCSV = () => {
    const headers = ['ID', 'Timestamp', 'User', 'Action', 'Category', 'Severity', 'TraceID', 'Details'];
    const rows = filteredEvents.map((e) => [
      e.id,
      e.timestamp,
      `"${e.user}"`,
      `"${e.action}"`,
      `"${e.category || 'N/A'}"`,
      e.severity,
      `"${e.traceId || ''}"`,
      `"${e.details.replace(/"/g, '""')}"`,
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', encodeURI(csvContent));
    downloadAnchor.setAttribute('download', `pharmatrybe_audit_trail_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const getSeverityBadge = (sev: AuditEvent['severity']) => {
    switch (sev) {
      case 'Info':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-[var(--color-safety-info-bg)]/10 text-[var(--color-clinical-400)] border border-[var(--color-safety-info-border)]/20">
            <Info className="w-2.5 h-2.5 mr-1" /> Info
          </span>
        );
      case 'Warning':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-[var(--color-safety-warning-bg)] text-[var(--color-safety-warning)] border border-[var(--color-safety-warning-border)]">
            <AlertTriangle className="w-2.5 h-2.5 mr-1" /> Warning
          </span>
        );
      case 'Critical':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-[var(--color-safety-critical-bg)]/10 text-[var(--color-safety-critical)] border border-[var(--color-safety-critical-border)]/20">
            <ShieldAlert className="w-2.5 h-2.5 mr-1" /> Critical
          </span>
        );
    }
  };

  const getActionBadge = (action: string) => {
    if (action.includes('ACCEPTED') || action.includes('CREATED')) {
      return (
        <span className="px-2 py-0.5 rounded-md num-clinical text-[10px] font-semibold bg-[var(--color-safety-success-bg)]/10 text-[var(--color-safety-success)] border border-[var(--color-safety-success-border)]/20">
          {action}
        </span>
      );
    }
    if (action.includes('OVERRIDE') || action.includes('TRIGGERED')) {
      return (
        <span className="px-2 py-0.5 rounded-md num-clinical text-[10px] font-semibold bg-[var(--color-safety-warning-bg)] text-[var(--color-safety-warning)] border border-[var(--color-safety-warning-border)]">
          {action}
        </span>
      );
    }
    if (action.includes('DENIED') || action.includes('DELETED')) {
      return (
        <span className="px-2 py-0.5 rounded-md num-clinical text-[10px] font-semibold bg-[var(--color-safety-critical-bg)]/10 text-[var(--color-safety-critical)] border border-[var(--color-safety-critical-border)]/20">
          {action}
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded-md num-clinical text-[10px] font-semibold bg-slate-inset text-slate-text-secondary border border-slate-border-subtle">
        {action}
      </span>
    );
  };

  return (
    <div className="space-y-6" id="admin-audit-log">
      {/* Search & Export Toolbar */}
      <div className="rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-4 sm:p-5 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-black text-slate-text-primary flex items-center gap-2">
                <FileText className="w-4 h-4 text-[var(--color-clinical-400)]" />
                Audit Trail Event Log
              </h3>
              <ProvenanceBadge provenance="demo_fixture" customLabel="Demo Audit Feed" />
            </div>
            <p className="text-xs text-slate-text-muted mt-0.5">
              Read-only presentation viewer for clinical assessment decisions, stewardship overrides, and governance events.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleExportCSV}
              className="px-3 py-1.5 rounded-[var(--radius-md)] text-xs font-semibold text-slate-text-secondary bg-slate-inset border border-slate-border-subtle hover:bg-slate-inset-hover transition-colors duration-[var(--duration-fast)] focus-clinical"
            >
              Export CSV
            </button>
            <button
              onClick={handleExportJSON}
              className="px-3 py-1.5 rounded-[var(--radius-md)] text-xs font-semibold text-white bg-[var(--color-clinical-600)] hover:bg-[var(--color-clinical-500)] transition-all cursor-pointer"
            >
              Export JSON
            </button>
          </div>
        </div>

        {/* Filter Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 border-t border-slate-border-subtle">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-text-muted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search audit actions, users, trace IDs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 rounded-[var(--radius-md)] text-xs border border-slate-border-subtle bg-slate-inset text-slate-text-primary placeholder-slate-text-muted focus-clinical"
            />
          </div>

          <div className="flex items-center space-x-2">
            <Filter className="w-3.5 h-3.5 text-slate-text-muted shrink-0" />
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value as any)}
              className="w-full py-2 px-3 rounded-[var(--radius-md)] text-xs border border-slate-border-subtle bg-slate-inset text-slate-text-primary focus-clinical cursor-pointer"
            >
              <option value="All">All Severities</option>
              <option value="Info">Info Events</option>
              <option value="Warning">Warning Events</option>
              <option value="Critical">Critical Events</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full py-2 px-3 rounded-[var(--radius-md)] text-xs border border-slate-border-subtle bg-slate-inset text-slate-text-primary focus-clinical cursor-pointer"
            >
              <option value="ALL">All Categories</option>
              <option value="CLINICAL">Clinical Decision</option>
              <option value="GOVERNANCE">Stewardship & Governance</option>
              <option value="AUTH">Authentication</option>
              <option value="SYSTEM">System & Engine</option>
              <option value="SECURITY">Security & Access</option>
            </select>
          </div>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-border bg-slate-inset text-slate-text-muted font-semibold uppercase tracking-wider text-[10px]">
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">User / Actor</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Details</th>
                <th className="py-3 px-4 text-right">Trace & Context</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-border-subtle">
              {filteredEvents.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-text-muted text-xs">
                    No audit records match the selected filter criteria.
                  </td>
                </tr>
              ) : (
                filteredEvents.map((evt) => {
                  const isExpanded = expandedId === evt.id;
                  const isCopied = copiedTrace === evt.traceId;

                  return (
                    <React.Fragment key={evt.id}>
                      <tr className="hover:bg-slate-inset-hover transition-colors duration-[var(--duration-fast)]">
                        <td className="py-3 px-4 text-slate-text-muted num-clinical text-[11px] whitespace-nowrap">
                          {evt.timestamp}
                        </td>
                        <td className="py-3 px-4 font-semibold text-slate-text-primary">
                          {evt.user}
                        </td>
                        <td className="py-3 px-4">{getActionBadge(evt.action)}</td>
                        <td className="py-3 px-4">{getSeverityBadge(evt.severity)}</td>
                        <td className="py-3 px-4 text-slate-text-secondary max-w-xs truncate">
                          {evt.details}
                        </td>
                        <td className="py-3 px-4 text-right whitespace-nowrap">
                          <div className="flex items-center justify-end space-x-2">
                            {evt.traceId && (
                              <button
                                onClick={() => handleCopyTrace(evt.traceId)}
                                title={`Copy Trace ID: ${evt.traceId}`}
                                className="p-1 rounded text-slate-text-muted hover:text-[var(--color-clinical-400)] hover:bg-[var(--color-clinical-950)] transition-colors duration-[var(--duration-fast)] focus-clinical"
                              >
                                {isCopied ? (
                                  <Check className="w-3.5 h-3.5 text-[var(--color-safety-success)]" />
                                ) : (
                                  <Copy className="w-3.5 h-3.5" />
                                )}
                              </button>
                            )}
                            <button
                              onClick={() => setExpandedId(isExpanded ? null : evt.id)}
                              className="p-1 rounded text-slate-text-muted hover:text-slate-text-primary transition-colors duration-[var(--duration-fast)] focus-clinical"
                            >
                              {isExpanded ? (
                                <ChevronUp className="w-3.5 h-3.5" />
                              ) : (
                                <ChevronDown className="w-3.5 h-3.5" />
                              )}
                            </button>
                          </div>
                        </td>
                      </tr>

                      {isExpanded && (
                        <tr className="bg-slate-inset">
                          <td colSpan={6} className="p-4 border-b border-slate-border">
                            <div className="rounded-[var(--radius-md)] border border-slate-border bg-slate-surface p-4 space-y-3">
                              <div className="flex items-center justify-between">
                                <span className="font-semibold text-xs text-slate-text-primary flex items-center gap-1.5">
                                  <Code className="w-3.5 h-3.5 text-[var(--color-clinical-400)]" />
                                  Structured Audit Payload
                                </span>
                                {evt.traceId && (
                                  <span className="num-clinical text-[11px] text-slate-text-muted bg-slate-inset px-2 py-0.5 rounded">
                                    Trace Session ID: {evt.traceId}
                                  </span>
                                )}
                              </div>
                              <p className="text-xs text-slate-text-secondary">
                                {evt.details}
                              </p>
                              {evt.payload && (
                                <pre className="p-3 rounded-[var(--radius-md)] bg-slate-canvas text-slate-text-primary num-clinical text-[11px] overflow-x-auto">
                                  {JSON.stringify(evt.payload, null, 2)}
                                </pre>
                              )}
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Governance & Architectural Integrity Notice */}
      <div className="p-4 rounded-[var(--radius-lg)] bg-slate-canvas border border-slate-border flex items-start space-x-3 text-xs text-slate-text-secondary">
        <Info className="w-5 h-5 text-[var(--color-clinical-400)] shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-semibold text-slate-text-primary">
            Audit Trail Data Provenance & Cryptographic Boundary Notice
          </p>
          <p>
            The audit trail presented here is a read-only presentation viewer. In production, immutable audit streams are generated and signed directly by the backend clinical pipeline via the telemetry loggers. The frontend presentation viewer provides filtering, CSV/JSON export, and correlated trace ID inspection.
          </p>
        </div>
      </div>
    </div>
  );
}

import React, { useEffect, useState } from 'react';
import { Activity, FileCheck, FileText, RefreshCw, Shield } from 'lucide-react';
import { adminApi } from '@/api/adminApi';
import { AdminDashboardData, StewardshipPolicy } from '@/types';
import { MicroserviceHealthPanel } from './MicroserviceHealthPanel';
import { AuditLogPanel } from './AuditLogPanel';
import { StewardshipGovernancePanel } from './StewardshipGovernancePanel';
import { SafetyAlert } from '@/components/ui/SafetyAlert';

type GovernanceView = 'health' | 'audit' | 'stewardship';

export function GovernanceTelemetryView() {
  const [activeView, setActiveView] = useState<GovernanceView>('health');
  const [data, setData] = useState<AdminDashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAdminData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      setData(await adminApi.getAdminDashboardData());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch system health and governance data.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void fetchAdminData();
  }, []);

  const handleUpdatePolicy = async (policyId: string, updates: Partial<StewardshipPolicy>) => {
    await adminApi.updateStewardshipPolicy(policyId, updates);
    await fetchAdminData();
  };

  return (
    <div className="space-y-6" id="governance-telemetry">
      <div className="rounded-[var(--radius-lg)] border border-[var(--color-clinical-800)] bg-[var(--color-clinical-950)] p-6">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-[var(--color-clinical-300)]" aria-hidden="true" />
              <h1 className="text-xl font-bold text-slate-text-primary">System health & governance</h1>
            </div>
            <p className="mt-1 text-xs text-[var(--color-clinical-200)]">
              Operational telemetry, audit records, and stewardship policy governance.
            </p>
          </div>
          <button
            type="button"
            onClick={() => void fetchAdminData()}
            disabled={isLoading}
            className="focus-clinical inline-flex items-center gap-1.5 self-start rounded-[var(--radius-md)] border border-[var(--color-clinical-700)] bg-[var(--color-clinical-900)]/60 px-3 py-2 text-xs font-semibold text-[var(--color-clinical-200)] hover:bg-[var(--color-clinical-900)] disabled:opacity-50 md:self-auto"
            title="Refresh system health and governance data"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} aria-hidden="true" />
            Refresh
          </button>
        </div>
      </div>

      {error && <SafetyAlert level="warning" title="Some governance data is unavailable">{error}</SafetyAlert>}

      <div className="flex w-fit max-w-full items-center gap-1.5 overflow-x-auto rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-1.5">
        <button type="button" onClick={() => setActiveView('health')} className={`inline-flex items-center gap-2 whitespace-nowrap rounded-[var(--radius-md)] px-4 py-2.5 text-xs font-semibold ${activeView === 'health' ? 'bg-[var(--color-clinical-600)] text-white' : 'text-slate-text-secondary hover:bg-slate-inset-hover'}`}>
          <Activity className="h-3.5 w-3.5" aria-hidden="true" />
          System health & SLAs
        </button>
        <button type="button" onClick={() => setActiveView('audit')} className={`inline-flex items-center gap-2 whitespace-nowrap rounded-[var(--radius-md)] px-4 py-2.5 text-xs font-semibold ${activeView === 'audit' ? 'bg-[var(--color-clinical-600)] text-white' : 'text-slate-text-secondary hover:bg-slate-inset-hover'}`}>
          <FileText className="h-3.5 w-3.5" aria-hidden="true" />
          Platform audit trail
        </button>
        <button type="button" onClick={() => setActiveView('stewardship')} className={`inline-flex items-center gap-2 whitespace-nowrap rounded-[var(--radius-md)] px-4 py-2.5 text-xs font-semibold ${activeView === 'stewardship' ? 'bg-[var(--color-clinical-600)] text-white' : 'text-slate-text-secondary hover:bg-slate-inset-hover'}`}>
          <FileCheck className="h-3.5 w-3.5" aria-hidden="true" />
          Stewardship policy governance
        </button>
      </div>

      {activeView === 'health' && <MicroserviceHealthPanel components={data?.systemHealth || []} onRefresh={fetchAdminData} isLoading={isLoading} />}
      {activeView === 'audit' && <AuditLogPanel auditEvents={data?.auditTrail || []} isLoading={isLoading} />}
      {activeView === 'stewardship' && <StewardshipGovernancePanel policies={data?.stewardshipPolicies || []} knowledgeSources={data?.knowledgeSourceStatus || []} metrics={data?.governanceMetrics || []} onUpdatePolicy={handleUpdatePolicy} isLoading={isLoading} />}
    </div>
  );
}

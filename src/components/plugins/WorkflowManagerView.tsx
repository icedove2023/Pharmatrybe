import React, { useEffect, useMemo, useState } from 'react';
import { usePluginRegistry } from '@/hooks/usePluginRegistry';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { ClinicalButton } from '@/components/ui/ClinicalButton';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { pipelineApi } from '@/api';
import { ApiClientError } from '@/api/client';
import { useClinicalCaseStore } from '@/stores/clinicalCaseStore';

interface WorkflowManagerViewProps {
  caseId?: string;
  patientId?: string;
}

/**
 * Minimal Workflow Manager UI:
 * - lists available plugins (from registry)
 * - allows selecting plugins or leaving autoselect
 * - lets user choose sync vs async execution
 * - launches pipeline and displays summary + JSON details
 *
 * Enhancements:
 * - Renders per-plugin input forms when plugin.metadata.inputSchema exists (JSON Schema-like)
 * - Prefills form fields from the current clinical case store when keys match
 * - Builds input_payload from selected plugin inputs or from the case data
 *
 * This conservative scaffold intentionally avoids fabricating data and
 * surfaces server capability errors as explicit messages.
 */
export function WorkflowManagerView({ caseId, patientId }: WorkflowManagerViewProps) {
  const { data: plugins, isLoading } = usePluginRegistry();
  const caseData = useClinicalCaseStore((s) => s.caseData);
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const [executionMode, setExecutionMode] = useState<'sync' | 'async'>('sync');
  const [isRunning, setIsRunning] = useState(false);
  const [executionId, setExecutionId] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showRaw, setShowRaw] = useState(false);
  const [pluginInputs, setPluginInputs] = useState<Record<string, Record<string, any>>>({});

  useEffect(() => {
    if (!plugins) return;
    // initialize selection map without mutating plugin objects
    const initial: Record<string, boolean> = {};
    plugins.forEach((p: any) => { initial[p.id] = false; });
    setSelected(initial);
  }, [plugins]);

  useEffect(() => {
    // prefill pluginInputs for plugins that expose metadata.inputSchema
    if (!plugins) return;
    const prefill: Record<string, Record<string, any>> = {};
    plugins.forEach((p: any) => {
      const schema = p.metadata?.inputSchema;
      if (schema && schema.properties) {
        const values: Record<string, any> = {};
        Object.keys(schema.properties).forEach((k) => {
          // Prefill from caseData if matching key exists in case
          const maybe = (caseData as any)[k] ?? (caseData.presentation as any)?.[k] ?? (caseData.laboratory as any)?.[k] ?? (caseData.riskFactors as any)?.[k];
          values[k] = maybe ?? schema.properties[k].default ?? null;
        });
        prefill[p.id] = values;
      }
    });
    setPluginInputs((prev) => ({ ...prefill, ...prev }));
  }, [plugins, caseData]);

  const selectedPlugins = useMemo(() => {
    if (!plugins) return [];
    return plugins.filter((p: any) => selected[p.id]);
  }, [plugins, selected]);

  const toggleSelect = (pluginId: string) => {
    setSelected((s) => ({ ...s, [pluginId]: !s[pluginId] }));
  };

  const updatePluginInput = (pluginId: string, key: string, value: any) => {
    setPluginInputs((prev) => ({ ...prev, [pluginId]: { ...(prev[pluginId] || {}), [key]: value } }));
  };

  const buildInputPayload = (): Record<string, any> => {
    // If specific plugin inputs are present, include them keyed by plugin
    const payload: Record<string, any> = {};
    if (Object.keys(pluginInputs).length > 0) {
      Object.entries(pluginInputs).forEach(([pluginId, inputs]) => {
        if (Object.keys(inputs).length > 0) payload[pluginId] = inputs;
      });
    }
    // Always include the canonical caseData under 'case' for plugin consumption
    payload.case = caseData;
    return payload;
  };

  const launch = async () => {
    setError(null);
    setIsRunning(true);
    setResult(null);
    setExecutionId(null);

    const plugin_selection = selectedPlugins.length > 0
      ? selectedPlugins.map((p: any) => ({ plugin_id: p.id, plugin_version: p.version, plugin_role: p.category }))
      : undefined; // allow server autoselect when undefined

    try {
      const payload = {
        execution_mode: executionMode,
        patient_id: patientId ?? caseData?.demographics?.patientId,
        case_id: caseId ?? null,
        plugin_selection,
        input_payload: buildInputPayload(),
        response_mode: 'full',
      };

      const resp = await pipelineApi.executePipeline(payload as any);

      // If accepted, start polling
      if ((resp as any).status === 'accepted') {
        const accepted = resp as any;
        setExecutionId(accepted.execution_id);

        // poll
        let cancelled = false;
        const poll = async () => {
          try {
            const statusResp = await pipelineApi.getExecutionStatus(accepted.execution_id);
            if ((statusResp as any).status && (statusResp as any).status !== 'running') {
              setResult(statusResp);
              setIsRunning(false);
              cancelled = true;
            } else if ((statusResp as any).recommendation) {
              setResult(statusResp);
              setIsRunning(false);
              cancelled = true;
            }
          } catch (e) {
            // surface error but keep polling lightly
            setError((e as Error).message);
            setIsRunning(false);
            cancelled = true;
          }
        };

        // simple polling loop with limited attempts
        let attempts = 0;
        const interval = setInterval(async () => {
          if (cancelled || attempts > 60) {
            clearInterval(interval);
            if (!result && !error) setIsRunning(false);
            return;
          }
          attempts += 1;
          await poll();
        }, 2000);

      } else if ((resp as any).recommendation) {
        setResult(resp);
        setIsRunning(false);
      } else {
        setResult(resp);
        setIsRunning(false);
      }
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(`Backend error (${err.status}): ${err.message}`);
      } else {
        setError((err as Error).message);
      }
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Workflow Manager</h2>
        <div className="flex items-center gap-2">
          <label className="text-xs text-slate-text-muted flex items-center gap-2">
            <input
              type="radio"
              name="execMode"
              checked={executionMode === 'sync'}
              onChange={() => setExecutionMode('sync')}
            />
            <span>Sync</span>
          </label>
          <label className="text-xs text-slate-text-muted flex items-center gap-2">
            <input
              type="radio"
              name="execMode"
              checked={executionMode === 'async'}
              onChange={() => setExecutionMode('async')}
            />
            <span>Async</span>
          </label>
        </div>
      </div>

      <div className="rounded-[var(--radius-lg)] border border-slate-border p-4">
        <p className="text-xs text-slate-text-muted">Select plugins to include in this execution. Leave none selected to let the server autoselect active plugins.</p>

        {isLoading && <p className="text-sm text-slate-text-muted">Loading plugin registry…</p>}

        {!isLoading && (!plugins || plugins.length === 0) && (
          <SafetyAlert level="warning" title="No plugins available">
            The server plugin registry returned no plugins. Pipeline orchestration requires at least one active plugin to produce predictions.
          </SafetyAlert>
        )}

        <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {plugins?.map((p: any) => (
            <div key={p.id} className="flex items-center justify-between rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3">
              <div>
                <div className="flex items-center gap-2">
                  <div className="text-sm font-semibold">{p.name}</div>
                  <StatusBadge tone={p.type === 'PREDICTION' ? 'clinical' : 'success'}>{p.type}</StatusBadge>
                </div>
                <div className="text-xs text-slate-text-muted">v{p.version} · {p.id}</div>
              </div>
              <div>
                <input type="checkbox" checked={!!selected[p.id]} onChange={() => toggleSelect(p.id)} />
              </div>
            </div>
          ))}
        </div>

        {/* Dynamic plugin input forms */}
        {selectedPlugins.length > 0 && (
          <div className="mt-4 space-y-3">
            <div className="text-sm font-semibold">Plugin inputs</div>
            {selectedPlugins.map((p: any) => {
              const schema = p.metadata?.inputSchema;
              const inputs = pluginInputs[p.id] || {};
              if (!schema) {
                return (
                  <div key={p.id} className="rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3">
                    <div className="text-xs font-semibold">{p.name}</div>
                    <p className="text-xs text-slate-text-muted">No input schema exposed by this plugin. The server will determine required inputs.</p>
                  </div>
                );
              }

              return (
                <div key={p.id} className="rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3">
                  <div className="text-xs font-semibold">{p.name} inputs</div>
                  <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                    {Object.entries(schema.properties).map(([key, def]: any) => {
                      const type = def.type || 'string';
                      const value = inputs[key] ?? '';
                      if (type === 'boolean') {
                        return (
                          <label key={key} className="flex items-center gap-2 text-xs">
                            <input type="checkbox" checked={!!value} onChange={(e) => updatePluginInput(p.id, key, e.target.checked)} />
                            <span>{def.title || key}</span>
                          </label>
                        );
                      }
                      if (def.enum) {
                        return (
                          <label key={key} className="text-xs">
                            <div className="mb-1 text-[11px] text-slate-text-muted">{def.title || key}</div>
                            <select className="w-full rounded border p-2 text-sm" value={value} onChange={(e) => updatePluginInput(p.id, key, e.target.value)}>
                              <option value="">(select)</option>
                              {def.enum.map((opt: any) => (<option key={opt} value={opt}>{opt}</option>))}
                            </select>
                          </label>
                        );
                      }
                      return (
                        <label key={key} className="text-xs">
                          <div className="mb-1 text-[11px] text-slate-text-muted">{def.title || key}</div>
                          <input
                            type={type === 'number' ? 'number' : 'text'}
                            value={value}
                            onChange={(e) => updatePluginInput(p.id, key, type === 'number' ? Number(e.target.value) : e.target.value)}
                            className="w-full rounded border p-2 text-sm"
                          />
                        </label>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <div className="mt-4 flex items-center gap-3">
          <ClinicalButton onClick={launch} loading={isRunning} icon={undefined}>
            Launch pipeline
          </ClinicalButton>
          <ClinicalButton variant="outline" onClick={() => { setSelected({}); setResult(null); setError(null); setExecutionId(null); setPluginInputs({}); }}>
            Reset
          </ClinicalButton>
        </div>

        {error && (
          <div className="mt-4">
            <SafetyAlert level="critical" title="Pipeline execution error">
              <p className="text-xs">{error}</p>
            </SafetyAlert>
          </div>
        )}

        {executionId && (
          <div className="mt-4 text-xs text-slate-text-muted">Execution ID: {executionId}</div>
        )}

        {result && (
          <div className="mt-4 space-y-3">
            <div className="rounded-[var(--radius-md)] border border-slate-border bg-slate-surface p-3">
              <div className="text-sm font-semibold">Execution result</div>
              <div className="text-xs text-slate-text-muted mt-1">Patient: {result.patient_id || patientId || 'unknown'}</div>

              {result.recommendation && (
                <div className="mt-2">
                  <div className="text-xs font-semibold">Primary recommendation</div>
                  <div className="text-sm font-medium">{result.recommendation.primary_recommendation?.antibiotic_name || 'Not provided'}</div>
                  <div className="text-xs text-slate-text-muted">Confidence: {result.confidence || result.recommendation?.confidence || 'unknown'}</div>
                </div>
              )}

              <div className="mt-3">
                <button className="text-xs text-slate-text-primary underline" onClick={() => setShowRaw((s) => !s)}>{showRaw ? 'Hide' : 'Show'} full response</button>
              </div>
            </div>

            {showRaw && (
              <pre className="max-h-96 overflow-auto rounded-[var(--radius-sm)] bg-black/5 p-3 text-xs">{JSON.stringify(result, null, 2)}</pre>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

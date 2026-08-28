import React from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { Info, Clock, User } from 'lucide-react';
import { usePluginRegistry } from '@/hooks/usePluginRegistry';
import { getPluginNavMeta } from '@/lib/pluginNav';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { SkeletonCard } from '@/components/ui/Skeleton';

interface PluginExplorerViewProps {
  pluginId: string;
}

/**
 * Fallback explorer for any backend-registered plugin without a specialized
 * UI (e.g. additional KNOWLEDGE-type guideline sources beyond WHO AWaRe).
 * Shows only real registry metadata — no fabricated capabilities, status,
 * or content — and is honest about not yet having a dedicated experience.
 */
export function PluginExplorerView({ pluginId }: PluginExplorerViewProps) {
  const { data: plugins, isLoading } = usePluginRegistry();
  const prefersReducedMotion = useReducedMotion();

  if (isLoading) return <SkeletonCard lines={4} />;

  const plugin = plugins?.find((p) => p.id === pluginId);

  if (!plugin) {
    return (
      <SafetyAlert level="warning" title="Plugin not found in registry">
        No registered plugin with id "{pluginId}" was returned by the backend.
      </SafetyAlert>
    );
  }

  const meta = getPluginNavMeta(plugin);
  const Icon = meta.icon;

  return (
    <motion.div
      initial={prefersReducedMotion ? false : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="space-y-6"
    >
      <div className="flex flex-col justify-between gap-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6 md:flex-row md:items-center">
        <div className="flex items-start gap-3">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-clinical-950)] text-[var(--color-clinical-300)]">
            <Icon className="h-5 w-5" aria-hidden="true" />
          </div>
          <div>
            <div className="mb-1 flex flex-wrap items-center gap-1.5">
              <StatusBadge tone={plugin.type === 'PREDICTION' ? 'clinical' : 'success'}>
                {plugin.type === 'PREDICTION' ? 'Prediction' : plugin.type === 'KNOWLEDGE' ? 'Knowledge' : plugin.type}
              </StatusBadge>
              <StatusBadge tone={plugin.status === 'Active' ? 'success' : plugin.status === 'Degraded' ? 'warning' : 'neutral'}>
                {plugin.status}
              </StatusBadge>
            </div>
            <h2 className="text-lg font-semibold text-slate-text-primary">{plugin.name}</h2>
            <p className="mt-0.5 text-xs text-slate-text-muted">{plugin.description}</p>
          </div>
        </div>
      </div>

      <SafetyAlert level="info" title="Specialized explorer not yet available">
        This plugin is registered and reporting real metadata below, but a dedicated clinical explorer
        interface for it hasn't been built yet. It surfaces here rather than being silently hidden from
        navigation.
      </SafetyAlert>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="space-y-1 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3.5">
          <p className="flex items-center text-[10px] font-semibold uppercase text-slate-text-muted">
            <User className="mr-1 h-3 w-3" aria-hidden="true" /> Provenance
          </p>
          <p className="text-xs font-semibold text-slate-text-primary">{plugin.author}</p>
        </div>
        <div className="space-y-1 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3.5">
          <p className="text-[10px] font-semibold uppercase text-slate-text-muted">Version</p>
          <p className="num-clinical text-xs font-semibold text-slate-text-primary">{plugin.version}</p>
        </div>
        {typeof plugin.executionTimeMs === 'number' && (
          <div className="space-y-1 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3.5">
            <p className="flex items-center text-[10px] font-semibold uppercase text-slate-text-muted">
              <Clock className="mr-1 h-3 w-3" aria-hidden="true" /> Typical latency
            </p>
            <p className="num-clinical text-xs font-semibold text-slate-text-primary">{plugin.executionTimeMs} ms</p>
          </div>
        )}
        <div className="space-y-1 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3.5">
          <p className="flex items-center text-[10px] font-semibold uppercase text-slate-text-muted">
            <Info className="mr-1 h-3 w-3" aria-hidden="true" /> Registry ID
          </p>
          <p className="num-clinical text-xs font-semibold text-slate-text-primary">{plugin.id}</p>
        </div>
      </div>

      {plugin.capabilities && plugin.capabilities.length > 0 && (
        <div className="space-y-2 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-text-secondary">Reported capabilities</p>
          <div className="flex flex-wrap gap-1.5">
            {plugin.capabilities.map((cap) => (
              <span key={cap} className="num-clinical rounded-[var(--radius-sm)] border border-slate-border-subtle bg-slate-inset px-2 py-1 text-[11px] text-slate-text-secondary">
                {cap}
              </span>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}

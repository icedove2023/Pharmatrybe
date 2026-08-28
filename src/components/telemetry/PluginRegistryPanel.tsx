import React, { useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import {
  Layers, Search, Info, Cpu, HelpCircle, Puzzle,
} from 'lucide-react';
import {
  getExternalRegisteredPlugins, getInbuiltPlatformComponents,
} from '@/plugins/registry/pluginRegistry';
import { PluginDefinition } from '@/plugins/registry/pluginTypes';
import { getPluginStatusPresentation, getCategoryBadge } from '@/plugins/registry/pluginStatus';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { Accordion } from '@/components/ui/Accordion';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { cn } from '@/lib/utils';

function PluginDetailCard({ plugin }: { plugin: PluginDefinition }) {
  const statusMeta = getPluginStatusPresentation(plugin.status);
  const categoryMeta = getCategoryBadge(plugin.category);

  return (
    <div className="space-y-6 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6">
      <div className="space-y-2 border-b border-slate-border-subtle pb-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <span className={cn('rounded-full border px-2.5 py-0.5 text-xs font-semibold', categoryMeta.badgeClass)}>
              {categoryMeta.label}
            </span>
            {plugin.isCore && (
              <span className="rounded bg-slate-inset px-2 py-0.5 text-[10px] font-semibold uppercase text-slate-text-secondary">
                Platform core
              </span>
            )}
          </div>
          <div className="num-clinical flex items-center space-x-1.5 text-xs text-slate-text-muted">
            <span>ID:</span>
            <span className="font-semibold text-slate-text-primary">{plugin.id}</span>
          </div>
        </div>

        <h3 className="text-lg font-semibold text-slate-text-primary">{plugin.name}</h3>
        <p className="text-xs font-medium text-[var(--color-clinical-400)]">{plugin.role}</p>
      </div>

      <div className="flex items-center justify-between rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3.5">
        <div>
          <p className="text-[10px] font-semibold uppercase text-slate-text-muted">Runtime status</p>
          <div className="mt-0.5 flex items-center space-x-2">
            <span className={cn('h-2 w-2 rounded-full', statusMeta.dotClass)} />
            <span className="text-xs font-semibold text-slate-text-primary">{statusMeta.label}</span>
          </div>
        </div>
        <span className="max-w-xs text-right text-[10px] text-slate-text-muted">{statusMeta.description}</span>
      </div>

      <div className="space-y-1.5 text-xs">
        <h4 className="text-[10px] font-semibold uppercase tracking-wide text-slate-text-muted">Description & scope</h4>
        <p className="leading-relaxed text-slate-text-secondary">{plugin.description}</p>
      </div>

      <div className="grid grid-cols-2 gap-3 pt-1 text-xs sm:grid-cols-3">
        <div className="rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3">
          <p className="text-[10px] font-semibold uppercase text-slate-text-muted">Plugin version</p>
          <p className="num-clinical mt-0.5 font-semibold text-slate-text-primary">{plugin.version || 'v1.0.0'}</p>
        </div>
        <div className="rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3">
          <p className="text-[10px] font-semibold uppercase text-slate-text-muted">Model / engine release</p>
          <p className="num-clinical mt-0.5 font-semibold text-slate-text-primary">{plugin.modelVersion || 'Release 1.0'}</p>
        </div>
        <div className="col-span-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3 sm:col-span-1">
          <p className="text-[10px] font-semibold uppercase text-slate-text-muted">Knowledge / model source</p>
          <p className="mt-0.5 truncate font-medium text-slate-text-primary" title={plugin.source}>
            {plugin.source || 'PharmaTrybe clinical knowledge'}
          </p>
        </div>
      </div>

      <div className="space-y-2 text-xs">
        <h4 className="text-[10px] font-semibold uppercase tracking-wide text-slate-text-muted">
          Exposed capabilities ({plugin.capabilities.length})
        </h4>
        <div className="flex flex-wrap gap-1.5">
          {plugin.capabilities.map((cap, idx) => (
            <span key={idx} className="num-clinical rounded-[var(--radius-md)] border border-[var(--color-clinical-700)] bg-[var(--color-clinical-950)] px-2.5 py-1 text-[11px] text-[var(--color-clinical-300)]">
              {cap}
            </span>
          ))}
        </div>
      </div>

      {plugin.metadata && Object.keys(plugin.metadata).length > 0 && (
        <div className="space-y-2 border-t border-slate-border-subtle pt-2 text-xs">
          <h4 className="text-[10px] font-semibold uppercase tracking-wide text-slate-text-muted">Integration architecture parameters</h4>
          <div className="grid grid-cols-1 gap-2 text-[11px] sm:grid-cols-2">
            {Object.entries(plugin.metadata).map(([k, v]) => (
              <div key={k} className="rounded-[var(--radius-md)] bg-slate-inset p-2 text-slate-text-secondary">
                <span className="capitalize text-slate-text-muted">{k.replace(/([A-Z])/g, ' $1')}: </span>
                <strong className="text-slate-text-primary">{Array.isArray(v) ? v.join(', ') : String(v)}</strong>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function PluginRegistryPanel() {
  const [searchQuery, setSearchQuery] = useState('');
  const externalPlugins = getExternalRegisteredPlugins();
  const inbuiltComponents = getInbuiltPlatformComponents();

  const [selectedPluginId, setSelectedPluginId] = useState<string>('');

  const filteredExternal = externalPlugins.filter((p) => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return true;
    return p.name.toLowerCase().includes(q) || p.role.toLowerCase().includes(q) || p.description.toLowerCase().includes(q);
  });

  const selectedPlugin = externalPlugins.find((p) => p.id === selectedPluginId);

  return (
    <div className="space-y-6">
      <SafetyAlert level="warning" title="Clinical safety & architectural boundary notice">
        This information supports clinical decision-making; it does not replace clinician judgement. Frontend
        registry metadata represents known system components. Live backend status is not exposed via standalone
        endpoints and is consumed exclusively through the canonical recommendation pipeline.
      </SafetyAlert>

      {/* Header */}
      <div className="flex flex-col justify-between gap-4 rounded-[var(--radius-lg)] border border-[var(--color-clinical-800)] bg-[var(--color-clinical-950)] p-6 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center space-x-2">
            <Puzzle className="h-5 w-5 text-[var(--color-clinical-400)]" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-slate-text-primary">Registered plugin architecture</h2>
          </div>
          <p className="mt-1 text-xs text-[var(--color-clinical-200)]">
            Externally registered knowledge & prediction capabilities participating in decision fusion.
          </p>
        </div>
        <span className="num-clinical rounded-[var(--radius-md)] border border-[var(--color-clinical-700)] bg-[var(--color-clinical-900)]/60 px-3 py-1.5 text-[11px] font-semibold text-[var(--color-clinical-200)]">
          {externalPlugins.length} registered plugins
        </span>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
        <input
          type="text"
          id="plugin-registry-search"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by plugin name, capability, or role…"
          className="focus-clinical w-full rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface py-2.5 pl-10 pr-4 text-xs text-slate-text-primary placeholder-slate-text-muted"
        />
      </div>

      {/* Main Grid: Registered Plugins List & Detail */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="space-y-2.5 lg:col-span-5">
          <div className="px-1 text-xs font-semibold uppercase tracking-wide text-slate-text-muted">
            Registered plugins ({filteredExternal.length})
          </div>

          {filteredExternal.length === 0 ? (
            <div className="space-y-2 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-8 text-center">
              <HelpCircle className="mx-auto h-6 w-6 text-slate-text-muted" aria-hidden="true" />
              <p className="text-xs font-medium text-slate-text-muted">No plugins match your search.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredExternal.map((plugin) => {
                const isSelected = selectedPlugin?.id === plugin.id;
                const statusMeta = getPluginStatusPresentation(plugin.status);
                const categoryMeta = getCategoryBadge(plugin.category);

                return (
                  <React.Fragment key={plugin.id}>
                    <button
                      type="button"
                      id={`plugin-card-${plugin.id}`}
                      onClick={() => setSelectedPluginId(plugin.id)}
                      className={cn(
                        'w-full rounded-[var(--radius-lg)] border p-3.5 text-left transition-colors duration-[var(--duration-fast)]',
                        isSelected ? 'border-[var(--color-clinical-600)] bg-[var(--color-clinical-950)]/60' : 'border-slate-border bg-slate-surface hover:border-slate-border',
                      )}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="truncate text-xs font-semibold text-slate-text-primary">{plugin.name}</span>
                        <span className={cn('rounded-full border px-2 py-0.5 text-[10px] font-semibold', categoryMeta.badgeClass)}>{categoryMeta.label}</span>
                      </div>
                      <p className="mt-1 line-clamp-2 text-[11px] text-slate-text-secondary">{plugin.role}</p>
                      <div className="mt-2.5 flex items-center justify-between border-t border-slate-border-subtle pt-2 text-[10px] text-slate-text-muted">
                        <span className="num-clinical">v{plugin.version || '1.0.0'}</span>
                        <span className="flex items-center space-x-1">
                          <span className={cn('h-1.5 w-1.5 rounded-full', statusMeta.dotClass)} />
                          <span>{statusMeta.label}</span>
                        </span>
                      </div>
                    </button>

                    <AnimatePresence initial={false}>
                      {isSelected && (
                        <motion.div
                          initial={{ opacity: 0, height: 0, y: -8 }}
                          animate={{ opacity: 1, height: 'auto', y: 0 }}
                          exit={{ opacity: 0, height: 0, y: -8 }}
                          transition={{ duration: 0.2, ease: [0.2, 0.8, 0.2, 1] }}
                          className="overflow-hidden"
                        >
                          <div className="pt-2">
                            <PluginDetailCard plugin={plugin} />
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </React.Fragment>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Inbuilt Platform Components — explicitly NOT registered plugins */}
      <Accordion
        title="Platform architecture components"
        subtitle="Clinical Rules, Decision Fusion, Explainability, and Audit & Telemetry — inbuilt, not registered plugins"
        icon={Cpu}
      >
        <div className="space-y-2">
          <div className="mb-3 flex items-start gap-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3 text-[11px] text-slate-text-muted">
            <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
            <span>
              These are architectural components of the CDSS platform itself, not externally registered or
              swappable plugins. They cannot be disabled or replaced through the plugin registry.
            </span>
          </div>
          {inbuiltComponents.map((component) => {
            const categoryMeta = getCategoryBadge(component.category);
            return (
              <div key={component.id} className="flex items-center justify-between rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset/20 p-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className={cn('rounded-full border px-2 py-0.5 text-[10px] font-semibold', categoryMeta.badgeClass)}>{categoryMeta.label}</span>
                    <span className="truncate text-xs font-semibold text-slate-text-primary">{component.name}</span>
                  </div>
                  <p className="mt-0.5 truncate text-[11px] text-slate-text-muted">{component.role}</p>
                </div>
                <StatusBadge tone="neutral">Inbuilt</StatusBadge>
              </div>
            );
          })}
        </div>
      </Accordion>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'motion/react';
import { TestTube2, Sparkles, BarChart2 } from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell, Legend,
} from 'recharts';
import { ArmdModelSummary, ArmdModelDetail } from '@/types';
import { armdApi } from '@/api/armdApi';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { SkeletonCard, Skeleton } from '@/components/ui/Skeleton';
import { cn } from '@/lib/utils';

export function ARMDExplorer() {
  const [models, setModels] = useState<ArmdModelSummary[]>([]);
  const [selectedModelId, setSelectedModelId] = useState<string>('ecoli_cipro');
  const [modelDetail, setModelDetail] = useState<ArmdModelDetail | null>(null);
  const [isLoadingList, setIsLoadingList] = useState<boolean>(true);
  const [isLoadingDetail, setIsLoadingDetail] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const prefersReducedMotion = useReducedMotion();

  useEffect(() => {
    let isMounted = true;
    async function loadModels() {
      try {
        setIsLoadingList(true);
        const data = await armdApi.getArmdModels();
        if (isMounted) {
          setModels(data);
          if (data.length > 0 && !selectedModelId) setSelectedModelId(data[0].id);
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load ARMD models.');
      } finally {
        if (isMounted) setIsLoadingList(false);
      }
    }
    loadModels();
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedModelId) return;
    let isMounted = true;
    async function loadDetail() {
      try {
        setIsLoadingDetail(true);
        const detail = await armdApi.getArmdModelDetails(selectedModelId);
        if (isMounted) setModelDetail(detail);
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load model details.');
      } finally {
        if (isMounted) setIsLoadingDetail(false);
      }
    }
    loadDetail();
    return () => {
      isMounted = false;
    };
  }, [selectedModelId]);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col justify-between gap-4 rounded-[var(--radius-lg)] border border-[var(--color-clinical-800)] bg-gradient-to-br from-[var(--color-clinical-950)] to-slate-canvas p-6 sm:flex-row sm:items-center">
        <div>
          <div className="mb-1 flex items-center space-x-2">
            <TestTube2 className="h-5 w-5 text-[var(--color-clinical-400)]" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-slate-text-primary">ARMD resistance prediction</h2>
          </div>
          <p className="text-xs text-[var(--color-clinical-200)]">
            ARMD model registry and standalone resistance outputs are not exposed by the backend.
          </p>
        </div>
        <div className="flex items-center gap-1.5">
          <StatusBadge tone="warning">Not exposed by backend</StatusBadge>
          <span className="num-clinical rounded-[var(--radius-sm)] border border-[var(--color-clinical-700)] bg-[var(--color-clinical-900)]/60 px-3 py-1.5 text-[10px] font-semibold text-[var(--color-clinical-200)]">
            Version not exposed
          </span>
        </div>
      </div>

      {error && <SafetyAlert level="warning" title="ARMD model registry error">{error}</SafetyAlert>}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left: Model Selector */}
        <div className="space-y-2 lg:col-span-4">
          <div className="px-1 text-xs font-semibold uppercase tracking-wide text-slate-text-muted">
            Trained ML models ({models.length})
          </div>

          {isLoadingList ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i}>
                  <Skeleton className="h-16 rounded-[var(--radius-md)]" />
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {models.map((m, idx) => {
                const isSelected = selectedModelId === m.id;
                return (
                  <motion.button
                    key={m.id}
                    id={`armd-model-card-${m.id}`}
                    onClick={() => setSelectedModelId(m.id)}
                    initial={prefersReducedMotion ? false : { opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.15, delay: Math.min(idx * 0.02, 0.2) }}
                    aria-current={isSelected}
                    className={cn(
                      'focus-clinical w-full rounded-[var(--radius-md)] border p-3.5 text-left transition-colors duration-[var(--duration-fast)]',
                      isSelected
                        ? 'border-[var(--color-clinical-600)] bg-[var(--color-clinical-950)]/60'
                        : 'border-slate-border-subtle bg-slate-inset hover:border-slate-border',
                    )}
                  >
                    <p className="text-xs font-semibold text-slate-text-primary">{m.name}</p>
                    <div className="mt-1.5 flex flex-wrap items-center gap-1.5 text-[11px]">
                      <span className="num-clinical rounded bg-[var(--color-clinical-950)] px-2 py-0.5 font-semibold text-[var(--color-clinical-300)]">
                        {m.targetPathogen}
                      </span>
                      <span className="rounded bg-slate-inset px-2 py-0.5 font-medium text-slate-text-secondary">
                        {m.targetDrug}
                      </span>
                    </div>
                  </motion.button>
                );
              })}
            </div>
          )}
        </div>

        {/* Right: Model Architecture & Performance Details */}
        <div className="lg:col-span-8">
          {isLoadingDetail ? (
            <SkeletonCard lines={6} />
          ) : (
            <AnimatePresence mode="wait">
              {modelDetail ? (
                <motion.div
                  key={modelDetail.id}
                  initial={prefersReducedMotion ? false : { opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={prefersReducedMotion ? undefined : { opacity: 0, y: -8 }}
                  transition={{ duration: 0.2, ease: [0.2, 0.8, 0.2, 1] }}
                  className="space-y-6"
                >
                  {/* Header Info */}
                  <div className="space-y-3 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div>
                        <span className="rounded bg-[var(--color-clinical-950)] px-2 py-0.5 text-[10px] font-semibold uppercase text-[var(--color-clinical-300)]">
                          Deep resistance transformer
                        </span>
                        <h3 className="mt-1 text-base font-semibold text-slate-text-primary">{modelDetail.name}</h3>
                      </div>
                      <div className="num-clinical text-right text-[11px] text-slate-text-muted">
                        <p>Dataset: <strong className="text-slate-text-secondary">{modelDetail.datasetSize.toLocaleString()} isolates</strong></p>
                        <p>Last trained: {modelDetail.lastTrained}</p>
                      </div>
                    </div>

                    {/* Performance Metrics Cards */}
                    <div className="grid grid-cols-2 gap-3 pt-2 sm:grid-cols-4">
                      {[
                        { label: 'AUC-ROC', value: modelDetail.performanceMetrics.aucRoc, color: 'text-[var(--color-clinical-400)]' },
                        { label: 'Precision', value: modelDetail.performanceMetrics.precision, color: 'text-[var(--color-safety-success)]' },
                        { label: 'Recall', value: modelDetail.performanceMetrics.recall, color: 'text-[var(--color-safety-success)]' },
                        { label: 'F1 score', value: modelDetail.performanceMetrics.f1Score, color: 'text-[var(--color-safety-warning)]' },
                      ].map((metric, idx) => (
                        <motion.div
                          key={metric.label}
                          initial={prefersReducedMotion ? false : { opacity: 0, scale: 0.95 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ duration: 0.2, delay: idx * 0.04 }}
                          className="rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3 text-center"
                        >
                          <p className="text-[10px] font-semibold uppercase text-slate-text-muted">{metric.label}</p>
                          <p className={`num-clinical text-lg font-bold ${metric.color}`}>{metric.value}</p>
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  {/* Feature Importance (SHAP) Chart */}
                  <div className="space-y-3 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5">
                    <div className="flex items-center justify-between">
                      <h4 className="flex items-center text-xs font-semibold uppercase tracking-wide text-slate-text-muted">
                        <Sparkles className="mr-1.5 h-3.5 w-3.5 text-[var(--color-clinical-400)]" aria-hidden="true" />
                        Model feature attributions (SHAP)
                      </h4>
                      <span className="text-[10px] text-slate-text-muted">Mean |SHAP value|</span>
                    </div>

                    <div className="h-56 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart layout="vertical" data={modelDetail.featureImportance} margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#263252" opacity={0.6} />
                          <XAxis type="number" tick={{ fontSize: 10, fill: '#7c8aa8' }} domain={[-0.5, 0.5]} />
                          <YAxis type="category" dataKey="feature" tick={{ fontSize: 10, fill: '#7c8aa8' }} width={180} />
                          <Tooltip
                            contentStyle={{ backgroundColor: '#0b1220', border: '1px solid #263252', borderRadius: '8px', color: '#eef2f8', fontSize: '11px' }}
                            formatter={(val: any) => [val, 'Feature weight']}
                          />
                          <Bar dataKey="importance" name="Weight" radius={[0, 4, 4, 0]} animationDuration={600}>
                            {modelDetail.featureImportance.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.importance >= 0 ? '#4da3f5' : '#2dd4bf'} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* MIC Shift Distribution */}
                  <div className="space-y-3 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5">
                    <div className="flex items-center justify-between">
                      <h4 className="flex items-center text-xs font-semibold uppercase tracking-wide text-slate-text-muted">
                        <BarChart2 className="mr-1.5 h-3.5 w-3.5 text-[var(--color-clinical-400)]" aria-hidden="true" />
                        MIC shift distribution (mg/L)
                      </h4>
                      <span className="text-[10px] text-slate-text-muted">Susceptible vs resistant</span>
                    </div>

                    <div className="h-56 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={modelDetail.micDistribution} margin={{ top: 10, right: 20, left: -10, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#263252" opacity={0.6} />
                          <XAxis
                            dataKey="mic"
                            tick={{ fontSize: 10, fill: '#7c8aa8' }}
                            label={{ value: 'MIC (mg/L)', position: 'insideBottom', offset: -5, fontSize: 10, fill: '#7c8aa8' }}
                          />
                          <YAxis tick={{ fontSize: 10, fill: '#7c8aa8' }} />
                          <Tooltip contentStyle={{ backgroundColor: '#0b1220', border: '1px solid #263252', borderRadius: '8px', color: '#eef2f8', fontSize: '11px' }} />
                          <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '4px' }} />
                          <Bar dataKey="susceptibleCount" name="Susceptible isolates" fill="#2e9e6e" animationDuration={600} />
                          <Bar dataKey="resistantCount" name="Resistant isolates" fill="#c4364c" animationDuration={600} animationBegin={100} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </motion.div>
              ) : null}
            </AnimatePresence>
          )}
        </div>
      </div>
    </div>
  );
}

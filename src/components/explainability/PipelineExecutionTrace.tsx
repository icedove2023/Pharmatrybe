import React, { useState } from 'react';
import { GitBranch, CheckCircle2, ShieldCheck, ArrowDown, Activity, Info, Sparkles, Layers, Zap, Pill } from 'lucide-react';
import { ReasoningNode } from '@/types';

interface PipelineExecutionTraceProps {
  nodes?: ReasoningNode[];
  traceSteps?: {
    step_id: string;
    stage_name: string;
    status: string;
    summary: string;
    execution_time_ms?: number;
  }[];
}

export function PipelineExecutionTrace({ nodes, traceSteps }: PipelineExecutionTraceProps) {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(
    nodes && nodes.length > 0 ? nodes[nodes.length - 2]?.id || nodes[0].id : null
  );

  // If both nodes and traceSteps are missing or empty
  if ((!nodes || nodes.length === 0) && (!traceSteps || traceSteps.length === 0)) {
    return (
      <div className="space-y-3 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6">
        <div className="flex items-center space-x-2">
          <GitBranch className="h-4 w-4 text-[var(--color-clinical-400)]" aria-hidden="true" />
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-text-secondary">Pipeline execution graph</h3>
        </div>
        <div className="rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-4 text-xs italic text-slate-text-muted">
          No pipeline execution trace returned by the CDSS backend for this case.
        </div>
      </div>
    );
  }

  const activeNode = nodes?.find((n) => n.id === selectedNodeId) || nodes?.[0];

  return (
    <div className="space-y-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-border-subtle pb-3">
        <div className="flex items-center space-x-2">
          <GitBranch className="h-4 w-4 text-[var(--color-clinical-400)]" aria-hidden="true" />
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-text-primary">Pipeline execution graph</h3>
        </div>
        <span className="text-[10px] text-slate-text-muted">Interactive node inspector</span>
      </div>

      {nodes && nodes.length > 0 ? (
        <div className="relative flex min-h-[380px] flex-col justify-between overflow-hidden rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-canvas p-4 text-white sm:p-5">
          {/* Subtle background grid pattern */}
          <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,#26325215_1px,transparent_1px),linear-gradient(to_bottom,#26325215_1px,transparent_1px)] bg-[size:16px_16px]" />

          {/* Interactive Graph Nodes Flow */}
          <div className="space-y-3 relative z-10">
            {/* Level 1: Clinical Case Input */}
            <div className="flex justify-center">
              {nodes[0] && (
                <button
                  type="button"
                  onClick={() => setSelectedNodeId(nodes[0].id)}
                  className={`px-4 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                    selectedNodeId === nodes[0].id
                      ? 'bg-[var(--color-clinical-600)] border-white text-white shadow-lg ring-2 ring-[var(--color-clinical-400)]'
                      : 'bg-slate-inset border-slate-border text-slate-text-secondary hover:bg-slate-inset-hover'
                  }`}
                >
                  📍 {nodes[0].label || '1. Clinical Input Request'}
                </button>
              )}
            </div>

            {/* Connecting line */}
            <div className="h-3 w-0.5 bg-[var(--color-safety-info-bg)]/40 mx-auto" />

            {/* Level 2: Knowledge Sources & Predictions */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-center">
              {nodes.slice(1, 4).map((node) => (
                <button
                  key={node.id}
                  type="button"
                  onClick={() => setSelectedNodeId(node.id)}
                  className={`p-2.5 rounded-xl text-xs font-bold border transition-all cursor-pointer text-center ${
                    selectedNodeId === node.id
                      ? 'bg-[var(--color-safety-success-bg)] border-white text-white shadow-md ring-2 ring-[var(--color-safety-success-border)]'
                      : 'bg-slate-inset border-slate-border text-slate-text-secondary hover:bg-slate-inset-hover'
                  }`}
                >
                  <span className="block truncate">{node.label || node.title}</span>
                  {node.source && (
                    <span className="block text-[10px] text-slate-text-muted num-clinical mt-0.5">
                      {node.source}
                    </span>
                  )}
                </button>
              ))}
            </div>

            {/* Connecting line */}
            <div className="h-3 w-0.5 bg-[var(--color-safety-info-bg)]/40 mx-auto" />

            {/* Level 3: Rules & Decision Fusion */}
            <div className="flex justify-center">
              {nodes[4] ? (
                <button
                  type="button"
                  onClick={() => setSelectedNodeId(nodes[4].id)}
                  className={`px-5 py-2.5 rounded-xl text-xs font-extrabold border transition-all cursor-pointer ${
                    selectedNodeId === nodes[4].id
                      ? 'bg-[var(--color-clinical-600)] border-[var(--color-safety-success-border)] text-white shadow-xl ring-2 ring-[var(--color-safety-success-border)]'
                      : 'bg-slate-inset border-slate-border text-slate-text-secondary hover:bg-slate-inset-hover'
                  }`}
                >
                  <><Zap className="mr-1.5 inline-block h-3.5 w-3.5 align-[-0.15em]" aria-hidden="true" />{nodes[4].label || 'Decision Fusion & Safety Verification'}</>
                </button>
              ) : null}
            </div>

            {/* Connecting line */}
            <div className="h-3 w-0.5 bg-[var(--color-safety-info-bg)]/40 mx-auto" />

            {/* Level 4: Final Output Regimen */}
            <div className="flex justify-center">
              {nodes[nodes.length - 1] && (
                <button
                  type="button"
                  onClick={() => setSelectedNodeId(nodes[nodes.length - 1].id)}
                  className={`px-4 py-2 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                    selectedNodeId === nodes[nodes.length - 1].id
                      ? 'bg-[var(--color-safety-success-bg)] border-white text-white shadow-lg ring-2 ring-[var(--color-safety-success-border)]'
                      : 'bg-slate-inset border-slate-border text-slate-text-secondary hover:bg-slate-inset-hover'
                  }`}
                >
                  <><Pill className="mr-1.5 inline-block h-3.5 w-3.5 align-[-0.15em]" aria-hidden="true" />{nodes[nodes.length - 1].label || 'Recommendation Package Output'}</>
                </button>
              )}
            </div>
          </div>

          {/* Active Node Detail Inspector Card */}
          {activeNode && (
            <div className="mt-4 p-3.5 rounded-xl bg-slate-canvas/95 border border-slate-border text-xs z-10 space-y-1.5 shadow-md">
              <div className="flex flex-wrap items-center justify-between gap-2 text-[var(--color-safety-success)] font-semibold">
                <div className="flex items-center space-x-1.5">
                  <Info className="w-3.5 h-3.5 text-[var(--color-safety-success)]" aria-hidden="true" />
                  <span>{activeNode.title || activeNode.label}</span>
                </div>
                <div className="flex items-center space-x-2">
                  {activeNode.source && (
                    <span className="bg-slate-inset text-slate-text-secondary px-2 py-0.5 rounded text-[10px] num-clinical border border-slate-border">
                      Source: {activeNode.source}
                    </span>
                  )}
                  {activeNode.confidence && (
                    <span className="bg-[var(--color-safety-success-bg)] text-[var(--color-safety-success)] px-2 py-0.5 rounded text-[10px] num-clinical border border-[var(--color-safety-success-border)]">
                      Weight/Conf: {activeNode.confidence}
                    </span>
                  )}
                </div>
              </div>
              <p className="text-slate-text-secondary text-xs leading-relaxed">
                {activeNode.details}
              </p>
            </div>
          )}
        </div>
      ) : (
        /* Render traceSteps list if nodes array is not present */
        <div className="space-y-2">
          {traceSteps?.map((step) => (
            <div
              key={step.step_id}
              className="flex items-center justify-between rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3 text-xs"
            >
              <div className="space-y-0.5">
                <p className="font-semibold text-slate-text-primary">{step.stage_name}</p>
                <p className="text-slate-text-muted">{step.summary}</p>
              </div>
              <span className="num-clinical rounded border border-[var(--color-safety-success-border)] bg-[var(--color-safety-success-bg)] px-2 py-0.5 text-[10px] font-semibold text-[var(--color-safety-success)]">
                {step.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

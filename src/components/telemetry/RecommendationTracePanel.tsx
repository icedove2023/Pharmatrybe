import React, { useState } from 'react';
import {
  Clock,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  ChevronDown,
  ChevronRight,
  Cpu,
  Layers,
  Terminal,
  Activity,
} from 'lucide-react';
import { RecommendationTrace, RecommendationTraceStep } from '@/types';

interface RecommendationTracePanelProps {
  trace?: RecommendationTrace | null;
}

export function RecommendationTracePanel({ trace }: RecommendationTracePanelProps) {
  const [expandedSteps, setExpandedSteps] = useState<Record<number, boolean>>({});

  const toggleStep = (stepNumber: number) => {
    setExpandedSteps((prev) => ({
      ...prev,
      [stepNumber]: !prev[stepNumber],
    }));
  };

  const steps = trace?.trace_steps || [];

  // If trace data is missing or empty, explicitly indicate it
  if (!trace || steps.length === 0) {
    return (
      <div className="p-8 text-center bg-slate-surface rounded-[var(--radius-lg)] border border-slate-border space-y-3">
        <HelpCircle className="w-8 h-8 text-slate-text-muted mx-auto" />
        <div className="space-y-1">
          <h4 className="text-sm font-semibold text-slate-text-primary">
            Trace Information Is Incomplete
          </h4>
          <p className="text-xs text-slate-text-muted max-w-md mx-auto leading-relaxed">
            Trace information is incomplete or not available for this recommendation. The backend did not return detailed execution trace steps.
          </p>
        </div>
      </div>
    );
  }

  const totalDuration = trace.total_duration_ms || steps.reduce((acc, s) => acc + (s.duration_ms || 0), 0);

  return (
    <div className="space-y-6">
      {/* Summary Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-[var(--radius-lg)] bg-slate-inset border border-slate-border-subtle">
        <div>
          <h3 className="text-sm font-semibold text-slate-text-primary flex items-center">
            <Activity className="w-4 h-4 text-[var(--color-safety-success)] mr-2" />
            Decision Pipeline Execution Trace
          </h3>
          <p className="text-xs text-slate-text-muted mt-0.5">
            Step-by-step chronological record of orchestration, prediction, rule evaluation, and decision fusion.
          </p>
        </div>

        <div className="flex items-center space-x-3 text-xs num-clinical">
          <span className="text-slate-text-muted">Total Latency:</span>
          <span className="font-semibold text-[var(--color-safety-success)] bg-[var(--color-safety-success-bg)] px-2.5 py-1 rounded-[var(--radius-md)] border border-[var(--color-safety-success-border)]">
            {totalDuration} ms
          </span>
          <span className="text-slate-text-muted">({steps.length} steps)</span>
        </div>
      </div>

      {/* Timeline Steps */}
      <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-inset">
        {steps.map((step, idx) => {
          const isExpanded = !!expandedSteps[step.step_number];
          const hasInputsOrOutputs =
            (step.inputs && Object.keys(step.inputs).length > 0) ||
            (step.outputs && Object.keys(step.outputs).length > 0);

          return (
            <div key={`trace-step-${idx}`} className="relative group">
              {/* Step indicator dot */}
              <div className="absolute -left-6 top-3 w-5 h-5 rounded-full bg-[var(--color-safety-info-bg)] text-white flex items-center justify-center text-[10px] font-semibold shadow-xs">
                {step.step_number}
              </div>

              {/* Step Content Card */}
              <div className="p-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-semibold num-clinical uppercase bg-slate-inset text-slate-text-primary px-2 py-0.5 rounded">
                      {step.phase_name}
                    </span>
                    <span className="text-xs font-semibold text-slate-text-primary">
                      {step.description}
                    </span>
                  </div>

                  <div className="flex items-center space-x-3 text-xs text-slate-text-muted">
                    <span className="num-clinical">{step.duration_ms} ms</span>
                    {step.timestamp && (
                      <span className="text-[10px] hidden sm:inline num-clinical">
                        {step.timestamp.slice(11, 19)}
                      </span>
                    )}
                  </div>
                </div>

                {/* Expand / Collapse Payload Details */}
                {hasInputsOrOutputs && (
                  <div className="pt-2 border-t border-slate-border-subtle">
                    <button
                      onClick={() => toggleStep(step.step_number)}
                      className="text-[11px] font-semibold text-[var(--color-clinical-400)] flex items-center space-x-1 hover:underline cursor-pointer"
                    >
                      {isExpanded ? (
                        <>
                          <ChevronDown className="w-3.5 h-3.5" />
                          <span>Hide Stage I/O Payloads</span>
                        </>
                      ) : (
                        <>
                          <ChevronRight className="w-3.5 h-3.5" />
                          <span>Inspect Stage I/O Payloads</span>
                        </>
                      )}
                    </button>

                    {isExpanded && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2 pt-2 text-[10px] num-clinical">
                        {step.inputs && Object.keys(step.inputs).length > 0 && (
                          <div className="p-2.5 rounded-[var(--radius-md)] bg-slate-canvas border border-slate-border overflow-x-auto">
                            <span className="text-slate-text-muted uppercase font-semibold block mb-1">Inputs</span>
                            <pre className="text-slate-text-secondary">
                              {JSON.stringify(step.inputs, null, 2)}
                            </pre>
                          </div>
                        )}
                        {step.outputs && Object.keys(step.outputs).length > 0 && (
                          <div className="p-2.5 rounded-[var(--radius-md)] bg-slate-canvas border border-slate-border overflow-x-auto">
                            <span className="text-slate-text-muted uppercase font-semibold block mb-1">Outputs</span>
                            <pre className="text-slate-text-secondary">
                              {JSON.stringify(step.outputs, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

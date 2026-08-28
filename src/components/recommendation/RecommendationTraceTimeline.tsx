import React, { useState } from 'react';
import { Activity, Clock, ChevronDown, ChevronUp, CheckCircle, Terminal } from 'lucide-react';
import { RecommendationTrace, RecommendationTraceStep } from '@/types';

interface RecommendationTraceTimelineProps {
  trace?: RecommendationTrace;
  traceStepsList?: RecommendationTraceStep[];
  totalDurationMs?: number;
}

export function RecommendationTraceTimeline({
  trace,
  traceStepsList,
  totalDurationMs,
}: RecommendationTraceTimelineProps) {
  const steps: RecommendationTraceStep[] = traceStepsList || trace?.trace_steps || [];
  const duration = totalDurationMs || trace?.total_duration_ms || 0;

  const [expandedStep, setExpandedStep] = useState<number | null>(null);

  if (steps.length === 0) {
    return (
      <div className="p-5 rounded-[var(--radius-lg)] bg-slate-surface border border-slate-border space-y-2">
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-[var(--color-clinical-400)]" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-text-primary">
            Recommendation Execution Trace
          </h3>
        </div>
        <p className="text-xs text-slate-text-muted italic p-3 bg-slate-inset rounded-[var(--radius-md)] border border-slate-border-subtle">
          No execution trace steps available.
        </p>
      </div>
    );
  }

  const toggleStep = (stepNum: number) => {
    setExpandedStep((prev) => (prev === stepNum ? null : stepNum));
  };

  return (
    <div className="p-5 rounded-[var(--radius-lg)] bg-slate-surface border border-slate-border space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-border-subtle pb-3">
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-[var(--color-clinical-400)]" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-text-primary">
            Recommendation Pipeline Execution Trace
          </h3>
        </div>
        <div className="flex items-center space-x-2 text-[11px] num-clinical text-slate-text-muted">
          <Clock className="w-3.5 h-3.5 text-[var(--color-safety-info)]" />
          <span>Total Duration:</span>
          <span className="font-semibold text-[var(--color-clinical-400)] bg-[var(--color-clinical-950)] px-2 py-0.5 rounded border border-[var(--color-clinical-700)]">
            {duration.toFixed(1)} ms
          </span>
        </div>
      </div>

      <div className="relative pl-6 space-y-3 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-inset">
        {steps.map((step) => {
          const isExpanded = expandedStep === step.step_number;
          return (
            <div key={step.step_number} className="relative group">
              {/* Step indicator circle */}
              <div className="absolute -left-6 top-2.5 w-5 h-5 rounded-full bg-slate-surface border-2 border-[var(--color-clinical-500)] flex items-center justify-center text-[9px] font-bold text-[var(--color-clinical-400)] shadow-xs">
                {step.step_number}
              </div>

              {/* Step Card */}
              <div className="p-3 rounded-[var(--radius-md)] bg-slate-inset border border-slate-border-subtle space-y-1.5 transition-colors duration-[var(--duration-fast)]">
                <div
                  onClick={() => toggleStep(step.step_number)}
                  className="flex items-center justify-between cursor-pointer"
                >
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-semibold num-clinical uppercase text-slate-text-primary">
                      {step.phase_name}
                    </span>
                    <span className="text-[10px] num-clinical text-slate-text-muted bg-slate-inset/60 px-1.5 py-0.2 rounded">
                      +{step.duration_ms.toFixed(1)}ms
                    </span>
                  </div>

                  <div className="flex items-center space-x-1 text-slate-text-muted text-xs hover:text-slate-text-primary">
                    <span className="text-[10px] hidden sm:inline">Inspect I/O</span>
                    {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </div>
                </div>

                <p className="text-xs text-slate-text-secondary">
                  {step.description}
                </p>

                {/* Inspectable Inputs / Outputs JSON */}
                {isExpanded && (
                  <div className="pt-2 border-t border-slate-border-subtle grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] num-clinical">
                    <div className="p-2 rounded bg-slate-canvas border border-slate-border space-y-1">
                      <span className="text-[10px] font-semibold text-slate-text-muted uppercase flex items-center">
                        <Terminal className="w-3 h-3 mr-1 text-[var(--color-clinical-400)]" />
                        Inputs
                      </span>
                      <pre className="text-slate-text-primary overflow-x-auto text-[10px] whitespace-pre-wrap">
                        {JSON.stringify(step.inputs, null, 2)}
                      </pre>
                    </div>

                    <div className="p-2 rounded bg-slate-canvas border border-slate-border space-y-1">
                      <span className="text-[10px] font-semibold text-slate-text-muted uppercase flex items-center">
                        <Terminal className="w-3 h-3 mr-1 text-[var(--color-safety-success)]" />
                        Outputs
                      </span>
                      <pre className="text-slate-text-primary overflow-x-auto text-[10px] whitespace-pre-wrap">
                        {JSON.stringify(step.outputs, null, 2)}
                      </pre>
                    </div>
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

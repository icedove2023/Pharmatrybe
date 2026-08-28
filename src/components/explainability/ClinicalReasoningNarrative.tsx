import React from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { Sparkles, ShieldCheck, AlertCircle } from 'lucide-react';

interface ClinicalReasoningNarrativeProps {
  narrative?: string;
  traceId?: string;
  generatedAt?: string;
}

export function ClinicalReasoningNarrative({ narrative, traceId, generatedAt }: ClinicalReasoningNarrativeProps) {
  const prefersReducedMotion = useReducedMotion();

  if (!narrative || narrative.trim() === '') {
    return (
      <div className="space-y-2 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5 text-slate-text-muted">
        <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wide text-slate-text-muted">
          <AlertCircle className="h-4 w-4" aria-hidden="true" />
          <span>Clinical reasoning narrative</span>
        </div>
        <p className="text-xs italic">No clinical reasoning narrative was returned by the CDSS backend for this assessment.</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={prefersReducedMotion ? false : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28, ease: [0.2, 0.8, 0.2, 1] }}
      className="space-y-3 rounded-[var(--radius-lg)] border border-[var(--color-clinical-800)] bg-[var(--color-clinical-950)]/60 p-5"
    >
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--color-clinical-800)] pb-2.5">
        <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wide text-[var(--color-clinical-300)]">
          <Sparkles className="h-4 w-4" aria-hidden="true" />
          <span>Why this recommendation?</span>
        </div>
        <div className="flex items-center space-x-2 text-[11px] text-[var(--color-clinical-300)]">
          <span className="inline-flex items-center space-x-1 rounded-[var(--radius-sm)] border border-[var(--color-clinical-700)] bg-[var(--color-clinical-900)] px-2 py-0.5 text-[10px] font-medium">
            <ShieldCheck className="h-3 w-3" aria-hidden="true" />
            <span>Deterministic fusion</span>
          </span>
          {generatedAt && <span className="num-clinical">• Generated: {new Date(generatedAt).toLocaleTimeString()}</span>}
        </div>
      </div>

      <p className="text-xs leading-relaxed text-[var(--color-clinical-100)] sm:text-sm">{narrative}</p>

      <div className="flex items-center justify-between border-t border-[var(--color-clinical-800)] pt-2 text-[11px] text-[var(--color-clinical-300)]">
        <span className="font-medium italic">Evidence precedes AI. The clinician retains final prescribing authority.</span>
        {traceId && <span className="num-clinical hidden text-[10px] sm:inline-block">Trace: {traceId.slice(0, 16)}…</span>}
      </div>
    </motion.div>
  );
}

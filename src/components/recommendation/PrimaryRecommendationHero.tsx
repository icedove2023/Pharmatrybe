import React from 'react';
import { motion, useReducedMotion } from 'motion/react';
import {
  Pill, ShieldCheck, AlertTriangle, Route, Calendar, Sparkles, Shield, ArrowDown,
} from 'lucide-react';
import { PrimaryRecommendation, ConfidenceLevel, ClinicalWarning } from '@/types';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { ClinicalButton } from '@/components/ui/ClinicalButton';

interface PrimaryRecommendationHeroProps {
  primaryRecommendation: PrimaryRecommendation;
  confidence: ConfidenceLevel;
  criticalWarnings?: ClinicalWarning[];
  onScrollToReview?: () => void;
  onOpenExplainability?: () => void;
}

export function PrimaryRecommendationHero({
  primaryRecommendation,
  confidence,
  criticalWarnings = [],
  onScrollToReview,
  onOpenExplainability,
}: PrimaryRecommendationHeroProps) {
  const normCategory = (primaryRecommendation.guideline_category || '').toLowerCase();

  const awareBadge = () => {
    if (normCategory === 'access') {
      return (
        <StatusBadge tone="success" icon={ShieldCheck}>
          WHO AWaRe: Access
        </StatusBadge>
      );
    }
    if (normCategory === 'watch') {
      return (
        <StatusBadge tone="warning" icon={AlertTriangle}>
          WHO AWaRe: Watch
        </StatusBadge>
      );
    }
    return (
      <StatusBadge tone="critical" icon={AlertTriangle}>
        WHO AWaRe: Reserve
      </StatusBadge>
    );
  };

  const formatConfidence = (conf: ConfidenceLevel) => {
    const c = (conf || '').toLowerCase();
    if (c === 'very_high') return { label: 'Very high', tone: 'text-[var(--color-safety-success)] bg-[var(--color-safety-success-bg)] border-[var(--color-safety-success-border)]' };
    if (c === 'high') return { label: 'High', tone: 'text-[var(--color-safety-success)] bg-[var(--color-safety-success-bg)] border-[var(--color-safety-success-border)]' };
    if (c === 'moderate') return { label: 'Moderate', tone: 'text-[var(--color-safety-warning)] bg-[var(--color-safety-warning-bg)] border-[var(--color-safety-warning-border)]' };
    if (c === 'low') return { label: 'Low', tone: 'text-[var(--color-safety-critical)] bg-[var(--color-safety-critical-bg)] border-[var(--color-safety-critical-border)]' };
    if (c === 'very_low') return { label: 'Very low', tone: 'text-[var(--color-safety-critical)] bg-[var(--color-safety-critical-bg)] border-[var(--color-safety-critical-border)]' };
    return { label: (conf || 'Moderate'), tone: 'text-[var(--color-clinical-300)] bg-[var(--color-clinical-950)] border-[var(--color-clinical-700)]' };
  };

  const confInfo = formatConfidence(confidence);
  const isLowConfidence = confidence === 'low' || confidence === 'very_low';
  const prefersReducedMotion = useReducedMotion();

  return (
    <motion.div
      id="primary-recommendation-hero"
      initial={prefersReducedMotion ? false : { opacity: 0, y: 10, scale: 0.99 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.32, ease: [0.2, 0.8, 0.2, 1] }}
      className="relative space-y-5 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6"
    >
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        {/* Left / Main Regimen details */}
        <div className="flex-1 space-y-4">
          {/* Taxonomy & Provenance Chips */}
          <div className="flex flex-wrap items-center gap-2">
            {awareBadge()}
            <StatusBadge tone="clinical">Rank #{primaryRecommendation.ranking || 1} · Primary recommendation</StatusBadge>
          </div>

          {/* Drug Title */}
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wide text-[var(--color-clinical-400)]">
              Primary evidence-based antimicrobial regimen
            </p>
            <h1 className="mt-1 flex flex-wrap items-center gap-2 text-2xl font-bold text-slate-text-primary sm:text-3xl">
              <Pill className="h-7 w-7 shrink-0 text-[var(--color-clinical-400)]" aria-hidden="true" />
              {primaryRecommendation.antibiotic_name || 'Antimicrobial not specified'}
            </h1>
            <p className="mt-1 text-xs leading-relaxed text-slate-text-secondary sm:text-sm">
              {primaryRecommendation.reason}
            </p>
          </div>

          {/* Critical Warnings — Surfaced Above-the-Fold, Never Below */}
          {criticalWarnings.length > 0 && (
            <SafetyAlert
              level="critical"
              title={`Critical safety warnings & contraindications (${criticalWarnings.length})`}
            >
              <div className="mt-1 space-y-1.5">
                {criticalWarnings.map((cw, idx) => (
                  <div key={idx} className="rounded-[var(--radius-sm)] border border-[var(--color-safety-critical-border)] bg-black/20 p-2">
                    <strong className="block text-white">{cw.title}</strong>
                    <span className="leading-snug">{cw.details}</span>
                  </div>
                ))}
              </div>
            </SafetyAlert>
          )}

          {/* Low-confidence caution */}
          {isLowConfidence && (
            <SafetyAlert level="warning" title="Increased clinical scrutiny required">
              This recommendation has lower model confidence and requires increased clinical review. Evaluate
              microbiological culture history and organ function before prescribing.
            </SafetyAlert>
          )}

          {/* Regimen Spec Grid */}
          <div className="grid grid-cols-1 gap-3 pt-1 text-xs sm:grid-cols-2">
            <div className="space-y-1 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3.5">
              <div className="flex items-center space-x-1.5 font-medium text-slate-text-muted">
                <Route className="h-3.5 w-3.5 text-[var(--color-clinical-400)]" aria-hidden="true" />
                <span>Dosage & administration</span>
              </div>
              <p className="num-clinical text-xs font-semibold text-slate-text-primary">
                {primaryRecommendation.dosage_notes || 'Standard therapeutic dosing per institutional formulary'}
              </p>
            </div>

            <div className="space-y-1 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3.5">
              <div className="flex items-center space-x-1.5 font-medium text-slate-text-muted">
                <Calendar className="h-3.5 w-3.5 text-[var(--color-safety-success)]" aria-hidden="true" />
                <span>Recommended duration</span>
              </div>
              <p className="num-clinical text-xs font-semibold text-[var(--color-safety-success)]">
                {primaryRecommendation.duration_notes || '5–7 days (review at 48–72h)'}
              </p>
            </div>
          </div>
        </div>

        {/* Right / Confidence & Determination panel */}
        <div className="flex min-w-[240px] max-w-[280px] shrink-0 flex-col justify-between space-y-3 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface-raised p-4 sm:p-5">
          <div className="space-y-1 text-center">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-text-muted">
              Statistical model confidence
            </p>
            <div className={`my-1.5 flex items-center justify-center rounded-[var(--radius-md)] border px-3 py-1.5 ${confInfo.tone}`}>
              <span className="text-sm font-bold tracking-wide">{confInfo.label}</span>
            </div>
            <p className="text-[10px] leading-snug text-slate-text-muted">
              Model confidence is not clinical certainty.
            </p>
          </div>

          <div className="space-y-2 border-y border-slate-border-subtle py-2.5 text-xs">
            <div className="flex items-center justify-between text-[11px]">
              <span className="flex items-center text-slate-text-muted">
                <ShieldCheck className="mr-1 h-3 w-3 text-[var(--color-safety-success)]" aria-hidden="true" />
                Guideline concordance
              </span>
              <span className="text-[10px] font-semibold uppercase text-[var(--color-safety-success)]">{normCategory || 'access'}</span>
            </div>
            <div className="flex items-center justify-between text-[11px]">
              <span className="flex items-center text-slate-text-muted">
                <Shield className="mr-1 h-3 w-3 text-[var(--color-clinical-400)]" aria-hidden="true" />
                Safety engine rules
              </span>
              <span className="text-[10px] font-semibold text-[var(--color-clinical-300)]">Evaluated</span>
            </div>
          </div>

          <div className="rounded-[var(--radius-sm)] border border-slate-border-subtle bg-slate-canvas p-2 text-left text-[10px] leading-tight text-slate-text-muted">
            <span className="mb-0.5 block font-semibold text-slate-text-secondary">Clinical disclaimer</span>
            This information supports clinical decision-making; it does not replace clinician judgement.
          </div>

          <div className="w-full space-y-2 pt-1">
            {onOpenExplainability && (
              <ClinicalButton variant="primary" size="sm" icon={Sparkles} onClick={onOpenExplainability} className="w-full">
                Why this recommendation?
              </ClinicalButton>
            )}
            {onScrollToReview && (
              <ClinicalButton variant="secondary" size="sm" icon={ArrowDown} onClick={onScrollToReview} className="w-full">
                Review & determine
              </ClinicalButton>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

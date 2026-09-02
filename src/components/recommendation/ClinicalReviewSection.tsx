import React, { useState, useEffect } from 'react';
import {
  CheckCircle2, Edit3, XCircle, UserCheck,
  Clock, AlertTriangle, Send, History, Lock,
} from 'lucide-react';
import {
  PrimaryRecommendation,
  AlternativeRecommendation,
  ClinicalReviewRequest,
  ClinicalReviewResponse,
} from '@/types';
import { recommendationApi } from '@/api/recommendationApi';
import { createApprovedPatientHistory } from '@/api/patientsApi';
import { useAuthStore } from '@/stores/authStore';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { ClinicalButton } from '@/components/ui/ClinicalButton';
import { cn } from '@/lib/utils';

interface ClinicalReviewSectionProps {
  recommendationId: string;
  patientId: string;
  primaryRecommendation: PrimaryRecommendation;
  alternativeRecommendations?: AlternativeRecommendation[];
  patientName?: string;
  patientDemographics?: Record<string, unknown>;
  onReviewRecorded?: (review: ClinicalReviewResponse) => void;
}

type ReviewDecisionType = 'APPROVED' | 'MODIFIED' | 'REJECTED';

export function ClinicalReviewSection({
  recommendationId,
  patientId,
  primaryRecommendation,
  alternativeRecommendations = [],
  patientName,
  patientDemographics,
  onReviewRecorded,
}: ClinicalReviewSectionProps) {
  const user = useAuthStore((state) => state.user);
  const clinicianId = user?.id || '';

  const [selectedDecision, setSelectedDecision] = useState<ReviewDecisionType>('APPROVED');
  const [selectedAntibiotic, setSelectedAntibiotic] = useState<string>(primaryRecommendation.antibiotic_name);
  const [customAntibiotic, setCustomAntibiotic] = useState<string>('');
  const [clinicalNotes, setClinicalNotes] = useState<string>('');
  const [reasonForDeviation, setReasonForDeviation] = useState<string>('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [recordedReviews, setRecordedReviews] = useState<ClinicalReviewResponse[]>([]);
  const [latestRecordedReview, setLatestRecordedReview] = useState<ClinicalReviewResponse | null>(null);

  useEffect(() => {
    let mounted = true;
    recommendationApi.getClinicalReviews(recommendationId).then((reviews) => {
      if (mounted && reviews.length > 0) {
        setRecordedReviews(reviews);
        setLatestRecordedReview(reviews[reviews.length - 1]);
      }
    }).catch(() => {
      if (mounted) setRecordedReviews([]);
    });
    return () => {
      mounted = false;
    };
  }, [recommendationId]);

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!clinicianId) {
      setErrorMessage('Authentication backend integration pending. A verified clinician identity is required.');
      return;
    }

    if (selectedDecision === 'MODIFIED' && !reasonForDeviation.trim()) {
      setErrorMessage('Reason for deviation is required when modifying the recommendation.');
      return;
    }
    if (selectedDecision === 'REJECTED' && !reasonForDeviation.trim()) {
      setErrorMessage('Reason for rejection is required when rejecting the recommendation.');
      return;
    }

    const finalAntibiotic =
      selectedDecision === 'APPROVED'
        ? primaryRecommendation.antibiotic_name
        : selectedDecision === 'MODIFIED'
        ? selectedAntibiotic === 'OTHER_CUSTOM'
          ? customAntibiotic.trim() || 'Custom Regimen'
          : selectedAntibiotic
        : undefined;

    const payload: ClinicalReviewRequest = {
      recommendation_id: recommendationId,
      patient_id: patientId,
      patient_name: patientName,
      patient_demographics: patientDemographics,
      clinician_id: clinicianId,
      review_decision: selectedDecision,
      selected_antibiotic: finalAntibiotic,
      clinical_notes: clinicalNotes.trim() || undefined,
      reason_for_deviation: reasonForDeviation.trim() || undefined,
    };

    setIsSubmitting(true);
    try {
      const response = await recommendationApi.recordClinicalReview(payload);
      if (selectedDecision === 'APPROVED' || selectedDecision === 'MODIFIED') {
        await createApprovedPatientHistory(patientId, {
          recommendation_id: recommendationId,
          review_decision: selectedDecision,
          selected_antibiotic: finalAntibiotic,
          clinical_notes: clinicalNotes.trim() || undefined,
          patient_name: patientName,
          demographics: patientDemographics,
        });
      }
      setLatestRecordedReview(response);
      setRecordedReviews((prev) => [...prev, response]);
      if (onReviewRecorded) onReviewRecorded(response);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to record clinical review with backend.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const submitLabel =
    selectedDecision === 'APPROVED' ? 'Approve regimen' : selectedDecision === 'MODIFIED' ? 'Record modification' : 'Reject regimen';
  const submitVariant = selectedDecision === 'APPROVED' ? 'primary' : selectedDecision === 'MODIFIED' ? 'secondary' : 'destructive';

  return (
    <div
      id="clinician-review-section"
      className="space-y-6 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6"
    >
      {/* Header & Immutability Clarification Banner */}
      <div className="space-y-2 border-b border-slate-border-subtle pb-4">
        <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-center">
          <div className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--color-clinical-950)] text-[var(--color-clinical-300)]">
              <UserCheck className="h-5 w-5" aria-hidden="true" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-text-primary sm:text-lg">Clinician determination</h2>
              <p className="text-xs text-slate-text-muted">The clinician decides; the system only recommends</p>
            </div>
          </div>

          <div className="flex items-center space-x-1.5 rounded-[var(--radius-md)] border border-[var(--color-safety-warning-border)] bg-[var(--color-safety-warning-bg)] px-3 py-1.5 text-xs text-[var(--color-safety-warning)]">
            <Lock className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
            <span className="text-[11px] font-semibold">AI recommendation is immutable</span>
          </div>
        </div>

        <div className="space-y-1.5 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3 text-xs leading-relaxed">
          <p className="text-slate-text-secondary">
            <strong className="text-slate-text-primary">Prescribing authority:</strong> the CDSS recommendation
            provides evidence-based guidance. This information supports clinical decision-making; it does not
            replace clinician judgement.
          </p>
          <p className="text-[11px] text-slate-text-muted">
            Determinations recorded below are session workflow state.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmitReview} className="space-y-5">
        {/* Decision hierarchy: Approve primary, Modify secondary, Reject destructive */}
        <div>
          <label className="mb-2.5 block text-xs font-semibold uppercase tracking-wide text-slate-text-secondary">
            Select clinician review determination
          </label>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <button
              type="button"
              onClick={() => setSelectedDecision('APPROVED')}
              aria-pressed={selectedDecision === 'APPROVED'}
              className={cn(
                'flex flex-col justify-between space-y-2 rounded-[var(--radius-md)] border-2 p-4 text-left transition-colors duration-[var(--duration-fast)] focus-clinical',
                selectedDecision === 'APPROVED'
                  ? 'border-[var(--color-safety-success)] bg-[var(--color-safety-success-bg)]'
                  : 'border-slate-border bg-slate-inset hover:border-slate-border',
              )}
            >
              <div className="flex items-center justify-between">
                <span className="flex items-center text-xs font-bold text-[var(--color-safety-success)]">
                  <CheckCircle2 className="mr-1.5 h-4 w-4 shrink-0 text-[var(--color-safety-success)]" aria-hidden="true" />
                  Approve
                </span>
                <span className="rounded bg-[var(--color-safety-success-bg)]/60 px-1.5 py-0.5 text-[10px] font-semibold text-[var(--color-safety-success)]">
                  Recommended
                </span>
              </div>
              <p className="text-xs text-slate-text-secondary">
                Prescribe the primary recommendation ({primaryRecommendation.antibiotic_name}).
              </p>
            </button>

            <button
              type="button"
              onClick={() => setSelectedDecision('MODIFIED')}
              aria-pressed={selectedDecision === 'MODIFIED'}
              className={cn(
                'flex flex-col justify-between space-y-2 rounded-[var(--radius-md)] border p-4 text-left transition-colors duration-[var(--duration-fast)] focus-clinical',
                selectedDecision === 'MODIFIED'
                  ? 'border-[var(--color-safety-warning)] bg-[var(--color-safety-warning-bg)]'
                  : 'border-slate-border bg-slate-inset hover:border-slate-border',
              )}
            >
              <div className="flex items-center justify-between">
                <span className="flex items-center text-xs font-semibold text-[var(--color-safety-warning)]">
                  <Edit3 className="mr-1.5 h-4 w-4 shrink-0 text-[var(--color-safety-warning)]" aria-hidden="true" />
                  Modify
                </span>
                <span className="rounded bg-[var(--color-safety-warning-bg)]/60 px-1.5 py-0.5 text-[10px] font-semibold text-[var(--color-safety-warning)]">
                  Alternative
                </span>
              </div>
              <p className="text-xs text-slate-text-secondary">
                Select an alternative antibiotic or customize dosing with documented rationale.
              </p>
            </button>

            <button
              type="button"
              onClick={() => setSelectedDecision('REJECTED')}
              aria-pressed={selectedDecision === 'REJECTED'}
              className={cn(
                'flex flex-col justify-between space-y-2 rounded-[var(--radius-md)] border p-4 text-left transition-colors duration-[var(--duration-fast)] focus-clinical',
                selectedDecision === 'REJECTED'
                  ? 'border-[var(--color-safety-critical)] bg-[var(--color-safety-critical-bg)]'
                  : 'border-slate-border bg-slate-inset hover:border-slate-border',
              )}
            >
              <div className="flex items-center justify-between">
                <span className="flex items-center text-xs font-semibold text-[var(--color-safety-critical)]">
                  <XCircle className="mr-1.5 h-4 w-4 shrink-0 text-[var(--color-safety-critical)]" aria-hidden="true" />
                  Reject
                </span>
                <span className="rounded bg-[var(--color-safety-critical-bg)]/60 px-1.5 py-0.5 text-[10px] font-semibold text-[var(--color-safety-critical)]">
                  Withhold
                </span>
              </div>
              <p className="text-xs text-slate-text-secondary">
                Withhold antimicrobial prescription (e.g. viral etiology, palliative care).
              </p>
            </button>
          </div>
        </div>

        {/* Dynamic Fields for MODIFIED Decision */}
        {selectedDecision === 'MODIFIED' && (
          <div className="space-y-3 rounded-[var(--radius-md)] border border-[var(--color-safety-warning-border)] bg-[var(--color-safety-warning-bg)]/40 p-4">
            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-text-primary">
                Selected prescribed antibiotic
              </label>
              <select
                value={selectedAntibiotic}
                onChange={(e) => setSelectedAntibiotic(e.target.value)}
                className="focus-clinical w-full rounded-[var(--radius-sm)] border border-slate-border bg-slate-canvas p-2.5 text-xs font-medium text-slate-text-primary"
              >
                <optgroup label="AI Alternatives">
                  {alternativeRecommendations.map((alt) => (
                    <option key={alt.antibiotic_name} value={alt.antibiotic_name}>
                      {alt.antibiotic_name} ({alt.guideline_category?.toUpperCase() || 'ACCESS'} — Rank #{alt.ranking})
                    </option>
                  ))}
                </optgroup>
                <optgroup label="Primary Regimen">
                  <option value={primaryRecommendation.antibiotic_name}>
                    {primaryRecommendation.antibiotic_name} (primary regimen with dose adjustment)
                  </option>
                </optgroup>
                <optgroup label="Custom / Other">
                  <option value="OTHER_CUSTOM">Other custom regimen…</option>
                </optgroup>
              </select>
            </div>

            {selectedAntibiotic === 'OTHER_CUSTOM' && (
              <div>
                <label className="mb-1 block text-xs font-semibold text-slate-text-primary">
                  Specify custom regimen & dose
                </label>
                <input
                  type="text"
                  placeholder="e.g. Meropenem 1g IV q8h (microbiology consultant guidance)"
                  value={customAntibiotic}
                  onChange={(e) => setCustomAntibiotic(e.target.value)}
                  className="focus-clinical w-full rounded-[var(--radius-sm)] border border-slate-border bg-slate-canvas p-2.5 text-xs text-slate-text-primary"
                />
              </div>
            )}
          </div>
        )}

        {/* Reason for Deviation (Mandatory if MODIFIED or REJECTED) */}
        {(selectedDecision === 'MODIFIED' || selectedDecision === 'REJECTED') && (
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="block text-xs font-semibold text-slate-text-primary">
                Reason for clinical deviation <span className="text-[var(--color-safety-critical)]">*</span>
              </label>
              <span className="rounded bg-[var(--color-safety-warning-bg)]/40 px-2 py-0.5 text-[10px] font-medium text-[var(--color-safety-warning)]">
                Required
              </span>
            </div>
            <input
              type="text"
              required
              placeholder={
                selectedDecision === 'MODIFIED'
                  ? 'e.g. Documented severe unrecorded intolerance to first-line agent, ID team consult'
                  : 'e.g. Clinical presentation consistent with acute viral bronchitis; antimicrobials not indicated'
              }
              value={reasonForDeviation}
              onChange={(e) => setReasonForDeviation(e.target.value)}
              className="focus-clinical w-full rounded-[var(--radius-sm)] border border-slate-border bg-slate-inset p-2.5 text-xs text-slate-text-primary"
            />
            <p className="text-[11px] italic text-slate-text-muted">
              Mandatory documented rationale ensures transparent auditability of prescribing deviation.
            </p>
          </div>
        )}

        {/* Clinical Notes */}
        <div>
          <label className="mb-1 block text-xs font-semibold text-slate-text-primary">
            Clinician charting & prescribing notes
          </label>
          <textarea
            rows={3}
            placeholder="Document patient counselling, microbiology culture follow-up plan, or formulary authorization…"
            value={clinicalNotes}
            onChange={(e) => setClinicalNotes(e.target.value)}
            className="focus-clinical w-full rounded-[var(--radius-sm)] border border-slate-border bg-slate-inset p-2.5 text-xs text-slate-text-primary"
          />
        </div>

        {errorMessage && <SafetyAlert level="warning" title="Cannot record determination">{errorMessage}</SafetyAlert>}

        {/* Submission Action Bar */}
        <div className="flex flex-col justify-between gap-3 pt-2 sm:flex-row sm:items-center">
          <div className="num-clinical text-[11px] text-slate-text-muted">
            Clinician ID: <strong className="text-slate-text-secondary">{clinicianId}</strong>
          </div>

          <ClinicalButton type="submit" variant={submitVariant as any} size="lg" icon={Send} loading={isSubmitting}>
            {isSubmitting ? 'Recording determination…' : submitLabel}
          </ClinicalButton>
        </div>
      </form>

      {/* Recorded Review Confirmation & Audit Log */}
      {recordedReviews.length > 0 && (
        <div className="space-y-3 border-t border-slate-border-subtle pt-4">
          <div className="flex items-center space-x-2">
            <History className="h-4 w-4 text-[var(--color-clinical-400)]" aria-hidden="true" />
            <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-text-primary">
              Session determination log ({recordedReviews.length})
            </h3>
          </div>

          <div className="space-y-2">
            {recordedReviews.map((rev, idx) => {
              const isApproved = rev.review_decision === 'APPROVED';
              const isModified = rev.review_decision === 'MODIFIED';
              const tone = isApproved
                ? 'border-[var(--color-safety-success-border)] bg-[var(--color-safety-success-bg)]/50'
                : isModified
                ? 'border-[var(--color-safety-warning-border)] bg-[var(--color-safety-warning-bg)]/50'
                : 'border-[var(--color-safety-critical-border)] bg-[var(--color-safety-critical-bg)]/50';
              const pillTone = isApproved ? 'bg-[var(--color-safety-success-bg)]' : isModified ? 'bg-[var(--color-safety-warning-bg)]' : 'bg-[var(--color-safety-critical-bg)]';

              return (
                <div
                  key={`${rev.recommendation_id}-${rev.recorded_at}-${idx}`}
                  className={cn('space-y-1.5 rounded-[var(--radius-md)] border p-3.5 text-xs', tone)}
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center space-x-2">
                      <span className={cn('rounded px-2 py-0.5 text-[10px] font-bold text-white', pillTone)}>
                        {rev.review_decision}
                      </span>
                      <span className="font-semibold text-slate-text-primary">{rev.clinician_id}</span>
                    </div>
                    <div className="num-clinical flex items-center space-x-1 text-[11px] text-slate-text-muted">
                      <Clock className="h-3 w-3" aria-hidden="true" />
                      <span>{new Date(rev.recorded_at).toLocaleTimeString()}</span>
                    </div>
                  </div>

                  {rev.selected_antibiotic && (
                    <p className="text-slate-text-secondary">
                      <strong>Selected regimen:</strong> {rev.selected_antibiotic}
                    </p>
                  )}
                  {rev.reason_for_deviation && (
                    <p className="text-slate-text-secondary">
                      <strong>Reason for deviation:</strong> {rev.reason_for_deviation}
                    </p>
                  )}
                  {rev.clinical_notes && (
                    <p className="italic text-slate-text-muted">&ldquo;{rev.clinical_notes}&rdquo;</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

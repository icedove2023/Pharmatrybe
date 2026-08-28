import React, { useState } from 'react';
import { Edit3, X, Check } from 'lucide-react';
import { DrugRecommendation } from '@/types';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { ClinicalButton } from '@/components/ui/ClinicalButton';

interface PrescribingOverrideModalProps {
  isOpen: boolean;
  onClose: () => void;
  alternativeRecommendations: DrugRecommendation[];
  onSubmitOverride: (payload: { selectedDrug: string; reason: string; clinicianName: string }) => void;
  isPending: boolean;
  defaultClinicianName: string;
}

export function PrescribingOverrideModal({
  isOpen,
  onClose,
  alternativeRecommendations,
  onSubmitOverride,
  isPending,
  defaultClinicianName,
}: PrescribingOverrideModalProps) {
  const [selectedDrug, setSelectedDrug] = useState('');
  const [customDrug, setCustomDrug] = useState('');
  const [reason, setReason] = useState('');
  const [clinicianName, setClinicianName] = useState(defaultClinicianName || 'Dr. Ada Lovelace');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const finalDrug = selectedDrug === 'CUSTOM' ? customDrug.trim() : selectedDrug.trim();
    if (!finalDrug || !reason.trim()) return;

    onSubmitOverride({
      selectedDrug: finalDrug,
      reason: reason.trim(),
      clinicianName: clinicianName.trim(),
    });
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="override-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs"
    >
      <div className="w-full max-w-lg space-y-0 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-border-subtle pb-3">
          <div className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--color-safety-warning-bg)] text-[var(--color-safety-warning)]">
              <Edit3 className="h-4 w-4" aria-hidden="true" />
            </div>
            <div>
              <h3 id="override-modal-title" className="text-sm font-semibold text-slate-text-primary">
                Clinical prescribing override
              </h3>
              <p className="text-[11px] text-slate-text-muted">Antimicrobial stewardship governance protocol</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close override dialog"
            className="focus-clinical rounded-[var(--radius-sm)] p-1 text-slate-text-muted hover:text-slate-text-primary"
          >
            <X className="h-5 w-5" aria-hidden="true" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="space-y-4 pt-4 text-xs">
          <SafetyAlert level="warning" title="Overrides are permanently recorded">
            Clinicians retain prescribing authority. Per hospital stewardship policy, overrides require a documented
            clinical justification and are permanently recorded in the immutable audit log.
          </SafetyAlert>

          <div>
            <label className="mb-1 block font-semibold text-slate-text-secondary">
              Select desired antimicrobial regimen <span className="text-[var(--color-safety-critical)]">*</span>
            </label>
            <select
              value={selectedDrug}
              onChange={(e) => setSelectedDrug(e.target.value)}
              className="focus-clinical w-full rounded-[var(--radius-sm)] border border-slate-border bg-slate-inset px-3 py-2 text-slate-text-primary"
              required
            >
              <option value="">— Choose regimen —</option>
              {alternativeRecommendations.map((alt, idx) => (
                <option key={idx} value={`${alt.drugName} ${alt.dose}`}>
                  {alt.drugName} {alt.dose} ({alt.awareCategory || 'Standard'}) — {alt.route}
                </option>
              ))}
              <option value="CUSTOM">— Specify custom regimen —</option>
            </select>
          </div>

          {selectedDrug === 'CUSTOM' && (
            <div>
              <label className="mb-1 block font-semibold text-slate-text-secondary">
                Custom regimen name & dosing <span className="text-[var(--color-safety-critical)]">*</span>
              </label>
              <input
                type="text"
                value={customDrug}
                onChange={(e) => setCustomDrug(e.target.value)}
                placeholder="e.g. Piperacillin/Tazobactam 4.5g IV Q6H"
                className="focus-clinical w-full rounded-[var(--radius-sm)] border border-slate-border bg-slate-inset px-3 py-2 text-slate-text-primary"
                required
              />
            </div>
          )}

          <div>
            <label className="mb-1 block font-semibold text-slate-text-secondary">
              Documented clinical justification <span className="text-[var(--color-safety-critical)]">*</span>
            </label>
            <textarea
              rows={3}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="State rationale (e.g. microbiology culture sensitivity, prior treatment failure, patient intolerance)…"
              className="focus-clinical w-full rounded-[var(--radius-sm)] border border-slate-border bg-slate-inset px-3 py-2 leading-relaxed text-slate-text-primary"
              required
            />
          </div>

          <div>
            <label className="mb-1 block font-semibold text-slate-text-secondary">Signing clinician identifier</label>
            <input
              type="text"
              value={clinicianName}
              onChange={(e) => setClinicianName(e.target.value)}
              className="focus-clinical w-full rounded-[var(--radius-sm)] border border-slate-border bg-slate-inset px-3 py-2 text-slate-text-primary"
              required
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-2 pt-2">
            <ClinicalButton type="button" variant="outline" onClick={onClose}>
              Cancel
            </ClinicalButton>
            <ClinicalButton type="submit" variant="primary" icon={Check} loading={isPending}>
              {isPending ? 'Logging override…' : 'Sign & submit override'}
            </ClinicalButton>
          </div>
        </form>
      </div>
    </div>
  );
}

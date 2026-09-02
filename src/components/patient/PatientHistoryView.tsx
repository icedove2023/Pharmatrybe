import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'motion/react';
import { History, Search, X, Code2 } from 'lucide-react';
import { patientApi } from '@/api';
import { PatientSummary, PatientDetails, HistoryEvent } from '@/types';
import { StatusBadge, BadgeTone } from '@/components/ui/StatusBadge';
import { ClinicalButton } from '@/components/ui/ClinicalButton';
import { SkeletonCard } from '@/components/ui/Skeleton';
import { cn } from '@/lib/utils';

const EVENT_TONE: Record<HistoryEvent['type'], BadgeTone> = {
  Assessment: 'clinical',
  Recommendation: 'clinical',
  'Stewardship Alert': 'warning',
  'Clinician Action': 'success',
} as any;

export function PatientHistoryView() {
  const [patients, setPatients] = useState<PatientSummary[]>([]);
  const [directoryAvailable, setDirectoryAvailable] = useState<boolean | null>(null);
  const [selectedPatientId, setSelectedPatientId] = useState<string>('');
  const [patientDetails, setPatientDetails] = useState<PatientDetails | null>(null);
  const [historyEvents, setHistoryEvents] = useState<HistoryEvent[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeModalEvent, setActiveModalEvent] = useState<HistoryEvent | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const prefersReducedMotion = useReducedMotion();

  useEffect(() => {
    setIsLoading(true);
    patientApi.searchPatients(searchQuery)
      .then((res) => {
        if (!res) {
          // backend search not implemented
          setDirectoryAvailable(false);
          setPatients([]);
        } else {
          setDirectoryAvailable(true);
          setPatients(res);
        }
      })
      .catch(() => {
        setDirectoryAvailable(false);
        setPatients([]);
      })
      .finally(() => setIsLoading(false));
  }, [searchQuery]);

  useEffect(() => {
    if (selectedPatientId) {
      // load details and history but tolerate 'not available' returns
      patientApi.getPatientDetails(selectedPatientId)
        .then((res) => setPatientDetails(res ?? null))
        .catch(() => setPatientDetails(null));

      patientApi.getPatientHistory(selectedPatientId)
        .then((res) => setHistoryEvents(Array.isArray(res) ? res : (res ? [res as any] : [])))
        .catch(() => setHistoryEvents([]));
    }
  }, [selectedPatientId]);
            <h3 className="text-base font-semibold text-slate-text-primary">{patientDetails.name || 'Patient not named'}</h3>
  if (isLoading) {
    return (
      <div className="space-y-6">
        <SkeletonCard lines={1} />
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <SkeletonCard lines={4} />
          <div className="space-y-6 lg:col-span-2">
            <SkeletonCard lines={5} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative space-y-6">
      {/* Title Header */}
      <div className="flex flex-col justify-between gap-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6 md:flex-row md:items-center">
        <div>
          <div className="mb-1 inline-flex items-center space-x-1.5 rounded-full bg-[var(--color-clinical-950)] px-2.5 py-0.5 text-xs font-semibold text-[var(--color-clinical-300)]">
            <History className="h-3.5 w-3.5" aria-hidden="true" />
            <span>Longitudinal patient records</span>
          </div>
          <h2 className="text-xl font-semibold text-slate-text-primary">Patient directory & clinical audit</h2>
          <p className="text-xs text-slate-text-muted">
            Longitudinal timeline tracking assessments, recommendation packages, and clinician determinations.
          </p>
        </div>

        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search patient name or MRN…"
            className="focus-clinical w-full rounded-[var(--radius-md)] border border-slate-border bg-slate-inset py-2 pl-9 pr-4 text-xs text-slate-text-primary placeholder-slate-text-muted"
          />
        </div>
      </div>

      {/* Main Grid: Patient List Sidebar & Timeline Main View */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Patient Selection List */}
        <div className="space-y-2 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-4">
          <p className="px-2 text-[10px] font-semibold uppercase tracking-wide text-slate-text-muted">Select patient record</p>
          {patients.length === 0 ? (
            <div className="rounded-[var(--radius-md)] border border-dashed border-slate-border p-6 text-center text-xs text-slate-text-muted">
              {directoryAvailable === false ? (
                <>
                  <div className="font-semibold mb-1">Patient directory is not exposed by the backend.</div>
                  <div className="text-xs">The backend does not provide a patient search/directory endpoint. Use Clinical Cases until this is implemented.</div>
                </>
              ) : (
                'No patients match this search.'
              )}
            </div>
          ) : (
            <div className="space-y-1.5">
              {patients.map((pat) => {
                const isSelected = pat.id === selectedPatientId;
                return (
                  <button
                    key={pat.id}
                    type="button"
                    onClick={() => setSelectedPatientId(pat.id)}
                    aria-current={isSelected}
                    className={cn(
                      'focus-clinical flex w-full items-center justify-between rounded-[var(--radius-md)] border p-3 text-left text-xs transition-colors duration-[var(--duration-fast)]',
                      isSelected
                        ? 'border-[var(--color-clinical-700)] bg-[var(--color-clinical-950)]/60'
                        : 'border-slate-border-subtle bg-slate-inset hover:bg-slate-inset-hover',
                    )}
                  >
                    <div>
                      <p className="font-semibold text-slate-text-primary">{pat.name || 'Patient not named'}</p>
                      <p className="num-clinical mt-0.5 text-[10px] text-slate-text-muted">ID: {pat.id} · {pat.gender}</p>
                    </div>
                    <StatusBadge tone="clinical">{pat.recordCount} events</StatusBadge>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Patient Timeline Content (Span 2) */}
        <div className="space-y-6 lg:col-span-2">
          {patientDetails && (
            <div className="space-y-1 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-5">
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-semibold text-slate-text-primary">{patientDetails.name || 'Patient not named'}</h3>
                <span className="num-clinical rounded border border-slate-border-subtle bg-slate-inset px-2 py-0.5 text-xs text-slate-text-secondary">
                  {patientDetails.mrn}
                </span>
              </div>
              <p className="text-xs text-slate-text-muted">
                {patientDetails.sex}, {patientDetails.age} yrs · Comorbidities: {patientDetails.comorbidities.join(', ') || 'None documented'}
              </p>
              <p className="text-xs font-semibold text-[var(--color-safety-critical)]">
                Allergies: {patientDetails.allergies.length ? patientDetails.allergies.join(', ') : 'None documented (NKDA)'}
              </p>
            </div>
          )}

          {/* Vertical Event Timeline */}
          <div className="space-y-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6">
            <h3 className="text-sm font-semibold text-slate-text-primary">Longitudinal clinical activity timeline</h3>

            {historyEvents.length === 0 ? (
              <div className="rounded-[var(--radius-md)] border border-dashed border-slate-border p-6 text-center text-xs text-slate-text-muted">
                No recorded activity for this patient yet.
              </div>
            ) : (
              <div className="relative space-y-6 pl-6 before:absolute before:bottom-2 before:left-2.5 before:top-2 before:w-0.5 before:bg-slate-border-subtle">
                {historyEvents.map((evt, idx) => (
                  <motion.div
                    key={evt.id}
                    initial={prefersReducedMotion ? false : { opacity: 0, x: -6 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2, delay: Math.min(idx * 0.03, 0.3) }}
                    className="relative"
                  >
                    <div className="absolute -left-[19px] top-1.5 h-3 w-3 rounded-full bg-[var(--color-clinical-500)] ring-4 ring-slate-surface" />

                    <div className="space-y-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-4 transition-colors duration-[var(--duration-fast)] hover:border-[var(--color-clinical-700)]">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <StatusBadge tone={EVENT_TONE[evt.type] ?? 'neutral'}>{evt.type}</StatusBadge>
                          <span className="text-xs font-semibold text-slate-text-primary">{evt.user}</span>
                        </div>
                        <span className="num-clinical text-[10px] text-slate-text-muted">
                          {new Date(evt.timestamp).toLocaleString()}
                        </span>
                      </div>

                      <p className="text-xs font-medium text-slate-text-secondary">{evt.summary}</p>

                      <button
                        onClick={() => setActiveModalEvent(evt)}
                        className="focus-clinical flex items-center pt-1 text-[11px] font-semibold text-[var(--color-clinical-400)] hover:underline"
                      >
                        <Code2 className="mr-1 h-3.5 w-3.5" aria-hidden="true" /> View full event audit payload
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* JSON Audit Modal */}
      <AnimatePresence>
        {activeModalEvent && (
          <motion.div
            role="dialog"
            aria-modal="true"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs"
            onClick={() => setActiveModalEvent(null)}
          >
            <motion.div
              initial={prefersReducedMotion ? false : { opacity: 0, scale: 0.97, y: 8 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={prefersReducedMotion ? undefined : { opacity: 0, scale: 0.97, y: 8 }}
              transition={{ duration: 0.18, ease: [0.2, 0.8, 0.2, 1] }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-lg space-y-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6 shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-slate-border-subtle pb-3">
                <div>
                  <h3 className="text-sm font-semibold text-slate-text-primary">Audit record detail: {activeModalEvent.id}</h3>
                  <p className="text-xs text-slate-text-muted">{activeModalEvent.type} by {activeModalEvent.user}</p>
                </div>
                <button
                  onClick={() => setActiveModalEvent(null)}
                  aria-label="Close audit detail"
                  className="focus-clinical rounded-[var(--radius-sm)] p-1 text-slate-text-muted hover:text-slate-text-primary"
                >
                  <X className="h-5 w-5" aria-hidden="true" />
                </button>
              </div>

              <div className="space-y-2 text-xs">
                <p className="num-clinical font-semibold text-slate-text-secondary">
                  Timestamp: {activeModalEvent.timestamp}
                </p>
                <p className="text-slate-text-muted">{activeModalEvent.summary}</p>
                <p className="pt-2 font-semibold text-slate-text-primary">Structured payload (JSON):</p>
                <pre className="max-h-60 overflow-x-auto rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-canvas p-3 text-[11px] text-[var(--color-safety-success)]">
                  {JSON.stringify(activeModalEvent.payload, null, 2)}
                </pre>
              </div>

              <div className="flex justify-end pt-2">
                <ClinicalButton variant="secondary" onClick={() => setActiveModalEvent(null)}>
                  Close
                </ClinicalButton>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

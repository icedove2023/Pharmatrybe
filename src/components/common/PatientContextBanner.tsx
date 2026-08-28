import React, { useState } from 'react';
import { User, Stethoscope, Droplets, Scale, ChevronDown, ChevronUp, ShieldAlert, Building2, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface PatientContextData {
  patientId: string;
  name: string;
  age: number;
  gender: 'M' | 'F' | 'Other';
  weightKg: number;
  heightCm?: number;
  egfr: number;
  crcl?: number;
  primaryDiagnosis: string;
  allergies?: string[];
  infectionSite?: string;
  ward?: string;
  bed?: string;
  admissionDate?: string;
  attendingClinician?: string;
}

interface PatientContextBannerProps {
  patient: PatientContextData;
  onClear?: () => void;
  className?: string;
}

export function PatientContextBanner({ patient, className = '' }: PatientContextBannerProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const hasAllergies = patient.allergies && patient.allergies.length > 0;
  const isSevereRenalImpaired = patient.egfr < 30;
  const isModerateRenalImpaired = patient.egfr >= 30 && patient.egfr < 60;

  const getRenalBadgeClass = () => {
    if (isSevereRenalImpaired) {
      return 'bg-[var(--color-safety-critical-bg)] border-[var(--color-safety-critical-border)] text-[var(--color-safety-critical)]';
    }
    if (isModerateRenalImpaired) {
      return 'bg-[var(--color-safety-warning-bg)] border-[var(--color-safety-warning-border)] text-[var(--color-safety-warning)]';
    }
    return 'bg-slate-inset border-slate-border text-slate-text-secondary';
  };

  return (
    <div
      id="patient-context-banner"
      className={cn(
        'space-y-3 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-4',
        className,
      )}
    >
      {/* Primary Essential Bar (Layer 1 - Always Visible) */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Left: Patient Identity */}
        <div className="flex items-center space-x-3 min-w-fit">
          <div className="w-10 h-10 rounded-[var(--radius-md)] bg-[var(--color-clinical-950)] text-[var(--color-clinical-300)] flex items-center justify-center font-bold shrink-0">
            <User className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-sm text-slate-text-primary">{patient.name}</span>
              <span className="num-clinical text-[11px] font-medium text-slate-text-secondary bg-slate-inset px-2 py-0.5 rounded border border-slate-border">
                MRN: {patient.patientId}
              </span>
            </div>
            <p className="text-[11px] text-slate-text-muted mt-0.5">
              {patient.age}y {patient.gender === 'M' ? 'Male' : patient.gender === 'F' ? 'Female' : patient.gender}
              {patient.ward ? ` • ${patient.ward}` : ''}
            </p>
          </div>
        </div>

        {/* Middle: Clinical Context Vitals */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-3">
          {/* Indication / Syndrome */}
          <div className="flex items-center space-x-1.5 bg-slate-inset px-3 py-1.5 rounded-[var(--radius-md)] border border-slate-border-subtle">
            <Stethoscope className="w-3.5 h-3.5 text-[var(--color-clinical-400)] shrink-0" aria-hidden="true" />
            <div className="text-[11px]">
              <span className="text-slate-text-muted text-[10px] block leading-none">Syndrome / Indication</span>
              <span className="font-semibold text-slate-text-primary">{patient.primaryDiagnosis}</span>
            </div>
          </div>

          {/* eGFR / Renal Status */}
          <div className={cn('flex items-center space-x-1.5 px-3 py-1.5 rounded-[var(--radius-md)] border', getRenalBadgeClass())}>
            <Droplets className="w-3.5 h-3.5 shrink-0" aria-hidden="true" />
            <div className="text-[11px]">
              <span className="text-slate-text-muted text-[10px] block leading-none">eGFR (Renal)</span>
              <span className="num-clinical font-semibold">
                {patient.egfr} <span className="font-normal text-[10px]">mL/min</span>
                {isSevereRenalImpaired && <span className="ml-1 text-[10px] font-bold uppercase">Severe</span>}
                {isModerateRenalImpaired && <span className="ml-1 text-[10px] font-bold uppercase">Moderate</span>}
              </span>
            </div>
          </div>
        </div>

        {/* Right: Salient Allergy Gate Badge & Expand Toggle */}
        <div className="flex items-center space-x-2">
          {hasAllergies ? (
            <div
              id="patient-allergy-alert-badge"
              role="alert"
              className="flex items-center space-x-1.5 bg-[var(--color-safety-critical-bg)] border-2 border-[var(--color-safety-critical-border)] px-3 py-1.5 rounded-[var(--radius-md)] text-[var(--color-safety-critical)] font-semibold text-[11px]"
            >
              <ShieldAlert className="w-4 h-4 text-[var(--color-safety-critical)] shrink-0" aria-hidden="true" />
              <span>Allergies: {patient.allergies?.join(', ')}</span>
            </div>
          ) : (
            <span className="text-[11px] text-[var(--color-safety-success)] font-semibold bg-[var(--color-safety-success-bg)] px-3 py-1.5 rounded-[var(--radius-md)] border border-[var(--color-safety-success-border)] flex items-center space-x-1">
              <span>NKDA (No Known Allergies)</span>
            </span>
          )}

          {/* Progressive Disclosure Toggle Button */}
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="focus-clinical flex items-center space-x-1 px-2.5 py-1.5 rounded-[var(--radius-md)] border border-slate-border bg-slate-inset text-slate-text-secondary hover:text-slate-text-primary hover:bg-slate-inset-hover transition-colors duration-[var(--duration-fast)] text-[11px] font-semibold"
            aria-expanded={isExpanded}
            aria-controls="patient-secondary-details-drawer"
            aria-label="Toggle secondary patient details"
          >
            <span>{isExpanded ? 'Hide details' : 'Patient details'}</span>
            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" aria-hidden="true" /> : <ChevronDown className="w-3.5 h-3.5" aria-hidden="true" />}
          </button>
        </div>
      </div>

      {/* Secondary Demographics & Clinical Profile (Layer 2 - Progressively Disclosed) */}
      {isExpanded && (
        <div
          id="patient-secondary-details-drawer"
          role="region"
          aria-label="Additional patient details"
          className="pt-3 border-t border-slate-border-subtle grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs bg-slate-inset p-3 rounded-[var(--radius-md)]"
        >
          <div className="space-y-0.5">
            <span className="text-[10px] text-slate-text-muted font-semibold uppercase tracking-wider flex items-center">
              <Scale className="w-3 h-3 mr-1" aria-hidden="true" />
              Weight & body mass
            </span>
            <p className="num-clinical font-semibold text-slate-text-primary">
              {patient.weightKg} kg {patient.heightCm ? `• ${patient.heightCm} cm` : ''}
            </p>
          </div>

          <div className="space-y-0.5">
            <span className="text-[10px] text-slate-text-muted font-semibold uppercase tracking-wider flex items-center">
              <Droplets className="w-3 h-3 mr-1" aria-hidden="true" />
              Creatinine clearance
            </span>
            <p className="num-clinical font-semibold text-slate-text-primary">
              {patient.crcl ? `${patient.crcl} mL/min` : `${patient.egfr} mL/min (estimated)`}
            </p>
          </div>

          <div className="space-y-0.5">
            <span className="text-[10px] text-slate-text-muted font-semibold uppercase tracking-wider flex items-center">
              <Building2 className="w-3 h-3 mr-1" aria-hidden="true" />
              Location / ward
            </span>
            <p className="font-semibold text-slate-text-primary">
              {patient.ward || 'Inpatient general'} {patient.bed ? `• Bed ${patient.bed}` : ''}
            </p>
          </div>

          <div className="space-y-0.5">
            <span className="text-[10px] text-slate-text-muted font-semibold uppercase tracking-wider flex items-center">
              <FileText className="w-3 h-3 mr-1" aria-hidden="true" />
              Attending / admission
            </span>
            <p className="font-semibold text-slate-text-primary truncate">
              {patient.attendingClinician || 'Dr. J. Smith, MD'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

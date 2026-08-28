import React from 'react';
import { Filter, Globe, Bug, Pill } from 'lucide-react';

interface SurveillanceFiltersProps {
  selectedCountry: string;
  onCountryChange: (country: string) => void;
  availableCountries: string[];
  selectedPathogen: string;
  onPathogenChange: (pathogen: string) => void;
  availablePathogens: string[];
  selectedAntibiotic: string;
  onAntibioticChange: (antibiotic: string) => void;
  availableAntibiotics: string[];
  selectedYear?: number | 'All';
  onYearChange?: (year: number | 'All') => void;
}

const SELECT_CLASSES = 'focus-clinical rounded-[var(--radius-md)] border border-slate-border bg-slate-inset px-2.5 py-1.5 text-xs font-semibold text-slate-text-primary';

export function SurveillanceFilters({
  selectedCountry,
  onCountryChange,
  availableCountries,
  selectedPathogen,
  onPathogenChange,
  availablePathogens,
  selectedAntibiotic,
  onAntibioticChange,
  availableAntibiotics,
}: SurveillanceFiltersProps) {
  return (
    <div className="flex flex-wrap items-center gap-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-4 text-xs">
      <div className="flex shrink-0 items-center space-x-1 font-semibold uppercase tracking-wide text-slate-text-muted">
        <Filter className="h-4 w-4" aria-hidden="true" />
        <span>Surveillance filters:</span>
      </div>

      <div className="flex items-center space-x-1.5">
        <Globe className="h-3.5 w-3.5 shrink-0 text-slate-text-muted" aria-hidden="true" />
        <select id="soar-country-filter" value={selectedCountry} onChange={(e) => onCountryChange(e.target.value)} className={SELECT_CLASSES}>
          <option value="All">All regions</option>
          {availableCountries.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      <div className="flex items-center space-x-1.5">
        <Bug className="h-3.5 w-3.5 shrink-0 text-slate-text-muted" aria-hidden="true" />
        <select id="soar-pathogen-filter" value={selectedPathogen} onChange={(e) => onPathogenChange(e.target.value)} className={SELECT_CLASSES}>
          <option value="All">All pathogens</option>
          {availablePathogens.map((p) => <option key={p} value={p}>{p}</option>)}
        </select>
      </div>

      <div className="flex items-center space-x-1.5">
        <Pill className="h-3.5 w-3.5 shrink-0 text-slate-text-muted" aria-hidden="true" />
        <select id="soar-antibiotic-filter" value={selectedAntibiotic} onChange={(e) => onAntibioticChange(e.target.value)} className={SELECT_CLASSES}>
          <option value="All">All antibiotics</option>
          {availableAntibiotics.map((a) => <option key={a} value={a}>{a}</option>)}
        </select>
      </div>

      <button
        onClick={() => {
          onCountryChange('All');
          onPathogenChange('All');
          onAntibioticChange('All');
        }}
        className="focus-clinical ml-auto text-xs font-semibold text-[var(--color-clinical-400)] hover:underline"
      >
        Reset filters
      </button>
    </div>
  );
}

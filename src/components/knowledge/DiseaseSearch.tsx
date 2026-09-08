import React from 'react';
import { Filter } from 'lucide-react';
import { DynamicClinicalForm } from '@/forms/engine/DynamicClinicalForm';
import { ensureWhoSearchContractRegistered } from '@/plugins/contracts';
import { executeWhoSearchQuery } from '@/clinical/adapters/whoQueryAdapter';
import type { DiseaseSummary } from '@/types';

interface DiseaseSearchProps {
  onSearchResults: (query: string, diseases: DiseaseSummary[]) => void;
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
  categories: string[];
  totalResults: number;
}

export function DiseaseSearch({
  onSearchResults,
  selectedCategory,
  onCategoryChange,
  categories,
  totalResults,
}: DiseaseSearchProps) {
  const contract = ensureWhoSearchContractRegistered();

  return (
    <div className="flex flex-col justify-between gap-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-4 md:flex-row md:items-center">
      <div className="min-w-0 flex-1">
        <DynamicClinicalForm
          contract={contract}
          onSubmit={async (values) => {
            const diseases = await executeWhoSearchQuery(contract, values);
            onSearchResults(String(values.query_text), diseases);
          }}
        />
      </div>

      <div className="flex shrink-0 items-center space-x-2">
        <Filter className="h-4 w-4 shrink-0 text-slate-text-muted" aria-hidden="true" />
        <span className="text-xs font-semibold text-slate-text-secondary">Category:</span>
        <select
          id="who-category-select"
          value={selectedCategory}
          onChange={(e) => onCategoryChange(e.target.value)}
          className="focus-clinical rounded-[var(--radius-md)] border border-slate-border bg-slate-inset px-3 py-2 text-xs font-semibold text-slate-text-primary"
        >
          <option value="All">All categories ({categories.length})</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      <div className="num-clinical shrink-0 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset px-3 py-1.5 text-xs text-slate-text-muted">
        <span className="font-semibold text-[var(--color-clinical-400)]">{totalResults}</span>{' '}
        {totalResults === 1 ? 'guideline' : 'guidelines'} available
      </div>
    </div>
  );
}

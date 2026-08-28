import React from 'react';
import { Search, X, Filter } from 'lucide-react';

interface DiseaseSearchProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
  categories: string[];
  totalResults: number;
}

export function DiseaseSearch({
  searchQuery,
  onSearchChange,
  selectedCategory,
  onCategoryChange,
  categories,
  totalResults,
}: DiseaseSearchProps) {
  return (
    <div className="flex flex-col justify-between gap-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-4 md:flex-row md:items-center">
      <div className="relative flex-1">
        <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
        <input
          id="who-disease-search-input"
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search guidelines by disease, condition, pathogen, or keyword…"
          className="focus-clinical w-full rounded-[var(--radius-md)] border border-slate-border bg-slate-inset py-2.5 pl-10 pr-9 text-xs font-medium text-slate-text-primary placeholder-slate-text-muted"
        />
        {searchQuery && (
          <button
            type="button"
            onClick={() => onSearchChange('')}
            className="focus-clinical absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-text-muted hover:text-slate-text-primary"
            aria-label="Clear disease search"
            title="Clear search"
          >
            <X className="h-3.5 w-3.5" aria-hidden="true" />
          </button>
        )}
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

import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'motion/react';
import { Globe, BookOpen, AlertCircle, ChevronRight } from 'lucide-react';
import { DiseaseSummary, DiseaseDetail as DiseaseDetailType } from '@/types';
import { whoApi } from '@/api/whoApi';
import { DiseaseSearch } from './DiseaseSearch';
import { DiseaseDetail } from './DiseaseDetail';
import { StatusBadge, BadgeTone } from '@/components/ui/StatusBadge';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { SkeletonCard, Skeleton } from '@/components/ui/Skeleton';
import { cn } from '@/lib/utils';

const AWARE_TONE: Record<string, BadgeTone> = {
  Access: 'success',
  Watch: 'warning',
  Reserve: 'critical',
};

export function KnowledgeBaseExplorer() {
  const [diseases, setDiseases] = useState<DiseaseSummary[]>([]);
  const [selectedDiseaseId, setSelectedDiseaseId] = useState<string>('cap');
  const [selectedDiseaseDetail, setSelectedDiseaseDetail] = useState<DiseaseDetailType | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [isLoadingList, setIsLoadingList] = useState<boolean>(true);
  const [isLoadingDetail, setIsLoadingDetail] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const prefersReducedMotion = useReducedMotion();

  useEffect(() => {
    let isMounted = true;
    async function loadDiseases() {
      try {
        setIsLoadingList(true);
        setError(null);
        const data = await whoApi.getWhoDiseases();
        if (isMounted) {
          setDiseases(data);
          if (data.length > 0 && !selectedDiseaseId) setSelectedDiseaseId(data[0].id);
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load WHO guidelines.');
      } finally {
        if (isMounted) setIsLoadingList(false);
      }
    }
    loadDiseases();
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedDiseaseId) return;
    let isMounted = true;
    async function loadDetail() {
      try {
        setIsLoadingDetail(true);
        const detail = await whoApi.getWhoDiseaseById(selectedDiseaseId);
        if (isMounted) setSelectedDiseaseDetail(detail);
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load disease details.');
      } finally {
        if (isMounted) setIsLoadingDetail(false);
      }
    }
    loadDetail();
    return () => {
      isMounted = false;
    };
  }, [selectedDiseaseId]);

  const categories: string[] = Array.from(new Set(diseases.map((d) => d.category))).sort() as string[];

  const filteredDiseases = diseases.filter((d) => {
    const matchesCategory = selectedCategory === 'All' || d.category === selectedCategory;
    const q = searchQuery.toLowerCase().trim();
    const matchesSearch =
      !q ||
      d.name.toLowerCase().includes(q) ||
      d.category.toLowerCase().includes(q) ||
      d.commonPathogens.some((p) => p.toLowerCase().includes(q));
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col justify-between gap-4 rounded-[var(--radius-lg)] border border-[var(--color-clinical-800)] bg-gradient-to-br from-[var(--color-clinical-950)] to-slate-canvas p-6 sm:flex-row sm:items-center">
        <div>
          <div className="mb-1 flex items-center space-x-2">
            <Globe className="h-5 w-5 text-[var(--color-clinical-400)]" aria-hidden="true" />
            <h1 className="text-lg font-semibold text-slate-text-primary">WHO AWaRe knowledge base</h1>
          </div>
          <p className="text-xs text-[var(--color-clinical-200)]">
            The only registered knowledge plugin — authoritative guidelines, antimicrobial regimens, evidence
            grades, and Access / Watch / Reserve classification.
          </p>
        </div>
        <div className="flex items-center gap-1.5">
          <StatusBadge tone="success">Knowledge plugin</StatusBadge>
          <span className="num-clinical rounded-[var(--radius-sm)] border border-[var(--color-clinical-700)] bg-[var(--color-clinical-900)]/60 px-3 py-1.5 text-[10px] font-semibold text-[var(--color-clinical-200)]">
            WHO EML 2026
          </span>
        </div>
      </div>

      {/* AWaRe legend — belongs here, not on the dashboard, per progressive-disclosure design */}
      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset px-4 py-2.5 text-[11px] text-slate-text-muted">
        <span className="flex items-center gap-1.5"><StatusBadge tone="success">Access</StatusBadge> First/second-line, narrow-spectrum</span>
        <span className="flex items-center gap-1.5"><StatusBadge tone="warning">Watch</StatusBadge> Higher resistance potential, use judiciously</span>
        <span className="flex items-center gap-1.5"><StatusBadge tone="critical">Reserve</StatusBadge> Last-resort, multidrug-resistant organisms</span>
      </div>

      {error && <SafetyAlert level="warning" title="Knowledge base error">{error}</SafetyAlert>}

      <DiseaseSearch
        onSearchResults={(query, results) => {
          setSearchQuery(query);
          setDiseases(results);
          setSelectedDiseaseId(results[0]?.id || '');
        }}
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
        categories={categories}
        totalResults={filteredDiseases.length}
      />

      {/* Main Grid: Left Selector List & Right Detail View */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left: Disease List */}
        <div className="space-y-2 lg:col-span-4">
          <div className="px-1 text-xs font-semibold uppercase tracking-wide text-slate-text-muted">
            Guideline catalog
          </div>

          {isLoadingList ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i}>
                  <Skeleton className="h-16 rounded-[var(--radius-md)]" />
                </div>
              ))}
            </div>
          ) : filteredDiseases.length === 0 ? (
            <div className="rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-8 text-center">
              <AlertCircle className="mx-auto mb-2 h-5 w-5 text-slate-text-muted" aria-hidden="true" />
              <p className="text-xs text-slate-text-muted">No matching guidelines found.</p>
            </div>
          ) : (
            <div className="max-h-[700px] space-y-2 overflow-y-auto pr-1">
              {filteredDiseases.map((d, idx) => {
                const isSelected = selectedDiseaseId === d.id;
                return (
                  <motion.button
                    key={d.id}
                    id={`who-disease-card-${d.id}`}
                    onClick={() => setSelectedDiseaseId(d.id)}
                    initial={prefersReducedMotion ? false : { opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.15, delay: Math.min(idx * 0.02, 0.2) }}
                    aria-current={isSelected}
                    className={cn(
                      'focus-clinical w-full rounded-[var(--radius-md)] border p-3.5 text-left transition-colors duration-[var(--duration-fast)]',
                      isSelected
                        ? 'border-[var(--color-clinical-600)] bg-[var(--color-clinical-950)]/60'
                        : 'border-slate-border-subtle bg-slate-inset hover:border-slate-border',
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-semibold text-slate-text-muted">{d.category}</span>
                      <StatusBadge tone={AWARE_TONE[d.awareClass] ?? 'neutral'}>{d.awareClass}</StatusBadge>
                    </div>
                    <p className="mt-1 text-xs font-semibold text-slate-text-primary">{d.name}</p>
                    <div className="mt-2 flex items-center justify-between text-[11px] text-slate-text-muted">
                      <span>{d.commonPathogens.length} pathogens</span>
                      <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" />
                    </div>
                  </motion.button>
                );
              })}
            </div>
          )}
        </div>

        {/* Right: Disease Detail */}
        <div className="lg:col-span-8">
          {isLoadingDetail ? (
            <SkeletonCard lines={6} />
          ) : (
            <AnimatePresence mode="wait">
              {selectedDiseaseDetail ? (
                <motion.div
                  key={selectedDiseaseDetail.id}
                  initial={prefersReducedMotion ? false : { opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={prefersReducedMotion ? undefined : { opacity: 0, y: -8 }}
                  transition={{ duration: 0.2, ease: [0.2, 0.8, 0.2, 1] }}
                >
                  <DiseaseDetail disease={selectedDiseaseDetail} />
                </motion.div>
              ) : (
                <div className="rounded-[var(--radius-lg)] border border-dashed border-slate-border p-12 text-center">
                  <BookOpen className="mx-auto mb-2 h-8 w-8 text-slate-text-muted" aria-hidden="true" />
                  <p className="text-xs text-slate-text-muted">Select a guideline from the catalog to inspect details.</p>
                </div>
              )}
            </AnimatePresence>
          )}
        </div>
      </div>
    </div>
  );
}

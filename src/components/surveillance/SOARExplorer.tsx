import React, { useState, useEffect } from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { ShieldCheck } from 'lucide-react';
import { SoarDataPoint } from '@/types';
import { soarApi } from '@/api/soarApi';
import { SurveillanceFilters } from './SurveillanceFilters';
import { ResistanceSummary } from './ResistanceSummary';
import { ResistanceTrend } from './ResistanceTrend';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { SkeletonCard } from '@/components/ui/Skeleton';

export function SOARExplorer() {
  const [dataPoints, setDataPoints] = useState<SoarDataPoint[]>([]);
  const [availableCountries, setAvailableCountries] = useState<string[]>([]);
  const [availablePathogens, setAvailablePathogens] = useState<string[]>([]);
  const [availableAntibiotics, setAvailableAntibiotics] = useState<string[]>([]);

  const [selectedCountry, setSelectedCountry] = useState<string>('All');
  const [selectedPathogen, setSelectedPathogen] = useState<string>('All');
  const [selectedAntibiotic, setSelectedAntibiotic] = useState<string>('All');

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const prefersReducedMotion = useReducedMotion();

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      try {
        setIsLoading(true);
        setError(null);
        const [data, countries, pathogens, antibiotics] = await Promise.all([
          soarApi.getSoarData(),
          soarApi.getAvailableCountries(),
          soarApi.getAvailablePathogens(),
          soarApi.getAvailableAntibiotics(),
        ]);
        if (isMounted) {
          setDataPoints(data);
          setAvailableCountries(countries);
          setAvailablePathogens(pathogens);
          setAvailableAntibiotics(antibiotics);
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load SOAR surveillance dataset.');
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }
    loadData();
    return () => {
      isMounted = false;
    };
  }, []);

  const filteredData = dataPoints.filter((d) => {
    const matchCountry = selectedCountry === 'All' || d.country === selectedCountry;
    const matchPathogen = selectedPathogen === 'All' || d.pathogen === selectedPathogen;
    const matchAntibiotic = selectedAntibiotic === 'All' || d.antibiotic === selectedAntibiotic;
    return matchCountry && matchPathogen && matchAntibiotic;
  });

  const resistanceTone = (pct: number) => (pct >= 30 ? 'text-[var(--color-safety-critical)]' : pct >= 15 ? 'text-[var(--color-safety-warning)]' : 'text-[var(--color-safety-success)]');

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col justify-between gap-4 rounded-[var(--radius-lg)] border border-[var(--color-safety-success-border)] bg-gradient-to-br from-teal-950 to-slate-canvas p-6 sm:flex-row sm:items-center">
        <div>
          <div className="mb-1 flex items-center space-x-2">
            <ShieldCheck className="h-5 w-5 text-[var(--color-safety-success)]" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-slate-text-primary">SOAR surveillance prediction</h2>
          </div>
          <p className="text-xs text-[var(--color-safety-success)]">
            SOAR output is not exposed as a standalone surveillance dataset by the backend.
          </p>
        </div>
        <div className="flex items-center gap-1.5">
          <StatusBadge tone="warning">Not exposed by backend</StatusBadge>
          <span className="num-clinical rounded-[var(--radius-sm)] border border-[var(--color-safety-success-border)] bg-[var(--color-safety-success-bg)]/60 px-3 py-1.5 text-[10px] font-semibold text-[var(--color-safety-success)]">
            Version not exposed
          </span>
        </div>
      </div>

      <SurveillanceFilters
        selectedCountry={selectedCountry}
        onCountryChange={setSelectedCountry}
        availableCountries={availableCountries}
        selectedPathogen={selectedPathogen}
        onPathogenChange={setSelectedPathogen}
        availablePathogens={availablePathogens}
        selectedAntibiotic={selectedAntibiotic}
        onAntibioticChange={setSelectedAntibiotic}
        availableAntibiotics={availableAntibiotics}
      />

      {isLoading ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <SkeletonCard lines={1} />
            <SkeletonCard lines={1} />
            <SkeletonCard lines={1} />
          </div>
          <SkeletonCard lines={5} />
        </div>
      ) : error ? (
        <SafetyAlert level="critical" title="Surveillance data unavailable">{error}</SafetyAlert>
      ) : (
        <motion.div
          initial={prefersReducedMotion ? false : { opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="space-y-6"
        >
          <ResistanceSummary dataPoints={filteredData} />
          <ResistanceTrend dataPoints={filteredData} />

          <div className="space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-text-muted">
              Surveillance records ({filteredData.length} entries)
            </h3>

            {filteredData.length === 0 ? (
              <div className="rounded-[var(--radius-lg)] border border-dashed border-slate-border p-8 text-center text-xs text-slate-text-muted">
                No surveillance records match the current filters.
              </div>
            ) : (
              <div className="overflow-x-auto rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface">
                <table className="w-full text-left text-xs">
                  <thead className="border-b border-slate-border-subtle font-semibold text-slate-text-secondary">
                    <tr>
                      <th className="px-4 py-3">Country</th>
                      <th className="px-4 py-3">Year</th>
                      <th className="px-4 py-3">Target pathogen</th>
                      <th className="px-4 py-3">Antimicrobial agent</th>
                      <th className="px-4 py-3 text-right">Sample size</th>
                      <th className="px-4 py-3 text-right">Susceptible %</th>
                      <th className="px-4 py-3 text-right">Intermediate %</th>
                      <th className="px-4 py-3 text-right">Resistant %</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-border-subtle">
                    {filteredData.map((row) => (
                      <tr key={row.id} className="transition-colors duration-[var(--duration-fast)] hover:bg-slate-inset-hover">
                        <td className="px-4 py-3 font-semibold text-slate-text-primary">{row.country}</td>
                        <td className="num-clinical px-4 py-3 text-slate-text-muted">{row.year}</td>
                        <td className="px-4 py-3 italic font-medium text-slate-text-secondary">{row.pathogen}</td>
                        <td className="px-4 py-3 font-semibold text-[var(--color-clinical-400)]">{row.antibiotic}</td>
                        <td className="num-clinical px-4 py-3 text-right text-slate-text-muted">{row.sampleSize.toLocaleString()}</td>
                        <td className="num-clinical px-4 py-3 text-right font-semibold text-[var(--color-safety-success)]">{row.susceptiblePercent}%</td>
                        <td className="num-clinical px-4 py-3 text-right text-[var(--color-safety-warning)]">{row.intermediatePercent}%</td>
                        <td className={`num-clinical px-4 py-3 text-right font-semibold ${resistanceTone(row.resistancePercent)}`}>{row.resistancePercent}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </div>
  );
}

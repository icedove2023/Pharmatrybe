import React from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { AlertTriangle, ShieldCheck, Activity, TrendingUp } from 'lucide-react';
import { SoarDataPoint } from '@/types';

interface ResistanceSummaryProps {
  dataPoints: SoarDataPoint[];
}

export function ResistanceSummary({ dataPoints }: ResistanceSummaryProps) {
  const prefersReducedMotion = useReducedMotion();
  if (!dataPoints || dataPoints.length === 0) return null;

  const totalIsolates = dataPoints.reduce((acc, curr) => acc + curr.sampleSize, 0);
  const avgResistance = (dataPoints.reduce((acc, curr) => acc + curr.resistancePercent, 0) / dataPoints.length).toFixed(1);
  const avgSusceptibility = (dataPoints.reduce((acc, curr) => acc + curr.susceptiblePercent, 0) / dataPoints.length).toFixed(1);
  const highestResistance = [...dataPoints].sort((a, b) => b.resistancePercent - a.resistancePercent)[0];

  const cards = [
    {
      label: 'Surveillance isolates',
      icon: Activity,
      iconColor: 'text-[var(--color-clinical-400)]',
      value: totalIsolates.toLocaleString(),
      valueColor: 'text-slate-text-primary',
      note: `Across ${dataPoints.length} verified surveillance records`,
    },
    {
      label: 'Avg susceptibility',
      icon: ShieldCheck,
      iconColor: 'text-[var(--color-safety-success)]',
      value: `${avgSusceptibility}%`,
      valueColor: 'text-[var(--color-safety-success)]',
      note: 'Empiric effectiveness potential',
    },
    {
      label: 'Avg resistance',
      icon: AlertTriangle,
      iconColor: 'text-[var(--color-safety-warning)]',
      value: `${avgResistance}%`,
      valueColor: 'text-[var(--color-safety-warning)]',
      note: 'Across active filtered subset',
    },
    {
      label: 'Peak resistance flag',
      icon: TrendingUp,
      iconColor: 'text-[var(--color-safety-critical)]',
      value: `${highestResistance?.resistancePercent}%`,
      valueColor: 'text-[var(--color-safety-critical)]',
      note: `${highestResistance?.pathogen} vs ${highestResistance?.antibiotic}`,
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((c, idx) => {
        const Icon = c.icon;
        return (
          <motion.div
            key={c.label}
            initial={prefersReducedMotion ? false : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: idx * 0.05 }}
            className="space-y-1 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-4"
          >
            <div className="flex items-center justify-between text-xs text-slate-text-muted">
              <span className="text-[10px] font-semibold uppercase tracking-wide">{c.label}</span>
              <Icon className={`h-4 w-4 ${c.iconColor}`} aria-hidden="true" />
            </div>
            <p className={`num-clinical text-xl font-bold ${c.valueColor}`}>{c.value}</p>
            <p className="truncate text-[11px] text-slate-text-muted">{c.note}</p>
          </motion.div>
        );
      })}
    </div>
  );
}

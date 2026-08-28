import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart,
  Line,
} from 'recharts';
import { SoarDataPoint } from '@/types';

interface ResistanceTrendProps {
  dataPoints: SoarDataPoint[];
}

export function ResistanceTrend({ dataPoints }: ResistanceTrendProps) {
  if (!dataPoints || dataPoints.length === 0) {
    return (
      <div className="rounded-[var(--radius-lg)] border border-dashed border-slate-border bg-slate-inset p-8 text-center text-xs text-slate-text-muted">
        No surveillance data points available for current filter selection.
      </div>
    );
  }

  // Format chart data
  const chartData = dataPoints.map((d) => ({
    label: `${d.country} - ${d.year} (${d.antibiotic.substring(0, 4)})`,
    fullLabel: `${d.country} ${d.year} | ${d.pathogen} vs ${d.antibiotic}`,
    susceptible: d.susceptiblePercent,
    intermediate: d.intermediatePercent,
    resistant: d.resistancePercent,
    samples: d.sampleSize,
  }));

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-text-muted">
          Susceptibility & resistance proportions (% of isolates)
        </h3>
        <span className="text-[11px] text-slate-text-muted">
          Source: SOAR surveillance network
        </span>
      </div>

      <div className="h-72 w-full rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-3">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#263252" opacity={0.6} />
            <XAxis
              dataKey="label"
              tick={{ fontSize: 10, fill: '#7c8aa8' }}
              angle={-20}
              textAnchor="end"
              interval={0}
            />
            <YAxis tick={{ fontSize: 10, fill: '#7c8aa8' }} domain={[0, 100]} unit="%" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0b1220',
                border: '1px solid #263252',
                borderRadius: '8px',
                color: '#eef2f8',
                fontSize: '11px',
              }}
              formatter={(value: any, name: any) => [`${value}%`, name.toString().toUpperCase()]}
              labelFormatter={(label, items) => {
                const item = items?.[0]?.payload;
                return item ? item.fullLabel : label;
              }}
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
            <Bar dataKey="susceptible" name="Susceptible (S)" fill="#2e9e6e" stackId="a" radius={[0, 0, 0, 0]} animationDuration={600} />
            <Bar dataKey="intermediate" name="Intermediate (I)" fill="#c9862a" stackId="a" radius={[0, 0, 0, 0]} animationDuration={600} animationBegin={100} />
            <Bar dataKey="resistant" name="Resistant (R)" fill="#c4364c" stackId="a" radius={[4, 4, 0, 0]} animationDuration={600} animationBegin={200} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

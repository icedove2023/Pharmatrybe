import React from 'react';
import { cn } from '@/lib/utils';

export type BadgeTone = 'clinical' | 'critical' | 'warning' | 'success' | 'neutral' | 'planned';

const TONE_CLASSES: Record<BadgeTone, string> = {
  clinical:
    'bg-[var(--color-safety-info-bg)] text-[var(--color-safety-info)] border-[var(--color-safety-info-border)]',
  critical:
    'bg-[var(--color-safety-critical-bg)] text-[var(--color-safety-critical)] border-[var(--color-safety-critical-border)]',
  warning:
    'bg-[var(--color-safety-warning-bg)] text-[var(--color-safety-warning)] border-[var(--color-safety-warning-border)]',
  success:
    'bg-[var(--color-safety-success-bg)] text-[var(--color-safety-success)] border-[var(--color-safety-success-border)]',
  neutral: 'bg-slate-inset text-slate-text-secondary border-slate-border',
  planned: 'bg-slate-inset text-slate-text-muted border-slate-border border-dashed',
};

export interface StatusBadgeProps {
  tone?: BadgeTone;
  children: React.ReactNode;
  icon?: React.ElementType;
  className?: string;
}

/** Small, restrained status/classification pill. Never the sole carrier of meaning — pair with text. */
export function StatusBadge({ tone = 'neutral', children, icon: Icon, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-[var(--radius-xs)] border px-2 py-0.5 text-[11px] font-semibold uppercase leading-5 tracking-wide',
        TONE_CLASSES[tone],
        className,
      )}
    >
      {Icon && <Icon className="h-3 w-3" aria-hidden="true" />}
      {children}
    </span>
  );
}

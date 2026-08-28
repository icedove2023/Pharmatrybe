import React, { useEffect } from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { AlertTriangle, AlertOctagon, Info, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useNotificationStore } from '@/stores/notificationStore';

export type SafetyLevel = 'critical' | 'warning' | 'info' | 'success';

const LEVEL_CONFIG: Record<
  SafetyLevel,
  { icon: React.ElementType; label: string; classes: string; iconClasses: string }
> = {
  critical: {
    icon: AlertOctagon,
    label: 'Critical',
    classes: 'bg-[var(--color-safety-critical-bg)] border-[var(--color-safety-critical-border)] text-[var(--color-safety-critical)]',
    iconClasses: 'text-[var(--color-safety-critical)]',
  },
  warning: {
    icon: AlertTriangle,
    label: 'Warning',
    classes: 'bg-[var(--color-safety-warning-bg)] border-[var(--color-safety-warning-border)] text-[var(--color-safety-warning)]',
    iconClasses: 'text-[var(--color-safety-warning)]',
  },
  info: {
    icon: Info,
    label: 'Information',
    classes: 'bg-[var(--color-safety-info-bg)] border-[var(--color-safety-info-border)] text-[var(--color-safety-info)]',
    iconClasses: 'text-[var(--color-safety-info)]',
  },
  success: {
    icon: CheckCircle2,
    label: 'Verified safe',
    classes: 'bg-[var(--color-safety-success-bg)] border-[var(--color-safety-success-border)] text-[var(--color-safety-success)]',
    iconClasses: 'text-[var(--color-safety-success)]',
  },
};

export interface SafetyAlertProps {
  level: SafetyLevel;
  title: string;
  children?: React.ReactNode;
  /** Override the default semantic label shown above the title (e.g. "Allergy conflict") */
  eyebrow?: string;
  className?: string;
  actions?: React.ReactNode;
}

/**
 * Canonical clinical alert. Never relies on colour alone — always pairs
 * icon + semantic label + heading text, and exposes role="alert" for
 * critical/warning levels so screen readers announce it immediately.
 */
export function SafetyAlert({ level, title, children, eyebrow, className, actions }: SafetyAlertProps) {
  const cfg = LEVEL_CONFIG[level];
  const Icon = cfg.icon;
  const isUrgent = level === 'critical' || level === 'warning';
  const prefersReducedMotion = useReducedMotion();

  useEffect(() => {
    useNotificationStore.getState().publish({
      id: `alert:${level}:${eyebrow ?? cfg.label}:${title}`,
      level,
      title,
      message: typeof children === 'string' ? children : undefined,
    });
  }, [children, cfg.label, eyebrow, level, title]);

  return (
    <motion.div
      role={isUrgent ? 'alert' : 'status'}
      aria-live={isUrgent ? 'assertive' : 'polite'}
      initial={prefersReducedMotion || !isUrgent ? false : { opacity: 0, scale: 0.98, y: -4 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.22, ease: [0.2, 0.8, 0.2, 1] }}
      className={cn('flex gap-3 rounded-[var(--radius-lg)] border p-4 shadow-clinical-xs', cfg.classes, className)}
    >
      <Icon className={cn('mt-0.5 h-5 w-5 flex-none', cfg.iconClasses)} aria-hidden="true" />
      <div className="min-w-0 flex-1">
        <p className="text-[11px] font-semibold uppercase tracking-wide opacity-80">
          {eyebrow ?? cfg.label}
        </p>
        <p className="mt-0.5 text-sm font-semibold leading-snug">{title}</p>
        {children && <div className="mt-1.5 text-[13px] leading-relaxed opacity-90">{children}</div>}
        {actions && <div className="mt-3 flex flex-wrap gap-2">{actions}</div>}
      </div>
    </motion.div>
  );
}

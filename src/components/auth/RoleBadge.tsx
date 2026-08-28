import React from 'react';
import { UserRole } from '@/types/auth';
import { ShieldCheck, Stethoscope, FlaskConical, Pill, UserCheck } from 'lucide-react';
import { cn } from '@/lib/utils';

interface RoleBadgeProps {
  role: UserRole;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  className?: string;
}

function getRoleConfig(userRole: UserRole) {
  switch (userRole) {
    case 'Admin':
      return {
        label: 'Platform Admin',
        bg: 'bg-[var(--color-safety-info-bg)] text-[var(--color-safety-info)] dark:bg-[var(--color-safety-info-bg)]/60 dark:text-[var(--color-safety-info)] border-[var(--color-safety-info-border)] dark:border-[var(--color-safety-info-border)]',
        icon: ShieldCheck,
        iconColor: 'text-[var(--color-safety-info)] dark:text-[var(--color-safety-info)]',
      };
    case 'Researcher':
      return {
        label: 'Clinical Researcher',
        bg: 'bg-[var(--color-safety-warning-bg)] text-[var(--color-safety-warning)] dark:bg-[var(--color-safety-warning-bg)] dark:text-[var(--color-safety-warning)] border-[var(--color-safety-warning-border)] dark:border-[var(--color-safety-warning-border)]',
        icon: FlaskConical,
        iconColor: 'text-[var(--color-safety-warning)] dark:text-[var(--color-safety-warning)]',
      };
    case 'Pharmacist':
      return {
        label: 'Clinical Pharmacist',
        bg: 'bg-[var(--color-safety-success-bg)] text-[var(--color-safety-success)] dark:bg-[var(--color-safety-success-bg)]/60 dark:text-[var(--color-safety-success)] border-[var(--color-safety-success-border)] dark:border-[var(--color-safety-success-border)]',
        icon: Pill,
        iconColor: 'text-[var(--color-safety-success)] dark:text-[var(--color-safety-success)]',
      };
    case 'General Practitioner':
      return {
        label: 'General Practitioner',
        bg: 'bg-[var(--color-safety-info-bg)] text-[var(--color-safety-info)] dark:bg-[var(--color-safety-info-bg)]/60 dark:text-[var(--color-safety-info)] border-[var(--color-safety-info-border)] dark:border-[var(--color-safety-info-border)]',
        icon: UserCheck,
        iconColor: 'text-[var(--color-safety-info)] dark:text-[var(--color-safety-info)]',
      };
    case 'Infectious Disease Specialist':
    default:
      return {
        label: 'Infectious Disease Clinician',
        bg: 'bg-[var(--color-clinical-100)] text-[var(--color-clinical-800)] dark:bg-[var(--color-clinical-950)] dark:text-[var(--color-clinical-300)] border-[var(--color-clinical-200)] dark:border-[var(--color-clinical-700)]',
        icon: Stethoscope,
        iconColor: 'text-[var(--color-clinical-500)] dark:text-[var(--color-clinical-400)]',
      };
  }
}

/** Distinct role-differentiating badge. Uses the same radius scale as StatusBadge for consistency. */
export function RoleBadge({ role, size = 'md', showIcon = true, className = '' }: RoleBadgeProps) {
  const config = getRoleConfig(role);
  const Icon = config.icon;

  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5 space-x-1',
    md: 'text-xs px-2.5 py-1 space-x-1.5',
    lg: 'text-sm px-3.5 py-1.5 space-x-2',
  }[size];

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  }[size];

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-[var(--radius-sm)] border font-semibold',
        config.bg,
        sizeClasses,
        className,
      )}
    >
      {showIcon && <Icon className={cn(iconSizes, config.iconColor, 'shrink-0')} aria-hidden="true" />}
      <span className="truncate">{config.label}</span>
    </span>
  );
}

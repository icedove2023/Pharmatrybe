import React from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export type ButtonVariant = 'primary' | 'secondary' | 'destructive' | 'ghost' | 'outline';
export type ButtonSize = 'sm' | 'md' | 'lg';

const VARIANT_CLASSES: Record<ButtonVariant, string> = {
  primary:
    'bg-[var(--color-clinical-600)] text-white shadow-clinical-sm hover:bg-[var(--color-clinical-500)] active:bg-[var(--color-clinical-700)]',
  secondary:
    'bg-slate-surface-raised text-slate-text-primary border border-slate-border shadow-clinical-xs hover:bg-slate-inset-hover hover:border-[var(--color-clinical-300)] active:bg-slate-inset',
  destructive:
    'bg-[var(--color-safety-critical)] text-white shadow-clinical-sm hover:opacity-90 active:opacity-100',
  outline:
    'bg-transparent text-slate-text-secondary border border-slate-border hover:border-[var(--color-clinical-400)] hover:text-[var(--color-clinical-600)] hover:bg-[var(--color-clinical-50)]/60',
  ghost:
    'bg-transparent text-slate-text-secondary hover:bg-slate-inset-hover hover:text-slate-text-primary',
};

const SIZE_CLASSES: Record<ButtonSize, string> = {
  sm: 'h-8 px-3 text-xs gap-1.5 rounded-[var(--radius-sm)]',
  md: 'h-10 px-4 text-sm gap-2 rounded-[var(--radius-sm)]',
  lg: 'h-11 px-5 text-sm gap-2 rounded-[var(--radius-md)]',
};

export interface ClinicalButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: React.ElementType;
  loading?: boolean;
}

export const ClinicalButton = React.forwardRef<HTMLButtonElement, ClinicalButtonProps>(
  (
    { variant = 'secondary', size = 'md', icon: Icon, loading, className, children, disabled, ...props },
    ref,
  ) => {
    const prefersReducedMotion = useReducedMotion();
    const iconSize = size === 'sm' ? 'h-3.5 w-3.5' : 'h-4 w-4';

    return (
      <motion.button
        ref={ref}
        disabled={disabled || loading}
        aria-busy={loading || undefined}
        whileTap={disabled || loading || prefersReducedMotion ? undefined : { scale: 0.975 }}
        transition={{ duration: 0.1 }}
        className={cn(
          'focus-clinical relative inline-flex select-none items-center justify-center font-semibold tracking-[-0.005em]',
          'transition-[background-color,border-color,color,box-shadow,opacity] duration-[var(--duration-fast)] ease-[var(--ease-clinical)]',
          'disabled:cursor-not-allowed disabled:opacity-55 disabled:shadow-none',
          VARIANT_CLASSES[variant],
          SIZE_CLASSES[size],
          className,
        )}
        {...(props as React.ComponentProps<typeof motion.button>)}
      >
        {loading ? (
            <Loader2 className={cn(iconSize, 'shrink-0 animate-spin')} aria-hidden="true" />
        ) : (
          Icon && <Icon className={cn(iconSize, 'shrink-0')} aria-hidden="true" />
        )}
        {children}
      </motion.button>
    );
  },
);

ClinicalButton.displayName = 'ClinicalButton';

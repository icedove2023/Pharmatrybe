import React, { useId, useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface AccordionProps {
  /** Must clearly describe what will appear, e.g. "View supporting evidence" — never "More" or "Details" */
  title: string;
  subtitle?: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
  className?: string;
  icon?: React.ElementType;
}

/** Accessible single-panel disclosure for secondary clinical/technical content. */
export function Accordion({ title, subtitle, defaultOpen = false, children, className, icon: Icon }: AccordionProps) {
  const [open, setOpen] = useState(defaultOpen);
  const panelId = useId();

  return (
    <div className={cn('overflow-hidden rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface shadow-clinical-xs transition-colors duration-[var(--duration-fast)] hover:border-[var(--color-clinical-300)]', className)}>
      <button
        type="button"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((o) => !o)}
        className="focus-clinical flex w-full items-center justify-between gap-3 px-4 py-3.5 text-left transition-colors duration-[var(--duration-fast)] hover:bg-slate-inset/60"
      >
        <span className="flex items-center gap-2 min-w-0">
          {Icon && <Icon className="h-4 w-4 flex-none text-[var(--color-clinical-500)]" aria-hidden="true" />}
          <span className="min-w-0">
            <span className="block text-sm font-medium text-slate-text-primary">{title}</span>
            {subtitle && <span className="block text-xs text-slate-text-muted">{subtitle}</span>}
          </span>
        </span>
        <ChevronDown
          className={cn('h-4 w-4 flex-none text-slate-text-muted transition-transform duration-[var(--duration-base)]', open && 'rotate-180')}
          aria-hidden="true"
        />
      </button>
      <div
        id={panelId}
        role="region"
        className={cn(
          'grid transition-[grid-template-rows] duration-[var(--duration-base)] ease-[var(--ease-clinical)]',
          open ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]',
        )}
      >
        <div className="overflow-hidden">
          <div className="border-t border-slate-border-subtle px-4 py-3">{children}</div>
        </div>
      </div>
    </div>
  );
}

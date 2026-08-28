import React from 'react';
import { ChevronRight, Home } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface BreadcrumbItem {
  label: string;
  tabId?: string;
  active?: boolean;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  onNavigate?: (tabId: string) => void;
}

export function Breadcrumbs({ items, onNavigate }: BreadcrumbsProps) {
  return (
    <nav aria-label="Breadcrumb" className="mb-4 flex select-none items-center space-x-1.5 text-xs text-slate-text-muted">
      <button
        onClick={() => onNavigate?.('dashboard')}
        className="focus-clinical flex items-center rounded-[var(--radius-sm)] p-1 transition-colors duration-[var(--duration-fast)] hover:text-slate-text-primary"
        title="Go to dashboard"
      >
        <Home className="h-3.5 w-3.5" aria-hidden="true" />
      </button>

      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        return (
          <React.Fragment key={`${item.label}-${index}`}>
            <ChevronRight className="h-3.5 w-3.5 shrink-0 text-slate-text-muted" aria-hidden="true" />
            {isLast || !item.tabId ? (
              <span
                className={cn(
                  'max-w-[240px] truncate font-semibold',
                  isLast ? 'text-slate-text-primary' : 'text-slate-text-secondary',
                )}
              >
                {item.label}
              </span>
            ) : (
              <button
                onClick={() => item.tabId && onNavigate?.(item.tabId)}
                className="focus-clinical max-w-[200px] truncate font-medium text-slate-text-secondary transition-colors duration-[var(--duration-fast)] hover:text-[var(--color-clinical-400)]"
              >
                {item.label}
              </button>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}

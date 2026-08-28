import React from 'react';
import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
  style?: React.CSSProperties;
}

/** Shimmering placeholder block. Communicates pipeline transparency during loads. */
export function Skeleton({ className, style }: SkeletonProps) {
  return (
    <div
      style={style}
      className={cn(
        'relative overflow-hidden rounded-[var(--radius-sm)] bg-slate-inset',
        className,
      )}
    >
      <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.6s_ease-in-out_infinite] bg-gradient-to-r from-transparent via-slate-surface/70 to-transparent dark:via-white/6" />
    </div>
  );
}

export function SkeletonCard({ lines = 3, className }: { lines?: number; className?: string }) {
  return (
    <div className={cn('space-y-3 card-clinical p-5', className)}>
      <Skeleton className="h-4 w-1/3" />
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, i) => (
          <div key={i}>
            <Skeleton className="h-3" style={i === lines - 1 ? { width: '70%' } : undefined} />
          </div>
        ))}
      </div>
    </div>
  );
}

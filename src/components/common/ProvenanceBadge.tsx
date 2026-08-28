import React from 'react';
import { DataProvenance } from '@/types/provenance';
import { Database, Eye, Settings, HelpCircle, AlertCircle } from 'lucide-react';

interface ProvenanceBadgeProps {
  provenance: DataProvenance;
  customLabel?: string;
  size?: 'xs' | 'sm' | 'md';
  showIcon?: boolean;
}

export function ProvenanceBadge({
  provenance,
  customLabel,
  size = 'xs',
  showIcon = true,
}: ProvenanceBadgeProps) {
  const getDetails = () => {
    switch (provenance) {
      case 'backend_authoritative':
        return {
          label: customLabel || 'Backend Verified',
          icon: Database,
          classes:
            'bg-[var(--color-safety-success-bg)]/10 text-[var(--color-safety-success)] dark:text-[var(--color-safety-success)] border-[var(--color-safety-success-border)]/20',
          ariaLabel: 'Provenance: Backend Authoritative Data',
        };
      case 'client_observed':
        return {
          label: customLabel || 'Observed from Client',
          icon: Eye,
          classes:
            'bg-[var(--color-safety-info-bg)]/10 text-[var(--color-safety-info)] dark:text-[var(--color-safety-info)] border-[var(--color-safety-info-border)]/20',
          ariaLabel: 'Provenance: Client-Observed Response Telemetry',
        };
      case 'static_configuration':
        return {
          label: customLabel || 'Static Configuration',
          icon: Settings,
          classes:
            'bg-[var(--color-safety-info-bg)]/10 text-[var(--color-safety-info)] dark:text-[var(--color-safety-info)] border-[var(--color-safety-info-border)]/20',
          ariaLabel: 'Provenance: Static Baseline Configuration',
        };
      case 'demo_fixture':
        return {
          label: customLabel || 'Demo / Baseline Fixture',
          icon: HelpCircle,
          classes:
            'bg-[var(--color-safety-warning-bg)]/10 text-[var(--color-safety-warning)] dark:text-[var(--color-safety-warning)] border-[var(--color-safety-warning-border)]/20',
          ariaLabel: 'Provenance: Demo Baseline Fixture (Non-Authoritative)',
        };
      case 'unavailable':
      default:
        return {
          label: customLabel || 'Not Exposed by Backend',
          icon: AlertCircle,
          classes:
            'bg-slate-inset text-slate-text-secondary border-slate-border',
          ariaLabel: 'Provenance: Telemetry Not Exposed by Backend',
        };
    }
  };

  const details = getDetails();
  const Icon = details.icon;

  const sizeClasses = {
    xs: 'text-[9px] px-1.5 py-0.5',
    sm: 'text-[10px] px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
  }[size];

  const iconSizes = {
    xs: 'w-2.5 h-2.5',
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
  }[size];

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-[var(--radius-xs)] border font-semibold ${details.classes} ${sizeClasses}`}
      role="status"
      aria-label={details.ariaLabel}
      title={details.ariaLabel}
    >
      {showIcon && <Icon className={`${iconSizes} shrink-0`} aria-hidden="true" />}
      <span>{details.label}</span>
    </span>
  );
}

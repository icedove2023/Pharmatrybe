/**
 * Phase 11: Plugin Status & Accessibility Helpers
 * Provides accessible labels, badges, and status formatting without relying on color alone.
 */

import { PluginCategory, PluginStatus } from './pluginTypes';

export interface StatusPresentation {
  status: PluginStatus;
  label: string;
  badgeClass: string;
  dotClass: string;
  ariaLabel: string;
  description: string;
}

export function getPluginStatusPresentation(status: PluginStatus): StatusPresentation {
  switch (status) {
    case 'available':
      return {
        status: 'available',
        label: 'Available',
        badgeClass: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800',
        dotClass: 'bg-emerald-500',
        ariaLabel: 'Plugin Status: Available and active',
        description: 'Component is operational and participating in the recommendation pipeline.',
      };
    case 'unavailable':
      return {
        status: 'unavailable',
        label: 'Unavailable',
        badgeClass: 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border-rose-300 dark:border-rose-800',
        dotClass: 'bg-rose-500',
        ariaLabel: 'Plugin Status: Unavailable',
        description: 'Component is offline or explicitly reported as unavailable by the backend.',
      };
    case 'degraded':
      return {
        status: 'degraded',
        label: 'Degraded',
        badgeClass: 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border-amber-300 dark:border-amber-800',
        dotClass: 'bg-amber-500',
        ariaLabel: 'Plugin Status: Operating in degraded mode',
        description: 'Component is functioning with partial capabilities or increased latency.',
      };
    case 'unknown':
    default:
      return {
        status: 'unknown',
        label: 'Not exposed by backend',
        badgeClass: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-300 dark:border-slate-700',
        dotClass: 'bg-slate-400',
        ariaLabel: 'Plugin Status: Unknown (Not exposed by standalone backend endpoint)',
        description: 'Live standalone status is not exposed by backend. Component is consumed via canonical pipeline.',
      };
  }
}

export function getCategoryBadge(category: PluginCategory): { label: string; badgeClass: string } {
  switch (category) {
    case 'knowledge':
      return {
        label: 'Knowledge Base',
        badgeClass: 'bg-teal-100 text-teal-800 dark:bg-teal-950 dark:text-teal-300 border-teal-300 dark:border-teal-800',
      };
    case 'prediction':
      return {
        label: 'Prediction Engine',
        badgeClass: 'bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300 border-purple-300 dark:border-purple-800',
      };
    case 'rules':
      return {
        label: 'Rules & Safety',
        badgeClass: 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border-rose-300 dark:border-rose-800',
      };
    case 'fusion':
      return {
        label: 'Decision Fusion',
        badgeClass: 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 border-blue-300 dark:border-blue-800',
      };
    case 'explainability':
      return {
        label: 'Explainability (XAI)',
        badgeClass: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300 border-indigo-300 dark:border-indigo-800',
      };
    case 'audit':
      return {
        label: 'Audit & Telemetry',
        badgeClass: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300 border-slate-300 dark:border-slate-700',
      };
    case 'risk':
      return {
        label: 'Clinical Risk',
        badgeClass: 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border-amber-300 dark:border-amber-800',
      };
    case 'reporting':
      return {
        label: 'Reporting',
        badgeClass: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-950 dark:text-cyan-300 border-cyan-300 dark:border-cyan-800',
      };
    case 'integration':
      return {
        label: 'Integration',
        badgeClass: 'bg-sky-100 text-sky-800 dark:bg-sky-950 dark:text-sky-300 border-sky-300 dark:border-sky-800',
      };
    default:
      return {
        label: category,
        badgeClass: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-300 dark:border-slate-700',
      };
  }
}

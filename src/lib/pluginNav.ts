import { Globe, ShieldCheck, TestTube2, BookOpen, ClipboardList, Building2, Puzzle } from 'lucide-react';
import { PluginInfo } from '@/types';

export interface PluginNavMeta {
  /** activeTab route id used by App.tsx / Sidebar */
  route: string;
  icon: typeof Globe;
  /** Short nav label, distinct from the full plugin name shown in the explorer itself */
  navLabel: string;
  /** Whether a dedicated, specialized explorer UI exists for this plugin */
  hasDedicatedExplorer: boolean;
}

/**
 * Known registered plugins get a dedicated route + specialized explorer UI.
 * Any other plugin the backend reports still surfaces in navigation and
 * routes to the generic PluginExplorerView (honest metadata, no fabricated
 * specialized UI) rather than being silently dropped.
 */
const KNOWN_PLUGIN_META: Record<string, PluginNavMeta> = {
  who_aware: { route: 'who', icon: Globe, navLabel: 'WHO AWaRe', hasDedicatedExplorer: true },
  soar: { route: 'soar', icon: ShieldCheck, navLabel: 'SOAR', hasDedicatedExplorer: true },
  armd: { route: 'armd', icon: TestTube2, navLabel: 'ARMD', hasDedicatedExplorer: true },
};

const FALLBACK_ICONS = [BookOpen, ClipboardList, Building2, Puzzle];

export function getPluginNavMeta(plugin: PluginInfo): PluginNavMeta {
  const known = KNOWN_PLUGIN_META[plugin.id];
  if (known) return known;

  // Deterministic fallback icon so the same unregistered plugin always renders the same way
  const hash = plugin.id.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
  const icon = FALLBACK_ICONS[hash % FALLBACK_ICONS.length];

  return {
    route: `plugin:${plugin.id}`,
    icon,
    navLabel: plugin.name.replace(/\s*(Plugin|Knowledge Plugin)$/i, ''),
    hasDedicatedExplorer: false,
  };
}

export function isPluginRoute(route: string): boolean {
  return route.startsWith('plugin:');
}

export function pluginIdFromRoute(route: string): string {
  return route.replace(/^plugin:/, '');
}

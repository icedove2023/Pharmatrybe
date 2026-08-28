import React from 'react';
import {
  LayoutDashboard, Stethoscope, BrainCircuit, History, UsersRound, Shield, Settings, Pill,
  ChevronLeft, ChevronRight, Cpu, Activity, X, Puzzle,
} from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { usePluginRegistry } from '@/hooks/usePluginRegistry';
import { getPluginNavMeta } from '@/lib/pluginNav';
import { RoleBadge } from '@/components/auth/RoleBadge';
import { UserRole } from '@/types/auth';
import { cn } from '@/lib/utils';

interface SidebarProps {
  activeTab: string;
  onSelectTab: (tab: string) => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
  isMobileOpen?: boolean;
  onCloseMobile?: () => void;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  requiredPermission?: string;
}

export function Sidebar({
  activeTab,
  onSelectTab,
  isCollapsed = false,
  onToggleCollapse,
  isMobileOpen = false,
  onCloseMobile,
}: SidebarProps) {
  const { user } = useAuthStore();
  const can = useAuthStore((state) => state.can);
  const { data: plugins } = usePluginRegistry();

  // Backend capability truth: nav items for Knowledge & Surveillance are
  // generated directly from the registered plugin list — never hardcoded —
  // so the sidebar can never drift from what the backend actually reports.
  // WHO AWaRe, SOAR, and ARMD get their specialized routes; any additional
  // registered plugin (e.g. other KNOWLEDGE sources) still appears, routed
  // to the generic plugin explorer instead of being silently hidden.
  const clinicalItems: NavItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    {
      id: 'assessment',
      label: 'New assessment',
      icon: Stethoscope,
      requiredPermission: 'cases:create',
    },
    { id: 'patients', label: 'Patients', icon: UsersRound },
  ];

  const knowledgeSurveillanceItems: NavItem[] = (plugins ?? []).map((plugin) => {
    const meta = getPluginNavMeta(plugin);
    return {
      id: meta.route,
      label: meta.navLabel,
      icon: meta.icon,
      requiredPermission: plugin.type === 'PREDICTION' ? 'plugins:view' : 'guidelines:view',
    };
  });

  const administrationItems: NavItem[] = [
    { id: 'governance-telemetry', label: 'System health & governance', icon: Activity, requiredPermission: 'professionals:manage' },
    {
      id: 'telemetry',
      label: 'Plugin & telemetry hub',
      icon: Cpu,
      requiredPermission: 'plugins:configure',
    },
    { id: 'plugin-governance', label: 'Plugin governance', icon: Puzzle, requiredPermission: 'plugins:configure' },
    { id: 'admin', label: 'professionals & invitations', icon: UsersRound, requiredPermission: 'professionals:manage' },
  ];

  const handleItemClick = (id: string) => {
    onSelectTab(id);
    onCloseMobile?.();
  };

  const renderNavGroup = (title: string, items: NavItem[]) => {
    const visibleItems = items.filter((item) => {
      return !item.requiredPermission || can(item.requiredPermission);
    });

    if (visibleItems.length === 0) return null;

    return (
      <div className="space-y-1">
        {!isCollapsed ? (
          <p className="px-3 pb-1 text-[10px] font-semibold uppercase tracking-[0.08em] text-slate-text-muted">{title}</p>
        ) : (
          <div className="mx-auto my-2 h-px w-6 bg-slate-border" aria-hidden="true" />
        )}
        {visibleItems.map((item) => {
          const isActive = activeTab === item.id;
          const Icon = item.icon;

          return (
            <button
              key={item.id}
              onClick={() => handleItemClick(item.id)}
              title={isCollapsed ? item.label : undefined}
              aria-current={isActive ? 'page' : undefined}
              className={cn(
                'focus-clinical group relative flex w-full items-center rounded-[var(--radius-md)] text-[13px] font-medium transition-[background-color,color] duration-[var(--duration-fast)] ease-[var(--ease-clinical)]',
                isCollapsed ? 'justify-center px-2 py-2.5' : 'justify-between px-3 py-2.5',
                isActive
                  ? 'bg-[var(--color-clinical-600)] font-semibold text-white shadow-clinical-sm'
                  : 'text-slate-text-secondary hover:bg-slate-inset-hover hover:text-slate-text-primary',
              )}
            >
              <div className="flex min-w-0 items-center space-x-2.5">
                <Icon
                  className={cn(
                    'h-[18px] w-[18px] shrink-0 transition-colors duration-[var(--duration-fast)]',
                    isActive ? 'text-white' : 'text-slate-text-muted group-hover:text-[var(--color-clinical-500)]',
                  )}
                  aria-hidden="true"
                />
                {!isCollapsed && <span className="truncate">{item.label}</span>}
              </div>
              {isActive && !isCollapsed && (
                <span className="ml-2 h-1.5 w-1.5 shrink-0 rounded-full bg-white/80" aria-hidden="true" />
              )}
            </button>
          );
        })}
      </div>
    );
  };

  const sidebarContent = (
    <div className="flex h-full select-none flex-col bg-slate-surface text-slate-text-primary">
      {/* Brand Header */}
      <div
        className={cn(
          'flex h-16 shrink-0 items-center border-b border-slate-border-subtle bg-slate-surface',
          isCollapsed ? 'justify-center px-2' : 'justify-between px-4',
        )}
      >
        <div className="flex min-w-0 items-center space-x-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-clinical-600)] shadow-clinical-sm">
            <Pill className="h-5 w-5 text-white" aria-hidden="true" />
          </div>
          {!isCollapsed && (
            <div className="min-w-0">
              <h1 className="flex items-center text-sm font-bold tracking-tight text-slate-text-primary">
                PharmaTrybe
                <span className="ml-1.5 rounded-[var(--radius-xs)] border border-[var(--color-safety-info-border)] bg-[var(--color-safety-info-bg)] px-1.5 py-px text-[9px] font-semibold tracking-wide text-[var(--color-safety-info)]">
                  CDSS
                </span>
              </h1>
              <p className="truncate text-[10px] font-medium text-slate-text-muted">Explainable Antimicrobial AI</p>
            </div>
          )}
        </div>

        {isMobileOpen && (
          <button
            onClick={onCloseMobile}
            aria-label="Close navigation"
            className="focus-clinical rounded-[var(--radius-sm)] p-1 text-slate-text-muted hover:text-slate-text-primary lg:hidden"
          >
            <X className="h-5 w-5" aria-hidden="true" />
          </button>
        )}
      </div>

      {/* Navigation Sections */}
      <nav className="flex-1 space-y-5 overflow-y-auto p-3">
        {renderNavGroup('Clinical', clinicalItems)}
        {renderNavGroup('Knowledge & surveillance', knowledgeSurveillanceItems)}
        {renderNavGroup('Administration', administrationItems)}
      </nav>

      {/* Footer Controls & Collapse Toggle */}
      <div className="shrink-0 space-y-2 border-t border-slate-border-subtle bg-slate-canvas/40 p-3">
        {!isCollapsed && user && (
          <div className="space-y-1.5 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-canvas/60 p-2.5 text-xs">
            <div className="flex items-center justify-between">
              <span className="flex items-center text-[10px] font-semibold uppercase tracking-wide text-slate-text-muted">
                Active identity
              </span>
              <span className="h-1.5 w-1.5 rounded-full bg-[var(--color-safety-success)]" />
            </div>
            <p className="truncate font-semibold text-slate-text-primary">{user.name}</p>
            <RoleBadge role={user.role} size="sm" />
          </div>
        )}

        {onToggleCollapse && (
          <button
            onClick={onToggleCollapse}
            className="focus-clinical hidden w-full items-center justify-center rounded-[var(--radius-sm)] p-2 text-xs text-slate-text-muted transition-colors duration-[var(--duration-fast)] hover:bg-slate-inset-hover hover:text-slate-text-primary lg:flex"
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? (
              <ChevronRight className="h-4 w-4" aria-hidden="true" />
            ) : (
              <span className="flex items-center space-x-2 text-slate-text-muted">
                <ChevronLeft className="h-4 w-4" aria-hidden="true" />
                <span className="text-[11px] font-medium">Collapse navigation</span>
              </span>
            )}
          </button>
        )}
      </div>
    </div>
  );

  return (
    <>
      <aside
        className={cn(
          'sticky top-0 hidden h-screen shrink-0 flex-col border-r border-slate-border transition-[width] duration-[var(--duration-slow)] ease-[var(--ease-clinical)] lg:flex',
          isCollapsed ? 'w-20' : 'w-64',
        )}
      >
        {sidebarContent}
      </aside>

      {isMobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="fixed inset-0 bg-black/50 backdrop-blur-[2px] animate-fade-in" onClick={onCloseMobile} />
          <div className="fixed inset-y-0 left-0 z-10 w-72 max-w-full border-r border-slate-border shadow-clinical-lg animate-fade-in">{sidebarContent}</div>
        </div>
      )}
    </>
  );
}

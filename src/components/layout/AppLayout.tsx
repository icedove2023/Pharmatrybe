import React, { useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'motion/react';
import { Sidebar } from '@/components/common/Sidebar';
import { Header } from '@/components/common/Header';
import { Breadcrumbs, BreadcrumbItem } from '@/components/common/Breadcrumbs';
import { PatientContextBanner, PatientContextData } from '@/components/common/PatientContextBanner';

interface AppLayoutProps {
  activeTab: string;
  onSelectTab: (tab: string) => void;
  breadcrumbs?: BreadcrumbItem[];
  patientContext?: PatientContextData | null;
  children: React.ReactNode;
}

export function AppLayout({
  activeTab,
  onSelectTab,
  breadcrumbs,
  patientContext,
  children,
}: AppLayoutProps) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const prefersReducedMotion = useReducedMotion();

  return (
    <div className="flex min-h-screen bg-slate-canvas text-slate-text-primary">
      <Sidebar
        activeTab={activeTab}
        onSelectTab={onSelectTab}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        isMobileOpen={isMobileNavOpen}
        onCloseMobile={() => setIsMobileNavOpen(false)}
      />

      <div className="flex min-w-0 flex-1 flex-col overflow-y-auto">
        <Header
          onNavigateTab={onSelectTab}
          onOpenMobileNav={() => setIsMobileNavOpen(true)}
          onSearchSubmit={(query) => {
            const q = query.toLowerCase();
            if (q.includes('who') || q.includes('aware')) onSelectTab('who');
            else if (q.includes('soar') || q.includes('surveillance')) onSelectTab('soar');
            else if (q.includes('armd') || q.includes('ml')) onSelectTab('armd');
            else if (q.includes('patient') || q.includes('history')) onSelectTab('patients');
            else if (q.includes('admin')) onSelectTab('admin');
            else onSelectTab('who');
          }}
        />

        <main className="mx-auto w-full max-w-[1600px] flex-1 space-y-5 p-4 sm:p-6 lg:p-8">
          {breadcrumbs && breadcrumbs.length > 0 && <Breadcrumbs items={breadcrumbs} onNavigate={onSelectTab} />}

          {patientContext && <PatientContextBanner patient={patientContext} />}

          {/* Main View Area — subtle, fast tab-change transition */}
          <div className="w-full">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={prefersReducedMotion ? false : { opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={prefersReducedMotion ? undefined : { opacity: 0, y: -6 }}
                transition={{ duration: 0.18, ease: [0.2, 0.8, 0.2, 1] }}
              >
                {children}
              </motion.div>
            </AnimatePresence>
          </div>
        </main>

        {/* Footer — release identity only; no fabricated telemetry */}
        <footer className="flex h-11 shrink-0 select-none items-center justify-between border-t border-slate-border bg-slate-surface px-4 sm:px-6 text-[10px] font-medium uppercase tracking-tight text-slate-text-muted">
          <div className="flex items-center space-x-6">
            <span>PharmaTrybe CDSS</span>
            <span className="hidden sm:inline">Release: v1.0.7-prod</span>
          </div>
          <div className="text-[10px] normal-case text-slate-text-muted">
            &copy; 2026 PharmaTrybe Clinical Decision Support System
          </div>
        </footer>
      </div>
    </div>
  );
}

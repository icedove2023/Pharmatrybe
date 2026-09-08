import React, { useState } from 'react';
import {
  Sun, Moon, LogOut, ChevronDown,
  User as UserIcon, Menu, ShieldQuestion,
} from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { useSettingsStore } from '@/stores/settingsStore';
import { RoleBadge } from '@/components/auth/RoleBadge';
import { UserSessionModal } from '@/components/auth/UserSessionModal';
import { cn } from '@/lib/utils';
import { NotificationCenter } from './NotificationCenter';

interface HeaderProps {
  onSearchSubmit?: (query: string) => void;
  onNavigateTab?: (tab: string) => void;
  onOpenMobileNav?: () => void;
}

export function Header({ onSearchSubmit, onNavigateTab, onOpenMobileNav }: HeaderProps) {
  const { user, logout } = useAuthStore();
  const { settings, updateSettings } = useSettingsStore();
  const [showRoleMenu, setShowRoleMenu] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  const toggleTheme = () => {
    const nextTheme = settings.theme === 'dark' ? 'light' : 'dark';
    updateSettings({ theme: nextTheme });
  };

  return (
    <>
      <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-border bg-slate-surface/90 px-4 backdrop-blur-md supports-[backdrop-filter]:bg-slate-surface/75 sm:px-6">
        {/* Left: Mobile Menu */}
        <div className="flex items-center space-x-3">
          {onOpenMobileNav && (
            <button
              onClick={onOpenMobileNav}
              title="Open navigation menu"
              className="focus-clinical rounded-[var(--radius-sm)] p-2 text-slate-text-secondary hover:bg-slate-inset-hover lg:hidden"
            >
              <Menu className="h-5 w-5" aria-hidden="true" />
            </button>
          )}

        </div>

        {/* Right: Actions & Identity */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          <button
            onClick={toggleTheme}
            title={`Switch to ${settings.theme === 'dark' ? 'light' : 'dark'} mode`}
            className="focus-clinical rounded-[var(--radius-sm)] p-2 text-slate-text-secondary transition-colors duration-[var(--duration-fast)] hover:bg-slate-inset-hover hover:text-slate-text-primary"
          >
            {settings.theme === 'dark' ? (
              <Sun className="h-4 w-4 text-[var(--color-safety-warning)]" aria-hidden="true" />
            ) : (
              <Moon className="h-4 w-4" aria-hidden="true" />
            )}
          </button>

          <NotificationCenter />

          {/* User Account & Role */}
          {user && (
            <div className="relative">
              <button
                onClick={() => setShowRoleMenu(!showRoleMenu)}
                className="focus-clinical flex items-center space-x-2 rounded-[var(--radius-lg)] border border-slate-border p-1.5 transition-colors duration-[var(--duration-fast)] hover:border-[var(--color-clinical-300)] hover:bg-slate-inset-hover"
                aria-expanded={showRoleMenu}
              >
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-clinical-700)] text-xs font-bold text-white">
                  {user.name.split(' ').map((n) => n[0]).join('')}
                </div>
                <div className="hidden pr-1 text-left sm:block">
                  <p className="max-w-[120px] truncate text-xs font-semibold leading-tight text-slate-text-primary">{user.name}</p>
                  <RoleBadge role={user.role} size="sm" showIcon={false} />
                </div>
                <ChevronDown className="h-3.5 w-3.5 shrink-0 text-slate-text-muted" aria-hidden="true" />
              </button>

              {showRoleMenu && (
                <div className="absolute right-0 z-50 mt-2 w-72 origin-top-right animate-fade-in space-y-1 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface-raised p-2.5 shadow-clinical-lg">
                  <div className="mb-1 border-b border-slate-border-subtle px-3 py-2">
                    <div className="flex items-center justify-between">
                      <p className="text-xs font-semibold text-slate-text-primary">{user.name}</p>
                      <RoleBadge role={user.role} size="sm" />
                    </div>
                    <p className="truncate text-[11px] text-slate-text-muted">{user.email}</p>
                    <p className="mt-0.5 text-[10px] text-slate-text-muted">{user.organization}</p>
                  </div>

                  <button
                    onClick={() => {
                      setShowRoleMenu(false);
                      onNavigateTab?.('profile');
                    }}
                    className="focus-clinical flex w-full items-center space-x-2 rounded-[var(--radius-sm)] px-3 py-2 text-left text-xs font-medium text-slate-text-secondary hover:bg-slate-inset-hover"
                  >
                    <UserIcon className="h-3.5 w-3.5 text-[var(--color-clinical-400)]" aria-hidden="true" />
                    <span>My profile</span>
                  </button>
                  <button
                    onClick={() => {
                      setShowRoleMenu(false);
                      setShowProfileModal(true);
                    }}
                    className="focus-clinical flex w-full items-center space-x-2 rounded-[var(--radius-sm)] px-3 py-2 text-left text-xs font-medium text-slate-text-secondary hover:bg-slate-inset-hover"
                  >
                    <ShieldQuestion className="h-3.5 w-3.5 text-[var(--color-clinical-400)]" aria-hidden="true" />
                    <span>Quick view: session & permissions</span>
                  </button>

                  <div className="border-t border-slate-border-subtle pt-1">
                    <button
                      onClick={() => {
                        onNavigateTab?.('settings');
                      }}
                      className="focus-clinical w-full rounded-[var(--radius-sm)] px-3 py-2 text-left text-xs font-medium text-slate-text-secondary hover:bg-slate-inset-hover"
                    >
                      User & dosing preferences
                    </button>
                    <button
                      onClick={() => {
                        logout();
                      }}
                      className="focus-clinical flex w-full items-center rounded-[var(--radius-sm)] px-3 py-2 text-left text-xs font-semibold text-[var(--color-safety-critical)] hover:bg-[var(--color-safety-critical-bg)]"
                    >
                      <LogOut className="mr-2 h-3.5 w-3.5" aria-hidden="true" />
                      Sign out
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </header>

      <UserSessionModal isOpen={showProfileModal} onClose={() => setShowProfileModal(false)} />
    </>
  );
}

import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'motion/react';
import {
  Settings, Sun, Moon, Monitor, Sliders, Save, CheckCircle2, UserCircle,
} from 'lucide-react';
import { useSettingsStore } from '@/stores/settingsStore';
import { useAuthStore } from '@/stores/authStore';
import { RoleBadge } from '@/components/auth/RoleBadge';
import { ClinicalButton } from '@/components/ui/ClinicalButton';
import { cn } from '@/lib/utils';

export function SettingsView() {
  const { settings, updateSettings, loadSettings } = useSettingsStore();
  const { user } = useAuthStore();
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const prefersReducedMotion = useReducedMotion();

  useEffect(() => {
    loadSettings();
  }, []);

  const handleSave = async () => {
    setToastMsg('Preferences saved');
    setTimeout(() => setToastMsg(null), 2500);
  };

  const themeOptions: { key: 'light' | 'dark' | 'system'; label: string; icon: React.ElementType }[] = [
    { key: 'light', label: 'Light theme', icon: Sun },
    { key: 'dark', label: 'Dark theme', icon: Moon },
    { key: 'system', label: 'System default', icon: Monitor },
  ];

  return (
    <div className="relative mx-auto max-w-4xl space-y-6">
      {/* Toast Notification */}
      <AnimatePresence>
        {toastMsg && (
          <motion.div
            initial={prefersReducedMotion ? { opacity: 0 } : { opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.18 }}
            className="fixed bottom-6 right-6 z-50 flex items-center space-x-2 rounded-[var(--radius-md)] border border-slate-border bg-slate-surface-raised px-4 py-3 text-xs font-semibold text-slate-text-primary shadow-2xl"
          >
            <CheckCircle2 className="h-4 w-4 text-[var(--color-safety-success)]" aria-hidden="true" />
            <span>{toastMsg}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <div className="flex flex-col justify-between gap-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6 md:flex-row md:items-center">
        <div>
          <div className="mb-1 inline-flex items-center space-x-1.5 rounded-full bg-[var(--color-clinical-950)] px-2.5 py-0.5 text-xs font-semibold text-[var(--color-clinical-300)]">
            <Settings className="h-3.5 w-3.5" aria-hidden="true" />
            <span>Clinical system & user preferences</span>
          </div>
          <h2 className="text-xl font-bold text-slate-text-primary">Settings</h2>
          <p className="text-xs text-slate-text-muted">
            Appearance, clinical dosing defaults, AWaRe restriction strictness, and notifications.
          </p>
        </div>

        <ClinicalButton variant="primary" size="md" icon={Save} onClick={handleSave} className="shrink-0">
          Save preferences
        </ClinicalButton>
      </div>

      {/* 1. Theme & Appearance Section */}
      <div className="space-y-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6">
        <h3 className="flex items-center text-sm font-semibold text-slate-text-primary">
          <Sun className="mr-2 h-4 w-4 text-[var(--color-safety-warning)]" aria-hidden="true" />
          Appearance & visual theme
        </h3>

        <div className="grid grid-cols-3 gap-4 text-xs">
          {themeOptions.map((opt) => {
            const Icon = opt.icon;
            const isActive = settings.theme === opt.key;
            return (
              <button
                key={opt.key}
                onClick={() => updateSettings({ theme: opt.key })}
                aria-pressed={isActive}
                className={cn(
                  'flex flex-col items-center justify-center space-y-2 rounded-[var(--radius-md)] border p-4 text-center transition-colors duration-[var(--duration-fast)] focus-clinical',
                  isActive
                    ? 'border-[var(--color-clinical-500)] bg-[var(--color-clinical-950)] font-semibold text-[var(--color-clinical-300)] ring-1 ring-[var(--color-clinical-500)]'
                    : 'border-slate-border-subtle bg-slate-inset text-slate-text-secondary hover:border-slate-border',
                )}
              >
                <Icon className={cn('h-6 w-6', isActive ? 'text-[var(--color-clinical-400)]' : 'text-slate-text-muted')} aria-hidden="true" />
                <span>{opt.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Clinical Prescribing Controls */}
      <div className="space-y-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6">
        <h3 className="flex items-center text-sm font-semibold text-slate-text-primary">
          <Sliders className="mr-2 h-4 w-4 text-[var(--color-clinical-400)]" aria-hidden="true" />
          Clinical decision engine parameters
        </h3>

        <div className="space-y-4 text-xs">
          {/* Default Dosing Units */}
          <div className="flex items-center justify-between rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3.5">
            <div>
              <p className="font-semibold text-slate-text-primary">Default dosing display unit</p>
              <p className="text-slate-text-muted">Standard unit for drug mass in recommendations</p>
            </div>
            <select
              value={settings.defaultDosingUnit}
              onChange={(e) => updateSettings({ defaultDosingUnit: e.target.value as any })}
              className="focus-clinical rounded-[var(--radius-sm)] border border-slate-border-subtle bg-slate-canvas px-3 py-1.5 font-semibold text-slate-text-primary"
            >
              <option value="mg">Milligrams (mg)</option>
              <option value="g">Grams (g)</option>
              <option value="mg/kg">mg/kg (weight-based)</option>
            </select>
          </div>

          {/* AWaRe Strict Mode */}
          <div className="flex items-center justify-between rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-3.5">
            <div>
              <p className="font-semibold text-slate-text-primary">WHO AWaRe strict mode</p>
              <p className="text-slate-text-muted">Require justification before selecting Watch or Reserve antibiotics</p>
            </div>
            <label className="relative inline-flex cursor-pointer items-center">
              <input
                type="checkbox"
                checked={settings.awareStrictMode}
                onChange={(e) => updateSettings({ awareStrictMode: e.target.checked })}
                className="peer sr-only"
              />
              <div className="peer h-6 w-11 rounded-full bg-slate-border after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-slate-border after:bg-white after:transition-all after:content-[''] peer-checked:bg-[var(--color-clinical-600)] peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus-visible:outline peer-focus-visible:outline-2 peer-focus-visible:outline-[var(--color-clinical-400)]" />
            </label>
          </div>

          {/* High Risk Threshold */}
          <div className="space-y-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-4">
            <div className="flex items-center justify-between">
              <p className="font-semibold text-slate-text-primary">Resistance alert confidence threshold</p>
              <span className="num-clinical font-semibold text-[var(--color-clinical-400)]">{settings.highRiskAlertThreshold}% confidence</span>
            </div>
            <input
              type="range"
              min="50"
              max="95"
              value={settings.highRiskAlertThreshold}
              onChange={(e) => updateSettings({ highRiskAlertThreshold: Number(e.target.value) })}
              className="w-full accent-[var(--color-clinical-500)]"
            />
            <p className="text-[11px] text-slate-text-muted">
              Triggers stewardship warnings when AI resistance confidence exceeds this threshold.
            </p>
          </div>
        </div>
      </div>

      {/* 3. User Profile Summary */}
      {user && (
        <div className="space-y-3 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6 text-xs">
          <h3 className="flex items-center text-sm font-semibold text-slate-text-primary">
            <UserCircle className="mr-2 h-4 w-4 text-[var(--color-clinical-400)]" aria-hidden="true" />
            Authenticated session
          </h3>

          <div className="grid grid-cols-2 gap-4 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset p-4">
            <div>
              <p className="text-slate-text-muted">Name</p>
              <p className="font-semibold text-slate-text-primary">{user.name}</p>
            </div>
            <div>
              <p className="text-slate-text-muted">Email</p>
              <p className="num-clinical font-semibold text-slate-text-primary">{user.email}</p>
            </div>
            <div>
              <p className="text-slate-text-muted">Role</p>
              <RoleBadge role={user.role} size="sm" />
            </div>
            <div>
              <p className="text-slate-text-muted">Organization</p>
              <p className="font-semibold text-slate-text-primary">{user.organization}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

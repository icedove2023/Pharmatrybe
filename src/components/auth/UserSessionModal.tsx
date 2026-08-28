import React from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'motion/react';
import { useAuthStore } from '@/stores/authStore';
import { RoleBadge } from './RoleBadge';
import { X, User, Shield, Check, Ban, Clock, LogOut, Building } from 'lucide-react';
import { ClinicalButton } from '@/components/ui/ClinicalButton';
import { cn } from '@/lib/utils';

interface UserSessionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function UserSessionModal({ isOpen, onClose }: UserSessionModalProps) {
  const { user, session, logout } = useAuthStore();
  const prefersReducedMotion = useReducedMotion();

  const permissionsList: Array<{ key: keyof NonNullable<typeof user>['permissions']; label: string }> = [
    { key: 'canSubmitAssessment', label: 'Submit clinical case assessments' },
    { key: 'canViewRecommendations', label: 'View multi-source recommendations' },
    { key: 'canSignPrescription', label: 'Sign e-prescription orders' },
    { key: 'canOverrideStewardship', label: 'Execute stewardship overrides' },
    { key: 'canViewExplainability', label: 'Deep-dive explainability & SHAP values' },
    { key: 'canAccessKnowledgeExplorer', label: 'Access WHO & surveillance catalogs' },
    { key: 'canViewPatientDirectory', label: 'Access longitudinal patient directory' },
    { key: 'canManagePlugins', label: 'Manage registered prediction & knowledge plugins' },
    { key: 'canViewSystemHealth', label: 'Monitor microservice SLA telemetry' },
    { key: 'canManageUsers', label: 'Manage RBAC user directory' },
    { key: 'canViewAuditLogs', label: 'Inspect platform-wide audit logs' },
  ];

  return (
    <AnimatePresence>
      {isOpen && user && (
        <motion.div
          role="dialog"
          aria-modal="true"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs"
          onClick={onClose}
        >
          <motion.div
            initial={prefersReducedMotion ? false : { opacity: 0, scale: 0.97, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={prefersReducedMotion ? undefined : { opacity: 0, scale: 0.97, y: 8 }}
            transition={{ duration: 0.18, ease: [0.2, 0.8, 0.2, 1] }}
            onClick={(e) => e.stopPropagation()}
            className="max-h-[90vh] w-full max-w-lg space-y-6 overflow-y-auto rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6 shadow-2xl"
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-slate-border pb-4">
              <div className="flex items-center space-x-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-clinical-950)] font-semibold text-[var(--color-clinical-300)]">
                  <User className="h-5 w-5" aria-hidden="true" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-slate-text-primary">Clinician profile & session</h3>
                  <p className="text-[11px] text-slate-text-muted">Verified identity & role-based access control</p>
                </div>
              </div>
              <button
                onClick={onClose}
                aria-label="Close profile panel"
                className="focus-clinical rounded-[var(--radius-sm)] p-2 text-slate-text-muted hover:bg-slate-inset-hover hover:text-slate-text-primary"
              >
                <X className="h-5 w-5" aria-hidden="true" />
              </button>
            </div>

            {/* User Identity Card */}
            <div className="space-y-3 rounded-[var(--radius-lg)] border border-slate-border-subtle bg-slate-inset p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-semibold text-slate-text-primary">{user.name}</h4>
                  <p className="num-clinical text-xs text-slate-text-muted">{user.email}</p>
                </div>
                <RoleBadge role={user.role} />
              </div>

              <div className="grid grid-cols-2 gap-2 border-t border-slate-border-subtle pt-2 text-xs">
                <div>
                  <span className="block text-[10px] font-semibold uppercase text-slate-text-muted">Organization</span>
                  <span className="flex items-center truncate font-semibold text-slate-text-primary">
                    <Building className="mr-1 h-3 w-3 shrink-0 text-slate-text-muted" aria-hidden="true" />
                    {user.organization}
                  </span>
                </div>
                <div>
                  <span className="block text-[10px] font-semibold uppercase text-slate-text-muted">Department</span>
                  <span className="truncate font-semibold text-slate-text-primary">{user.department}</span>
                </div>
                {user.licenseNumber && (
                  <div>
                    <span className="block text-[10px] font-semibold uppercase text-slate-text-muted">Clinical license</span>
                    <span className="num-clinical text-slate-text-secondary">{user.licenseNumber}</span>
                  </div>
                )}
                <div>
                  <span className="block text-[10px] font-semibold uppercase text-slate-text-muted">Last active</span>
                  <span className="num-clinical text-slate-text-secondary">{user.lastLogin || 'Active now'}</span>
                </div>
              </div>
            </div>

            {/* Permissions Matrix */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="flex items-center text-xs font-semibold uppercase tracking-wide text-slate-text-muted">
                  <Shield className="mr-1.5 h-3.5 w-3.5 text-[var(--color-clinical-400)]" aria-hidden="true" />
                  Role permissions matrix
                </h4>
                <span className="text-[10px] text-slate-text-muted">Enforced server-side</span>
              </div>

              <div className="max-h-48 space-y-1.5 overflow-y-auto rounded-[var(--radius-lg)] border border-slate-border-subtle bg-slate-canvas p-3 text-xs">
                {permissionsList.map(({ key, label }) => {
                  const isAllowed = !!user.permissions[key];
                  return (
                    <div key={key} className="flex items-center justify-between rounded-[var(--radius-sm)] px-2 py-1 hover:bg-slate-inset-hover">
                      <span className="text-[11px] text-slate-text-secondary">{label}</span>
                      {isAllowed ? (
                        <span className="inline-flex items-center space-x-1 text-[10px] font-semibold text-[var(--color-safety-success)]">
                          <Check className="h-3.5 w-3.5" aria-hidden="true" />
                          <span>Allowed</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1 text-[10px] font-semibold text-slate-text-muted">
                          <Ban className="h-3 w-3" aria-hidden="true" />
                          <span>Restricted</span>
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Safe session context */}
            {session && (
              <div className="space-y-1 rounded-[var(--radius-lg)] border border-slate-border-subtle bg-slate-inset p-3 text-[11px] text-slate-text-muted">
                <div className="num-clinical flex items-center justify-between text-[10px]">
                  <span className="flex items-center space-x-1">
                    <Clock className="h-3 w-3" aria-hidden="true" />
                    <span>Authenticated session active until {new Date(session.expiresAt).toLocaleTimeString()}</span>
                  </span>
                </div>
                <p className="num-clinical text-[10px]">
                  Distributed trace ID: <span className="text-[var(--color-clinical-400)]">{session.traceSessionId}</span>
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center justify-between border-t border-slate-border pt-4">
              <ClinicalButton
                variant="destructive"
                size="sm"
                icon={LogOut}
                onClick={() => {
                  logout();
                  onClose();
                }}
              >
                Sign out
              </ClinicalButton>
              <ClinicalButton variant="primary" size="sm" onClick={onClose}>
                Done
              </ClinicalButton>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

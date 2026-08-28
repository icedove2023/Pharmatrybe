import React from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { useAuthStore } from '@/stores/authStore';
import { UserRole, BackendPermissionCode } from '@/types/auth';
import { RoleBadge } from './RoleBadge';
import { ShieldAlert, ArrowLeft, RefreshCw, Lock } from 'lucide-react';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { ClinicalButton } from '@/components/ui/ClinicalButton';

interface AuthGuardProps {
  children: React.ReactNode;
  requiredRole?: UserRole | UserRole[];
  requiredPermission?: BackendPermissionCode;
  fallbackRoute?: string;
  onNavigate?: (route: string) => void;
}

export function AuthGuard({
  children,
  requiredRole,
  requiredPermission,
  fallbackRoute = 'dashboard',
  onNavigate,
}: AuthGuardProps) {
  const { user, status, can } = useAuthStore();
  const prefersReducedMotion = useReducedMotion();

  if (status === 'loading') {
    return (
      <div className="flex min-h-[400px] items-center justify-center p-12">
        <div className="flex flex-col items-center space-y-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-[var(--color-clinical-500)] border-t-transparent" />
          <p className="text-xs font-semibold text-slate-text-muted">Checking RBAC credentials…</p>
        </div>
      </div>
    );
  }

  if (status !== 'authenticated' || !user) {
    return (
      <div className="mx-auto max-w-lg space-y-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-8 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-[var(--radius-lg)] bg-[var(--color-safety-warning-bg)] text-[var(--color-safety-warning)]">
          <Lock className="h-6 w-6" aria-hidden="true" />
        </div>
        <h3 className="text-lg font-semibold text-slate-text-primary">Authentication required</h3>
        <p className="text-xs leading-relaxed text-slate-text-muted">
          You must be signed in with a verified clinical or governance identity to access this section.
        </p>
      </div>
    );
  }

  let isRoleAuthorized = true;
  if (requiredRole) {
    const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
    isRoleAuthorized = roles.includes(user.role);
  }

  let isPermissionAuthorized = true;
  if (requiredPermission) {
    isPermissionAuthorized = can(requiredPermission);
  }

  if (!isRoleAuthorized || !isPermissionAuthorized) {
    return (
      <motion.div
        initial={prefersReducedMotion ? false : { opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        className="mx-auto max-w-2xl space-y-6 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-8"
      >
        <div className="flex items-start space-x-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-[var(--radius-lg)] bg-[var(--color-safety-critical-bg)] text-[var(--color-safety-critical)]">
            <ShieldAlert className="h-6 w-6" aria-hidden="true" />
          </div>
          <div className="space-y-1">
            <h3 className="text-lg font-semibold text-slate-text-primary">Access restricted — role-based policy (RBAC)</h3>
            <p className="text-xs leading-relaxed text-slate-text-muted">
              Your active account role does not have authorization to access this module under clinical
              governance protocols.
            </p>
          </div>
        </div>

        {/* Current Role Details Card */}
        <div className="space-y-3 rounded-[var(--radius-lg)] border border-slate-border-subtle bg-slate-inset p-4 text-xs">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-slate-text-muted">Active session identity:</span>
            <RoleBadge role={user.role} />
          </div>
          <div className="flex items-center justify-between text-slate-text-secondary">
            <span>Clinician / user:</span>
            <span className="font-semibold text-slate-text-primary">{user.name}</span>
          </div>
          <div className="flex items-center justify-between text-slate-text-secondary">
            <span>Required role(s):</span>
            <span className="num-clinical font-semibold text-[var(--color-clinical-400)]">
              {Array.isArray(requiredRole) ? requiredRole.join(' OR ') : requiredRole || 'Elevated privilege'}
            </span>
          </div>
        </div>

        {onNavigate && (
          <div className="flex justify-end">
            <ClinicalButton variant="primary" icon={ArrowLeft} onClick={() => onNavigate(fallbackRoute)}>
              Return to dashboard
            </ClinicalButton>
          </div>
        )}
      </motion.div>
    );
  }

  return <>{children}</>;
}

import React, { useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import {
  Users, Search, Filter, UserPlus, Shield, CheckCircle2, XCircle,
  Clock, Briefcase, Award, Key, X, AlertCircle, Info, ShieldCheck, ShieldOff, Copy, Check,
} from 'lucide-react';
import { AdminUser, UserRole } from '@/types';
import { ROLE_PERMISSIONS_MAP } from '@/types/auth';
import { RoleBadge } from '@/components/auth/RoleBadge';
import { useAuthStore } from '@/stores/authStore';
import { ProvenanceBadge } from '@/components/common/ProvenanceBadge';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { ClinicalButton } from '@/components/ui/ClinicalButton';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { cn } from '@/lib/utils';

interface UserDirectoryPanelProps {
  users: AdminUser[];
  onToggleStatus: (userId: string, currentStatus: 'Active' | 'Inactive') => Promise<void>;
  onAddUser: (userData: Omit<AdminUser, 'id' | 'lastLogin' | 'assessmentsCount'>) => Promise<{ tempPassword?: string } | void>;
  onUpdateRole: (userId: string, newRole: UserRole) => Promise<void>;
  isLoading?: boolean;
}

const ALL_ROLES: UserRole[] = [
  'Infectious Disease Specialist',
  'General Practitioner',
  'Pharmacist',
  'Admin',
  'Researcher',
];

export function UserDirectoryPanel({
  users,
  onToggleStatus,
  onAddUser,
  onUpdateRole,
  isLoading = false,
}: UserDirectoryPanelProps) {
  const { user: currentUser } = useAuthStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  const [selectedUserForPerms, setSelectedUserForPerms] = useState<AdminUser | null>(null);
  const [isAddUserOpen, setIsAddUserOpen] = useState(false);
  const [actionInProgress, setActionInProgress] = useState<string | null>(null);
  const [roleChangeTarget, setRoleChangeTarget] = useState<AdminUser | null>(null);
  const [roleError, setRoleError] = useState<string | null>(null);
  const [createdCredentials, setCreatedCredentials] = useState<{ email: string; tempPassword: string } | null>(null);
  const [copied, setCopied] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: 'General Practitioner' as UserRole,
    department: 'Primary Care Medicine',
    licenseNumber: '',
    status: 'Active' as 'Active' | 'Inactive',
  });
  const [formError, setFormError] = useState<string | null>(null);

  const filteredUsers = users.filter((u) => {
    const matchesSearch =
      u.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (u.department && u.department.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (u.licenseNumber && u.licenseNumber.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesRole = roleFilter === 'ALL' || u.role === roleFilter;
    const matchesStatus = statusFilter === 'ALL' || u.status === statusFilter;

    return matchesSearch && matchesRole && matchesStatus;
  });

  const activeAdminCount = users.filter((u) => u.role === 'Admin' && u.status === 'Active').length;

  const handleStatusToggle = async (u: AdminUser) => {
    if (u.id === currentUser?.id) return;
    try {
      setActionInProgress(u.id);
      await onToggleStatus(u.id, u.status);
    } catch (err: any) {
      setRoleError(err.message || 'Failed to update user status');
    } finally {
      setActionInProgress(null);
    }
  };

  const confirmRoleChange = async () => {
    if (!roleChangeTarget) return;
    const nextRole: UserRole = roleChangeTarget.role === 'Admin' ? 'Infectious Disease Specialist' : 'Admin';
    try {
      setActionInProgress(roleChangeTarget.id);
      setRoleError(null);
      await onUpdateRole(roleChangeTarget.id, nextRole);
      setRoleChangeTarget(null);
    } catch (err: any) {
      setRoleError(err.message || 'Failed to update role.');
    } finally {
      setActionInProgress(null);
    }
  };

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    if (!formData.name.trim() || !formData.email.trim()) {
      setFormError('Please enter a valid full name and email address.');
      return;
    }
    if (!formData.email.includes('@')) {
      setFormError('Please provide a valid corporate or hospital email.');
      return;
    }

    try {
      setActionInProgress('create');
      const result = await onAddUser({
        name: formData.name.trim(),
        email: formData.email.trim().toLowerCase(),
        role: formData.role,
        department: formData.department.trim(),
        licenseNumber: formData.licenseNumber.trim() || undefined,
        status: formData.status,
      });
      setIsAddUserOpen(false);
      if (result && 'tempPassword' in result && result.tempPassword) {
        setCreatedCredentials({ email: formData.email.trim().toLowerCase(), tempPassword: result.tempPassword });
      }
      setFormData({ name: '', email: '', role: 'General Practitioner', department: 'Primary Care Medicine', licenseNumber: '', status: 'Active' });
    } catch (err: any) {
      setFormError(err.message || 'Failed to create user account.');
    } finally {
      setActionInProgress(null);
    }
  };

  return (
    <div className="space-y-6" id="admin-user-directory">
      {/* Header and Action Bar */}
      <div className="space-y-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-4 sm:p-5">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="flex items-center gap-2 text-sm font-semibold text-slate-text-primary">
                <Users className="h-4 w-4 text-[var(--color-clinical-400)]" aria-hidden="true" />
                Staff directory & role management
              </h3>
              <ProvenanceBadge provenance="demo_fixture" customLabel="Demo directory" />
            </div>
            <p className="mt-0.5 text-xs text-slate-text-muted">
              Provision employee accounts, manage roles, and grant or revoke administrator access.
            </p>
          </div>

          <ClinicalButton variant="primary" size="md" icon={UserPlus} onClick={() => setIsAddUserOpen(true)}>
            Add employee
          </ClinicalButton>
        </div>

        {roleError && <SafetyAlert level="warning" title="Action failed">{roleError}</SafetyAlert>}

        {createdCredentials && (
          <SafetyAlert
            level="success"
            title="Account created — share these credentials securely"
            actions={
              <ClinicalButton
                variant="outline"
                size="sm"
                icon={copied ? Check : Copy}
                onClick={() => {
                  navigator.clipboard.writeText(`${createdCredentials.email} / ${createdCredentials.tempPassword}`);
                  setCopied(true);
                  setTimeout(() => setCopied(false), 2000);
                }}
              >
                {copied ? 'Copied' : 'Copy credentials'}
              </ClinicalButton>
            }
          >
            <p className="num-clinical">
              {createdCredentials.email} / <strong>{createdCredentials.tempPassword}</strong>
            </p>
            <p className="mt-1 text-[11px] opacity-80">
              This is a demo-only temporary password. A real backend would email an invite link instead of
              displaying a password in the UI.
            </p>
          </SafetyAlert>
        )}

        {/* Search & Filter Toolbar */}
        <div className="grid grid-cols-1 gap-3 border-t border-slate-border-subtle pt-3 sm:grid-cols-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-text-muted" aria-hidden="true" />
            <input
              type="text"
              placeholder="Search by name, email, department…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="focus-clinical w-full rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset py-2 pl-9 pr-3 text-xs text-slate-text-primary placeholder-slate-text-muted"
            />
          </div>

          <div className="flex items-center space-x-2">
            <Filter className="h-3.5 w-3.5 shrink-0 text-slate-text-muted" aria-hidden="true" />
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="focus-clinical w-full rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset px-3 py-2 text-xs text-slate-text-primary"
            >
              <option value="ALL">All roles ({users.length})</option>
              {ALL_ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="focus-clinical w-full rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset px-3 py-2 text-xs text-slate-text-primary"
          >
            <option value="ALL">All account statuses</option>
            <option value="Active">Active only</option>
            <option value="Inactive">Inactive only</option>
          </select>
        </div>
      </div>

      {/* Users Table */}
      <div className="overflow-hidden rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-xs">
            <thead>
              <tr className="border-b border-slate-border bg-slate-inset text-[10px] font-semibold uppercase tracking-wide text-slate-text-muted">
                <th className="px-4 py-3">Identity</th>
                <th className="px-4 py-3">Role & privileges</th>
                <th className="px-4 py-3">Department</th>
                <th className="px-4 py-3">Last activity</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Access controls</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-border-subtle">
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-xs text-slate-text-muted">
                    No accounts match the specified search or filter criteria.
                  </td>
                </tr>
              ) : (
                filteredUsers.map((u) => {
                  const isCurrent = u.id === currentUser?.id;
                  const isUpdating = actionInProgress === u.id;
                  const isLastAdmin = u.role === 'Admin' && activeAdminCount <= 1;

                  return (
                    <tr key={u.id} className="transition-colors duration-[var(--duration-fast)] hover:bg-slate-inset-hover">
                      <td className="px-4 py-3.5">
                        <div className="flex items-center space-x-3">
                          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[var(--color-clinical-700)] bg-[var(--color-clinical-950)] text-xs font-semibold text-[var(--color-clinical-300)]">
                            {u.name.split(' ').map((n) => n[0]).slice(0, 2).join('')}
                          </div>
                          <div>
                            <div className="flex items-center space-x-1.5">
                              <span className="font-semibold text-slate-text-primary">{u.name}</span>
                              {isCurrent && <StatusBadge tone="clinical">You</StatusBadge>}
                            </div>
                            <span className="num-clinical block text-[11px] text-slate-text-muted">{u.email}</span>
                            {u.licenseNumber && (
                              <span className="mt-0.5 flex items-center gap-1 text-[10px] text-slate-text-muted">
                                <Award className="h-2.5 w-2.5 text-[var(--color-clinical-400)]" aria-hidden="true" />
                                {u.licenseNumber}
                              </span>
                            )}
                          </div>
                        </div>
                      </td>

                      <td className="px-4 py-3.5">
                        <div className="space-y-1">
                          <RoleBadge role={u.role} size="sm" />
                          <button
                            onClick={() => setSelectedUserForPerms(u)}
                            className="focus-clinical flex items-center gap-1 text-[10px] font-medium text-[var(--color-clinical-400)] hover:underline"
                          >
                            <Key className="h-2.5 w-2.5" aria-hidden="true" />
                            View RBAC matrix
                          </button>
                        </div>
                      </td>

                      <td className="px-4 py-3.5 text-slate-text-secondary">
                        <div className="flex items-center space-x-1.5">
                          <Briefcase className="h-3.5 w-3.5 shrink-0 text-slate-text-muted" aria-hidden="true" />
                          <span className="max-w-[200px] truncate">{u.department}</span>
                        </div>
                      </td>

                      <td className="num-clinical px-4 py-3.5 text-[11px] text-slate-text-muted">
                        <div className="flex items-center space-x-1">
                          <Clock className="h-3 w-3 text-slate-text-muted" aria-hidden="true" />
                          <span>{u.lastLogin}</span>
                        </div>
                        {u.assessmentsCount !== undefined && (
                          <span className="mt-0.5 block text-[10px] text-slate-text-muted">{u.assessmentsCount} reviews logged</span>
                        )}
                      </td>

                      <td className="px-4 py-3.5">
                        <StatusBadge tone={u.status === 'Active' ? 'success' : 'neutral'}>{u.status}</StatusBadge>
                      </td>

                      <td className="px-4 py-3.5">
                        <div className="flex items-center justify-end space-x-1.5">
                          <button
                            onClick={() => setRoleChangeTarget(u)}
                            disabled={isUpdating || (isCurrent && u.role === 'Admin') || (u.role === 'Admin' && isLastAdmin)}
                            title={
                              isCurrent && u.role === 'Admin'
                                ? 'Cannot revoke your own admin access'
                                : u.role === 'Admin' && isLastAdmin
                                ? 'Cannot revoke the last active administrator'
                                : u.role === 'Admin'
                                ? 'Revoke administrator access'
                                : 'Grant administrator access'
                            }
                            className={cn(
                              'focus-clinical rounded-[var(--radius-sm)] border px-2.5 py-1.5 text-[11px] font-semibold transition-colors duration-[var(--duration-fast)] disabled:cursor-not-allowed disabled:opacity-40',
                              u.role === 'Admin'
                                ? 'border-[var(--color-safety-warning-border)] bg-[var(--color-safety-warning-bg)] text-[var(--color-safety-warning)] hover:brightness-110'
                                : 'border-[var(--color-clinical-700)] bg-[var(--color-clinical-950)] text-[var(--color-clinical-300)] hover:brightness-110',
                            )}
                          >
                            {u.role === 'Admin' ? <ShieldOff className="h-3 w-3" aria-hidden="true" /> : <ShieldCheck className="h-3 w-3" aria-hidden="true" />}
                          </button>

                          <button
                            onClick={() => handleStatusToggle(u)}
                            disabled={isUpdating || isCurrent || (u.role === 'Admin' && u.status === 'Active' && isLastAdmin)}
                            title={isCurrent ? 'Cannot deactivate your own active session' : u.status === 'Active' ? 'Deactivate account' : 'Reactivate account'}
                            className={cn(
                              'focus-clinical rounded-[var(--radius-sm)] border px-3 py-1.5 text-xs font-semibold transition-colors duration-[var(--duration-fast)] disabled:cursor-not-allowed disabled:opacity-40',
                              u.status === 'Active'
                                ? 'border-[var(--color-safety-critical-border)] bg-[var(--color-safety-critical-bg)] text-[var(--color-safety-critical)] hover:brightness-110'
                                : 'border-[var(--color-safety-success-border)] bg-[var(--color-safety-success-bg)] text-[var(--color-safety-success)] hover:brightness-110',
                            )}
                          >
                            {isUpdating ? 'Updating…' : u.status === 'Active' ? 'Deactivate' : 'Reactivate'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Role Change Confirmation Modal */}
      <AnimatePresence>
        {roleChangeTarget && (
          <motion.div
            role="dialog"
            aria-modal="true"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs"
            onClick={() => setRoleChangeTarget(null)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.97, y: 8 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.97, y: 8 }}
              transition={{ duration: 0.18 }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-md space-y-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6 shadow-2xl"
            >
              <SafetyAlert
                level="warning"
                title={roleChangeTarget.role === 'Admin' ? 'Revoke administrator access?' : 'Grant administrator access?'}
              >
                {roleChangeTarget.role === 'Admin' ? (
                  <>
                    <strong>{roleChangeTarget.name}</strong> will lose access to Governance, Plugin & Telemetry
                    management, Audit Logs, and User provisioning. They'll be reassigned to Infectious Disease
                    Specialist.
                  </>
                ) : (
                  <>
                    <strong>{roleChangeTarget.name}</strong> will gain full administrator privileges, including user
                    management, audit log access, and plugin governance. Grant this only to trusted personnel.
                  </>
                )}
              </SafetyAlert>

              <div className="flex justify-end space-x-2">
                <ClinicalButton variant="outline" onClick={() => setRoleChangeTarget(null)}>
                  Cancel
                </ClinicalButton>
                <ClinicalButton
                  variant={roleChangeTarget.role === 'Admin' ? 'destructive' : 'primary'}
                  loading={actionInProgress === roleChangeTarget.id}
                  onClick={confirmRoleChange}
                >
                  {roleChangeTarget.role === 'Admin' ? 'Revoke admin access' : 'Grant admin access'}
                </ClinicalButton>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Permissions Matrix Modal */}
      <AnimatePresence>
        {selectedUserForPerms && (
          <motion.div
            role="dialog"
            aria-modal="true"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs"
            onClick={() => setSelectedUserForPerms(null)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.97, y: 8 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.97, y: 8 }}
              transition={{ duration: 0.18 }}
              onClick={(e) => e.stopPropagation()}
              className="max-h-[85vh] w-full max-w-lg overflow-hidden rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-slate-border bg-slate-inset p-4 sm:p-5">
                <div className="flex items-center space-x-2.5">
                  <div className="rounded-[var(--radius-md)] border border-[var(--color-clinical-700)] bg-[var(--color-clinical-950)] p-2 text-[var(--color-clinical-300)]">
                    <Shield className="h-4 w-4" aria-hidden="true" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-slate-text-primary">RBAC permission vector: {selectedUserForPerms.name}</h4>
                    <p className="text-xs text-slate-text-muted">Presentation permissions for {selectedUserForPerms.role}</p>
                  </div>
                </div>
                <button onClick={() => setSelectedUserForPerms(null)} className="focus-clinical rounded-[var(--radius-sm)] p-1 text-slate-text-muted hover:text-slate-text-primary">
                  <X className="h-5 w-5" aria-hidden="true" />
                </button>
              </div>

              <div className="max-h-[70vh] space-y-4 overflow-y-auto p-5">
                <div className="rounded-[var(--radius-md)] border border-[var(--color-clinical-700)] bg-[var(--color-clinical-950)] p-3 text-xs text-[var(--color-clinical-200)]">
                  <p className="flex items-center gap-1.5 font-semibold">
                    <Info className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                    Frontend presentation guardrails notice
                  </p>
                  <p className="mt-1 text-[11px] leading-relaxed">
                    These permissions define client-side navigation and view visibility. Authoritative security, API
                    authorization, and role claims are strictly verified server-side on every HTTP transaction.
                  </p>
                </div>

                <div className="divide-y divide-slate-border-subtle text-xs">
                  {Object.entries(ROLE_PERMISSIONS_MAP[selectedUserForPerms.role]).map(([key, val]) => (
                    <div key={key} className="flex items-center justify-between py-2.5">
                      <span className="num-clinical text-slate-text-secondary">{key}</span>
                      {val ? (
                        <span className="inline-flex items-center font-semibold text-[var(--color-safety-success)]">
                          <CheckCircle2 className="mr-1 h-3.5 w-3.5" aria-hidden="true" /> Granted
                        </span>
                      ) : (
                        <span className="inline-flex items-center font-medium text-slate-text-muted">
                          <XCircle className="mr-1 h-3.5 w-3.5" aria-hidden="true" /> Denied
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end border-t border-slate-border bg-slate-inset p-4">
                <ClinicalButton variant="secondary" onClick={() => setSelectedUserForPerms(null)}>
                  Close matrix
                </ClinicalButton>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Add User Modal */}
      <AnimatePresence>
        {isAddUserOpen && (
          <motion.div
            role="dialog"
            aria-modal="true"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs"
            onClick={() => setIsAddUserOpen(false)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.97, y: 8 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.97, y: 8 }}
              transition={{ duration: 0.18 }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-md overflow-hidden rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-slate-border bg-slate-inset p-4 sm:p-5">
                <div className="flex items-center space-x-2.5">
                  <div className="rounded-[var(--radius-md)] border border-[var(--color-clinical-700)] bg-[var(--color-clinical-950)] p-2 text-[var(--color-clinical-300)]">
                    <UserPlus className="h-4 w-4" aria-hidden="true" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-slate-text-primary">Add employee account</h4>
                    <p className="text-xs text-slate-text-muted">Provision a new staff identity</p>
                  </div>
                </div>
                <button onClick={() => setIsAddUserOpen(false)} className="focus-clinical rounded-[var(--radius-sm)] p-1 text-slate-text-muted hover:text-slate-text-primary">
                  <X className="h-5 w-5" aria-hidden="true" />
                </button>
              </div>

              <form onSubmit={handleAddSubmit} className="space-y-4 p-5">
                <SafetyAlert level="info" title="Persistence notice">
                  Provisioned accounts are stored in demo fixture state (this browser only). A real backend needs
                  LDAP/SSO integration or a persisted user store — see BACKEND_REQUIREMENTS.md.
                </SafetyAlert>

                {formError && <SafetyAlert level="warning" title="Cannot create account">{formError}</SafetyAlert>}

                <div>
                  <label className="mb-1 block text-xs font-semibold text-slate-text-secondary">
                    Full name & title <span className="text-[var(--color-safety-critical)]">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Dr. Arthur Conan Doyle"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="focus-clinical w-full rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset px-3 py-2 text-xs text-slate-text-primary"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-xs font-semibold text-slate-text-secondary">
                    Email address <span className="text-[var(--color-safety-critical)]">*</span>
                  </label>
                  <input
                    type="email"
                    required
                    placeholder="e.g. adoyle@hospital.org"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="focus-clinical w-full rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset px-3 py-2 text-xs text-slate-text-primary"
                  />
                </div>

                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <div>
                    <label className="mb-1 block text-xs font-semibold text-slate-text-secondary">
                      Role <span className="text-[var(--color-safety-critical)]">*</span>
                    </label>
                    <select
                      value={formData.role}
                      onChange={(e) => setFormData({ ...formData, role: e.target.value as UserRole })}
                      className="focus-clinical w-full rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset px-3 py-2 text-xs text-slate-text-primary"
                    >
                      {ALL_ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
                    </select>
                  </div>

                  <div>
                    <label className="mb-1 block text-xs font-semibold text-slate-text-secondary">Medical license / reg ID</label>
                    <input
                      type="text"
                      placeholder="e.g. GMC-998811"
                      value={formData.licenseNumber}
                      onChange={(e) => setFormData({ ...formData, licenseNumber: e.target.value })}
                      className="focus-clinical w-full rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset px-3 py-2 text-xs text-slate-text-primary"
                    />
                  </div>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-semibold text-slate-text-secondary">Department / unit</label>
                  <input
                    type="text"
                    placeholder="e.g. Acute Medicine / Emergency"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    className="focus-clinical w-full rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset px-3 py-2 text-xs text-slate-text-primary"
                  />
                </div>

                <div className="flex justify-end space-x-2 border-t border-slate-border-subtle pt-4">
                  <ClinicalButton type="button" variant="outline" onClick={() => setIsAddUserOpen(false)}>
                    Cancel
                  </ClinicalButton>
                  <ClinicalButton type="submit" variant="primary" loading={actionInProgress === 'create'}>
                    {actionInProgress === 'create' ? 'Provisioning…' : 'Create account'}
                  </ClinicalButton>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

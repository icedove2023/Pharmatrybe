import {
  AdminDashboardData,
  AdminUser,
  AuditEvent,
  AuditFilterOptions,
  PluginInfo,
  StewardshipPolicy,
  SystemComponent,
} from '@/types';
import { UserRole } from '@/types/auth';

function unavailable<T>(capability: string): Promise<T> {
  return Promise.reject(new Error(`${capability} is not exposed by the backend.`));
}

export const adminApi = {
  getAdminDashboardData: (): Promise<AdminDashboardData> =>
    unavailable('Administration and governance data'),
  getSystemComponents: (): Promise<SystemComponent[]> =>
    unavailable('System health telemetry'),
  getUsers: (): Promise<AdminUser[]> =>
    unavailable('User provisioning'),
  updateUserStatus: (_userId: string, _newStatus: 'Active' | 'Inactive'): Promise<AdminUser> =>
    unavailable('User status mutation'),
  updateUserRole: (_userId: string, _newRole: UserRole): Promise<AdminUser> =>
    unavailable('User role mutation'),
  addUser: (
    _userData: Omit<AdminUser, 'id' | 'lastLogin' | 'assessmentsCount'>,
  ): Promise<AdminUser & { tempPassword: string }> =>
    unavailable('User provisioning'),
  getAuditEvents: (_filters?: AuditFilterOptions): Promise<AuditEvent[]> =>
    unavailable('Audit log retrieval'),
  getStewardshipPolicies: (): Promise<StewardshipPolicy[]> =>
    unavailable('Stewardship policy retrieval'),
  updateStewardshipPolicy: (
    _policyId: string,
    _updates: Partial<StewardshipPolicy>,
  ): Promise<StewardshipPolicy> =>
    unavailable('Stewardship policy mutation'),
  getRegisteredPlugins: (): Promise<PluginInfo[]> =>
    unavailable('Plugin registry'),
};

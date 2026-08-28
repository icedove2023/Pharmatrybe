import { apiRequest } from './client';

export type GovernanceStatus =
  | 'REGISTERED'
  | 'PENDING_VALIDATION'
  | 'SUBMITTED'
  | 'VALIDATING'
  | 'VALIDATED'
  | 'PENDING_APPROVAL'
  | 'APPROVED'
  | 'ACTIVE'
  | 'DISABLED'
  | 'REJECTED'
  | 'REVOKED'
  | 'QUARANTINED';

export interface PluginGovernanceRecord {
  plugin_id: string;
  plugin_name: string;
  plugin_type: 'knowledge' | 'prediction' | string;
  plugin_version: string;
  plugin_origin?: string;
  owner?: string;
  publisher?: string;
  capabilities?: string[];
  status: GovernanceStatus | string;
  validation_state?: string;
  approval_state?: string;
  trust_level?: string;
  hospital_id?: string;
  created_at?: string;
  updated_at?: string;
  audit_events?: Array<{
    action: string;
    details?: Record<string, unknown>;
    created_at: string;
  }>;
}

export interface PluginRegistrationInput {
  plugin_id: string;
  plugin_name: string;
  plugin_type: 'knowledge' | 'prediction';
  plugin_version: string;
  owner: string;
  publisher: string;
  artifact_hash?: string;
  artifact_uri?: string;
  capabilities?: string[];
  configuration?: Record<string, unknown>;
}

export const pluginGovernanceApi = {
  list: async () => (await apiRequest<{ items: PluginGovernanceRecord[] }>('/plugins')).items,
  get: (pluginId: string) => apiRequest<PluginGovernanceRecord>(`/plugins/${encodeURIComponent(pluginId)}`),
  register: (input: PluginRegistrationInput) => apiRequest<PluginGovernanceRecord>('/plugins', {
    method: 'POST',
    body: JSON.stringify(input),
  }),
  upload: (input: {
    pluginId: string;
    pluginName: string;
    pluginType: 'knowledge' | 'prediction';
    pluginVersion: string;
    owner: string;
    publisher: string;
    artifact: File;
  }) => {
    const form = new FormData();
    form.set('plugin_id', input.pluginId);
    form.set('plugin_name', input.pluginName);
    form.set('plugin_type', input.pluginType);
    form.set('plugin_version', input.pluginVersion);
    form.set('owner', input.owner);
    form.set('publisher', input.publisher);
    form.set('artifact', input.artifact);
    return apiRequest<PluginGovernanceRecord>('/plugins/upload', { method: 'POST', body: form });
  },
  action: (pluginId: string, action: 'validate' | 'approve' | 'activate' | 'deactivate' | 'reject' | 'quarantine' | 'revoke') =>
    apiRequest<PluginGovernanceRecord>(`/plugins/${encodeURIComponent(pluginId)}/${action}`, { method: 'POST' }),
};

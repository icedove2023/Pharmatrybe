import { pluginContractRegistry } from './registry';
import type { PluginInputContract } from './types';

export const WHO_SEARCH_CONTRACT: PluginInputContract = {
  pluginId: 'who_knowledge',
  contractId: 'who-search-query',
  contractVersion: '1.0.0',
  schemaVersion: '2020-12',
  displayName: 'WHO knowledge search',
  description: 'Search the WHO knowledge retrieval boundary by exact query text.',
  status: 'approved',
  provenance: {
    owner: 'WHO knowledge plugin',
    source: 'Frozen plugin runtime contract and public WHO search route',
    artifact: 'apps/api/app/plugins/knowledge/who_knowledge_plugin.py; apps/api/app/api/v1/who.py',
    artifactVersion: '1.0.0',
    approvedBy: 'Phase 20D governance decision',
    approvedAt: '2026-09-06T00:00:00Z',
  },
  inputSchema: {
    $schema: 'https://json-schema.org/draft/2020-12/schema',
    type: 'object',
    properties: {
      query_text: { type: 'string', minLength: 1, title: 'Search query', description: 'Text sent to the WHO knowledge search boundary.' },
    },
    required: ['query_text'],
    additionalProperties: false,
  },
  uiSchema: { fields: [{ field: 'query_text', widget: 'text', label: 'Search WHO knowledge', order: 1 }] },
  requiredFields: ['query_text'],
  supportedExecutionMode: 'sync',
};

export function ensureWhoSearchContractRegistered(): PluginInputContract {
  pluginContractRegistry.registerIfAbsent(WHO_SEARCH_CONTRACT);
  return pluginContractRegistry.resolve('who_knowledge', '1.0.0');
}

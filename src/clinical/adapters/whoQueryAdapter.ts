import { whoApi } from '@/api/whoApi';
import { PluginContractError } from '@/plugins/contracts';
import type { PluginInputContract } from '@/plugins/contracts';
import type { DiseaseSummary } from '@/types';

export async function executeWhoSearchQuery(contract: PluginInputContract, values: Record<string, unknown>): Promise<DiseaseSummary[]> {
  if (contract.pluginId !== 'who_knowledge' || contract.contractId !== 'who-search-query') {
    throw new PluginContractError('PLUGIN_ADAPTER_ERROR', 'The WHO search adapter received an unsupported contract.');
  }
  const query = values.query_text;
  if (typeof query !== 'string' || query.trim().length === 0) {
    throw new PluginContractError('PLUGIN_ADAPTER_ERROR', 'WHO search requires an explicit query_text value.');
  }
  return whoApi.searchWhoDiseases(query);
}

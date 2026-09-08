import type { CanonicalPipelineRequest } from '@/api/types';
import type { PluginInputContract } from '@/plugins/contracts';
import { PluginContractError } from '@/plugins/contracts';

export interface PluginInputAdapter {
  readonly pluginId: string;
  toCanonicalRequest(input: {
    contract: PluginInputContract;
    values: Record<string, unknown>;
    request: Pick<CanonicalPipelineRequest, 'patient_id' | 'case_id' | 'plugin_selection' | 'routing_context'>;
  }): CanonicalPipelineRequest;
}

export function requirePluginAdapter(adapter: PluginInputAdapter | undefined): PluginInputAdapter {
  if (!adapter) throw new PluginContractError('PLUGIN_ADAPTER_ERROR', 'No approved adapter is available for this plugin.');
  return adapter;
}

export function createPayloadAdapter(pluginId: string): PluginInputAdapter {
  return {
    pluginId,
    toCanonicalRequest: ({ contract, values, request }) => {
      if (contract.pluginId !== pluginId) throw new PluginContractError('PLUGIN_ADAPTER_ERROR', 'Contract and adapter plugin identities do not match.');
      return {
        ...request,
        input_payload: { [pluginId]: values },
        execution_mode: 'sync',
        response_mode: 'full',
      };
    },
  };
}

import { PluginContractError, validateFormValues } from '@/plugins/contracts';
import type { CanonicalPipelineRequest } from '@/api/types';
import type { PluginInputContract } from '@/plugins/contracts';

export function toArmdCanonicalRequest(input: {
  contract: PluginInputContract;
  values: Record<string, unknown>;
  request: Pick<CanonicalPipelineRequest, 'patient_id' | 'case_id' | 'plugin_selection' | 'routing_context'>;
}): CanonicalPipelineRequest {
  if (input.contract.pluginId !== 'armd' || input.contract.contractId !== 'armd-direct-clinical-inputs') {
    throw new PluginContractError('PLUGIN_ADAPTER_ERROR', 'The ARMD adapter received an unsupported contract.');
  }
  const validation = validateFormValues(input.contract.inputSchema, input.values);
  if (!validation.valid) throw new PluginContractError('FORM_VALIDATION_ERROR', 'ARMD inputs failed contract validation.', validation.issues);

  return {
    ...input.request,
    input_payload: { armd: input.values },
    execution_mode: 'sync',
    response_mode: 'full',
  };
}

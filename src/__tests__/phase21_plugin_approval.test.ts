import { ensureArmdClinicalContractRegistered, pluginContractRegistry, PluginContractError, validatePluginContract } from '../plugins/contracts';
import { WHO_SEARCH_CONTRACT } from '../plugins/contracts/whoSearchContract';

export interface Phase21TestResult { name: string; passed: boolean; error?: string }

export function runPhase21PluginApprovalTests(): Phase21TestResult[] {
  const results: Phase21TestResult[] = [];
  const assert = (name: string, condition: boolean, error?: string) => results.push({ name, passed: condition, error: condition ? undefined : error || 'Assertion failed' });

  assert('Phase 21: SOAR has no approved frontend contract', !pluginContractRegistry.has('soar', '1.0.0'));
  assert('Phase 21: ARMD contract remains the narrowly admitted direct-input contract', ensureArmdClinicalContractRegistered().contractId === 'armd-direct-clinical-inputs');
  assert('Phase 21: WHO approval remains limited to the existing search contract', WHO_SEARCH_CONTRACT.contractId === 'who-search-query');
  assert('Phase 21: WHO contract provenance is valid', validatePluginContract(WHO_SEARCH_CONTRACT).length === 0);

  try { pluginContractRegistry.resolve('soar', '1.0.0'); assert('Phase 21: SOAR resolution fails closed', false); } catch (error) { assert('Phase 21: SOAR resolution fails closed', error instanceof PluginContractError && error.code === 'CONTRACT_NOT_FOUND'); }
  assert('Phase 21: ARMD exact resolution remains available', pluginContractRegistry.resolve('armd', '1.0.0').contractId === 'armd-direct-clinical-inputs');

  const soarRoutingOnly = { pluginId: 'soar', contractId: 'routing-only', contractVersion: '1.0.0', schemaVersion: '2020-12', displayName: 'Invalid SOAR routing contract', status: 'approved', provenance: { owner: 'x', source: 'x', artifact: 'x', artifactVersion: '1.0.0', approvedBy: 'x', approvedAt: '2026-09-06T00:00:00Z' }, inputSchema: { type: 'object', properties: { deployment_id: { type: 'string' } }, required: ['deployment_id'] }, supportedExecutionMode: 'sync' } as const;
  assert('Phase 21: routing metadata is not registered as a clinical contract', validatePluginContract(soarRoutingOnly).length === 0);
  assert('Phase 21: routing metadata remains excluded by approval record', !pluginContractRegistry.has('soar', '1.0.0'));
  return results;
}

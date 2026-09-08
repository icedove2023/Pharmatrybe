import { ensureArmdClinicalContractRegistered, ensureWhoSearchContractRegistered, pluginContractRegistry } from '../plugins/contracts';
import { validatePluginContract } from '../plugins/contracts';

export interface Phase20TestResult { name: string; passed: boolean; error?: string }

export function runPhase20ContractMigrationTests(): Phase20TestResult[] {
  const results: Phase20TestResult[] = [];
  const assert = (name: string, condition: boolean, error?: string) => results.push({ name, passed: condition, error: condition ? undefined : error || 'Assertion failed' });
  const contract = ensureWhoSearchContractRegistered();

  assert('Phase 20: WHO approved contract resolves at exact version', pluginContractRegistry.resolve('who_knowledge', '1.0.0') === contract);
  assert('Phase 20: WHO search contract has valid provenance and schema', validatePluginContract(contract).length === 0);
  assert('Phase 20: WHO search contract exposes only query_text', Object.keys(contract.inputSchema.properties || {}).length === 1 && Object.prototype.hasOwnProperty.call(contract.inputSchema.properties, 'query_text'));
  assert('Phase 20: WHO search contract does not expose entity_type', !Object.prototype.hasOwnProperty.call(contract.inputSchema.properties, 'entity_type'));
  assert('Phase 20: WHO contract is knowledge query, not prediction input', contract.contractId === 'who-search-query');
  assert('Phase 20: SOAR remains without approved frontend contract', !pluginContractRegistry.has('soar', '1.0.0'));
  assert('Phase 20: ARMD contract is registered only by the later Phase 22 admission path', ensureArmdClinicalContractRegistered().contractId === 'armd-direct-clinical-inputs');
  return results;
}

import { createPayloadAdapter } from '../clinical/adapters/pluginInputAdapter';
import {
  PluginContractError,
  PluginContractRegistry,
  PluginInputContract,
  validateFormValues,
  validatePluginContract,
} from '../plugins/contracts';

export interface Phase19TestResult { name: string; passed: boolean; error?: string }

const approvedContract: PluginInputContract = {
  pluginId: 'fixture_plugin',
  contractId: 'fixture-input',
  contractVersion: '1.0.0',
  schemaVersion: '2020-12',
  displayName: 'Approved fixture input',
  status: 'approved',
  provenance: { owner: 'fixture-owner', source: 'fixture-registry', artifact: 'fixture.json', artifactVersion: '1.0.0', approvedBy: 'fixture-approver', approvedAt: '2026-09-01T00:00:00Z' },
  inputSchema: {
    type: 'object',
    properties: {
      label: { type: 'string', minLength: 2 },
      count: { type: 'integer', minimum: 1, maximum: 3 },
      enabled: { type: 'boolean' },
      tags: { type: 'array', items: { type: 'string' } },
    },
    required: ['label', 'count'],
  },
  uiSchema: { fields: [{ field: 'label', widget: 'text' }, { field: 'count', widget: 'number' }] },
  supportedExecutionMode: 'sync',
};

export function runPhase19SchemaFormEngineTests(): Phase19TestResult[] {
  const results: Phase19TestResult[] = [];
  const assert = (name: string, condition: boolean, error?: string) => results.push({ name, passed: condition, error: condition ? undefined : error || 'Assertion failed' });

  assert('Phase 19: approved contract is structurally valid', validatePluginContract(approvedContract).length === 0);
  assert('Phase 19: missing approval is rejected', validatePluginContract({ ...approvedContract, status: 'draft' }).some((issue) => issue.includes('approved')));
  assert('Phase 19: undeclared UI field is rejected', validatePluginContract({ ...approvedContract, uiSchema: { fields: [{ field: 'unknown' }] } }).some((issue) => issue.includes('undeclared')));

  const registry = new PluginContractRegistry();
  registry.register(approvedContract);
  assert('Phase 19: registered contract resolves deterministically', registry.resolve('fixture_plugin', '1.0.0') === approvedContract);
  try { registry.resolve('fixture_plugin', '2.0.0'); assert('Phase 19: unsupported version fails closed', false); } catch (error) { assert('Phase 19: unsupported version fails closed', error instanceof PluginContractError && error.code === 'CONTRACT_NOT_FOUND'); }
  try { registry.register(approvedContract); assert('Phase 19: duplicate contract fails closed', false); } catch (error) { assert('Phase 19: duplicate contract fails closed', error instanceof PluginContractError); }

  const invalid = validateFormValues(approvedContract.inputSchema, { label: 'x', count: 4, enabled: 'yes', tags: [1] });
  assert('Phase 19: required/type/range constraints reject invalid values', !invalid.valid && invalid.issues.length >= 3);
  const valid = validateFormValues(approvedContract.inputSchema, { label: 'ok', count: 2, enabled: true, tags: ['safe'] });
  assert('Phase 19: valid values pass validation', valid.valid);

  const request = createPayloadAdapter('fixture_plugin').toCanonicalRequest({
    contract: approvedContract,
    values: { label: 'ok', count: 2 },
    request: { patient_id: 'patient-fixture', case_id: 'case-fixture', routing_context: { deployment_id: 'explicit-route' }, plugin_selection: [{ plugin_id: 'fixture_plugin' }] },
  });
  assert('Phase 19: adapter preserves explicit routing context', request.routing_context?.deployment_id === 'explicit-route');
  assert('Phase 19: adapter keeps plugin values inside plugin payload boundary', (request.input_payload.fixture_plugin as Record<string, unknown>).label === 'ok');

  const productionRegistry = new PluginContractRegistry();
  for (const pluginId of ['soar', 'armd', 'who_knowledge']) {
    try { productionRegistry.resolve(pluginId, '1.0.0'); assert(`Phase 19: ${pluginId} missing frontend contract fails closed`, false); } catch (error) { assert(`Phase 19: ${pluginId} missing frontend contract fails closed`, error instanceof PluginContractError && error.code === 'CONTRACT_NOT_FOUND'); }
  }
  return results;
}

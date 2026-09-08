import { ensureArmdClinicalContractRegistered, PluginContractError, pluginContractRegistry, validateFormValues, validatePluginContract } from '../plugins/contracts';
import { toArmdCanonicalRequest } from '../clinical/adapters/armdClinicalAdapter';

export interface Phase22TestResult { name: string; passed: boolean; error?: string }

export function runPhase22AdmissionTests(): Phase22TestResult[] {
  const results: Phase22TestResult[] = [];
  const assert = (name: string, condition: boolean, error?: string) => results.push({ name, passed: condition, error: condition ? undefined : error || 'Assertion failed' });
  const contract = ensureArmdClinicalContractRegistered();
  const fields = Object.keys(contract.inputSchema.properties || {});
  const expected = ['age', 'temperature', 'creatinine', 'bun', 'wbc', 'neutrophils', 'lymphocytes', 'lactate', 'procalcitonin'];

  assert('Phase 22: ARMD admitted field set is exact and limited', fields.length === expected.length && expected.every((field) => fields.includes(field)));
  assert('Phase 22: ARMD admitted contract is approved and valid', contract.status === 'approved' && validatePluginContract(contract).length === 0);
  assert('Phase 22: ARMD derived and model fields are excluded', !fields.includes('age_group') && !fields.includes('log_days_since_abx') && !fields.includes('adi_score'));
  assert('Phase 22: ARMD legacy weight and eGFR fields are excluded', !fields.includes('weight') && !fields.includes('egfr'));

  const validValues = { age: 67, temperature: 38.2, creatinine: 1.1, bun: 15, wbc: 11, neutrophils: 7, lymphocytes: 2, lactate: 1.4, procalcitonin: 0.3 };
  assert('Phase 22: admitted ARMD values pass validation', validateFormValues(contract.inputSchema, validValues).valid);
  assert('Phase 22: invalid admitted ARMD values fail validation', !validateFormValues(contract.inputSchema, { age: 121, creatinine: -1 }).valid);

  const request = toArmdCanonicalRequest({ contract, values: validValues, request: { patient_id: 'patient-fixture', case_id: 'case-fixture', plugin_selection: [{ plugin_id: 'armd' }], routing_context: { deployment_id: 'must-remain-separate' } } });
  assert('Phase 22: ARMD adapter preserves raw values', (request.input_payload.armd as Record<string, unknown>).creatinine === 1.1);
  assert('Phase 22: ARMD adapter preserves routing separately', request.routing_context?.deployment_id === 'must-remain-separate' && !(request.input_payload.armd as Record<string, unknown>).deployment_id);
  assert('Phase 22: no SOAR contract is registered', !pluginContractRegistry.has('soar', '1.0.0'));
  try { pluginContractRegistry.resolve('soar', '1.0.0'); assert('Phase 22: SOAR remains fail-closed', false); } catch (error) { assert('Phase 22: SOAR remains fail-closed', error instanceof PluginContractError && error.code === 'CONTRACT_NOT_FOUND'); }
  return results;
}

import {
  SOAR_DEPLOYMENT_CONTRACTS,
  buildSoarExecutionPayload,
  resolveSoarDeploymentContract,
  resolveSoarInputs,
} from '../plugins/contracts';

export interface Phase23TestResult { name: string; passed: boolean; error?: string }

export function runPhase23InputResolutionTests(): Phase23TestResult[] {
  const results: Phase23TestResult[] = [];
  const assert = (name: string, condition: boolean, error?: string) => results.push({ name, passed: condition, error: condition ? undefined : error || 'Assertion failed' });
  const ceftriaxone = resolveSoarDeploymentContract('Ceftriaxone_Haemophilus_influenzae');
  const doxycycline = resolveSoarDeploymentContract('Doxycycline_Streptococcus_pneumoniae');

  assert('Phase 23: exactly ten verified deployment contracts exist', SOAR_DEPLOYMENT_CONTRACTS.length === 10);
  assert('Phase 23: H. influenzae contract includes beta-lactamase input', ceftriaxone.requiredInputs.some((field) => field.key === 'Beta_Lactamase_enc'));
  assert('Phase 23: S. pneumoniae contract excludes beta-lactamase input', !doxycycline.requiredInputs.some((field) => field.key === 'Beta_Lactamase_enc'));
  assert('Phase 23: verified categorical values are constrained', ceftriaxone.requiredInputs.find((field) => field.key === 'Region')?.schema.enum?.join('|') === 'Asia|Europe|Middle East');

  const partial = resolveSoarInputs({
    deploymentId: ceftriaxone.deploymentId,
    canonicalClinicalData: { Age: 47 },
  });
  assert('Phase 23: partial input returns structured missing fields', !partial.isComplete && partial.missingRequiredInputs.some((field) => field.field === 'YearCollected'));
  assert('Phase 23: canonical value preserves provenance', partial.provenance.Age?.source === 'CANONICAL_CLINICAL_ASSESSMENT');
  assert('Phase 23: missing beta status is not silently defaulted', partial.missingRequiredInputs.some((field) => field.field === 'Beta_Lactamase_enc' && field.reason === 'REQUIRED_INPUT_MISSING'));

  const complete = resolveSoarInputs({
    deploymentId: doxycycline.deploymentId,
    clinicianEntered: { Age: 47, YearCollected: 2019, Region: 'Europe', BodyLocation_Group: 'Blood', Country: 'Italy' },
  });
  assert('Phase 23: complete clinician input resolves', complete.isComplete && Object.keys(complete.resolvedInputs).length === 5);
  assert('Phase 23: clinician value preserves provenance', complete.provenance.Region?.source === 'CLINICIAN_ENTERED');
  const payload = buildSoarExecutionPayload(complete, doxycycline);
  assert('Phase 23: routing context remains separate from input payload', payload.routing_context.deployment_id === doxycycline.deploymentId && !('deployment_id' in payload.input_payload));

  try { resolveSoarDeploymentContract('unknown'); assert('Phase 23: unknown deployment fails closed', false); } catch { assert('Phase 23: unknown deployment fails closed', true); }
  return results;
}
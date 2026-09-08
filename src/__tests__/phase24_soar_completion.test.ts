import {
  SOAR_DEPLOYMENT_CONTRACTS,
  buildSoarExecutionPayload,
  resolveSoarDeploymentContract,
  resolveSoarInputs,
  toSoarPluginContract,
} from '../plugins/contracts';

export interface Phase24TestResult { name: string; passed: boolean; error?: string }

export function runPhase24SoarCompletionTests(): Phase24TestResult[] {
  const results: Phase24TestResult[] = [];
  const assert = (name: string, condition: boolean, error?: string) => results.push({ name, passed: condition, error: condition ? undefined : error || 'Assertion failed' });
  const strep = resolveSoarDeploymentContract('Doxycycline_Streptococcus_pneumoniae');
  const validValues = { Age: 47, YearCollected: 2019, Region: 'Europe', BodyLocation_Group: 'Blood', Country: 'Italy' };

  assert('Phase 24: all ten exact contracts remain registered', SOAR_DEPLOYMENT_CONTRACTS.length === 10);
  assert('Phase 24: unknown deployment fails closed', (() => { try { resolveSoarDeploymentContract('unknown'); return false; } catch { return true; } })());

  const partial = resolveSoarInputs({ deploymentId: strep.deploymentId, canonicalClinicalData: { Age: 47 } });
  assert('Phase 24: missing required values are structured', partial.missingRequiredInputs.some((item) => item.field === 'YearCollected'));

  const complete = resolveSoarInputs({ deploymentId: strep.deploymentId, clinicianEntered: validValues });
  const payload = buildSoarExecutionPayload(complete, strep);
  assert('Phase 24: Streptococcus completion creates an exact payload', complete.isComplete && payload.routing_context.deployment_id === strep.deploymentId);
  assert('Phase 24: routing identity stays outside clinical payload', !('deployment_id' in payload.input_payload));

  const invalidRegion = resolveSoarInputs({ deploymentId: strep.deploymentId, clinicianEntered: { ...validValues, Region: 'Unknown region' } });
  assert('Phase 24: invalid categorical input cannot execute', (() => { try { buildSoarExecutionPayload(invalidRegion, strep); return false; } catch { return true; } })());

  const haemophilus = resolveSoarDeploymentContract('Ceftriaxone_Haemophilus_influenzae');
  const publicContract = toSoarPluginContract(haemophilus);
  assert('Phase 25: public SOAR contract exposes beta-lactamase status only', Boolean(publicContract.inputSchema.properties?.BetaLactamaseStatus) && !Boolean(publicContract.inputSchema.properties?.Beta_Lactamase_enc));
  assert('Phase 25: public beta-lactamase field uses controlled enum', publicContract.inputSchema.properties?.BetaLactamaseStatus?.enum?.join('|') === 'POSITIVE|NEGATIVE');
  const positive = resolveSoarInputs({ deploymentId: haemophilus.deploymentId, clinicianEntered: { ...validValues, BetaLactamaseStatus: 'POSITIVE' } });
  const negative = resolveSoarInputs({ deploymentId: haemophilus.deploymentId, clinicianEntered: { ...validValues, BetaLactamaseStatus: 'NEGATIVE' } });
  assert('Phase 24.5: positive beta status maps to one', positive.resolvedInputs.Beta_Lactamase_enc === 1);
  assert('Phase 24.5: negative beta status maps to zero', negative.resolvedInputs.Beta_Lactamase_enc === 0);
  assert('Phase 24.5: verified H. influenzae payload can execute', positive.isComplete && Boolean(buildSoarExecutionPayload(positive, haemophilus)));
  const attemptedBeta = resolveSoarInputs({ deploymentId: haemophilus.deploymentId, clinicianEntered: { ...validValues, Beta_Lactamase_enc: 0 } });
  assert('Phase 24.5: raw numeric beta input cannot bypass mapping', attemptedBeta.missingRequiredInputs.some((item) => item.field === 'Beta_Lactamase_enc' && item.reason === 'UNSUPPORTED_MAPPING'));

  return results;
}
